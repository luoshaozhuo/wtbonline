#%% import
import pandas as pd
from typing import Union, List
from pathlib import Path
from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from wtbonline._common.utils import make_sure_list, make_sure_series
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._logging import get_logger
from wtbonline._process.preprocess import _LOGGER
from wtbonline._logging import log_it

#%% constant
RSDBFC = RSDBFacade()
PGFC = PGFacade()

OUTPATH = Path(RSDBFC.read_app_configuration(key_='ibox_outpath').squeeze()['value'])
EXT = RSDBFC.read_app_configuration(key_='ibox_extension').squeeze()['value']
PREFIX = RSDBFC.read_app_configuration(key_='ibox_prefix').squeeze()['value']
FILE_REGX = f'{PREFIX}*.{EXT}'
REMOTE_DIR = Path(RSDBFC.read_app_configuration(key_='ibox_srcpath').squeeze()['value'])

PORT = int(RSDBFC.read_app_configuration(key_='ibox_port').squeeze()['value'])
USER = RSDBFC.read_app_configuration(key_='ibox_user').squeeze()['value']
PASSWD = RSDBFC.read_app_configuration(key_='ibox_passwd').squeeze()['value']
TIME_OUT = 1

#%% function
def get_date(file_name:str):
    '''
    文件名类似'ibox20240828081046.zip'
    >>> get_date('ibox20240828081046.zip')
    ('2024', '08', '28')
    '''
    name = file_name.strip()
    name = name.replace(PREFIX, '')
    name = name.replace(f'.{EXT}', '')
    if len(name)<8:
        raise ValueError(f'ibox文件名没有包含日期时间信息：{file_name}')
    return name[0:4], name[4:6], name[6:8]


def list_local_file(set_id:str, turbine_id:str)->List[str]:
    now = pd.Timestamp.now()
    year = now.year
    month = now.month
    day = now.day
    p = OUTPATH/set_id/turbine_id/f'{year}/{month:02d}/{day:02d}'
    return [f for f in p.rglob(FILE_REGX)]

class _FTP():
    def __init__(self, set_id:str, turbine_id:str, host=None, username=USER, password=PASSWD, port=PORT):
        self.set_id = set_id
        self.turbine_id = turbine_id
        self.port = port
        self.ftp = None
        self.username = USER
        self.password = PASSWD
        self.host = host
        if host is None:
            self.host = PGFC.read_model_device(device_id=self.turbine_id).squeeze()['server_ip1']
    
    def _quit(self):
        if self.ftp is not None:
            try:
                self.ftp.quit()
            except:
                pass
        self.ftp = None
    
    def _login(self):
        self.ftp = FTP()
        self.ftp.connect(self.host, int(self.port), TIME_OUT)
        self.ftp.login(self.username, self.password)
        self.ftp.set_pasv(True)

    def __enter__(self):
        self._quit()
        self._login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._quit()
        
    def list_remote_files(self)->List[str]:
        self.ftp.cwd(str(REMOTE_DIR))
        file_sr = pd.Series(self.ftp.nlst())
        is_ibox_file = file_sr.str.match(FILE_REGX)   
        return file_sr[is_ibox_file]

    def download_files(self, file_names:Union[str, List[str]], local_root):
        file_names = make_sure_list(file_names)
        local_root = Path(local_root)/self.set_id/self.turbine_id
        for name in file_names:
            try:
                y,m,d = get_date(name)
                path = local_root/y/m/d
                path.mkdir(parents=True, exist_ok=True)
                tempfile = path/(name+'.tmp')
                with open(tempfile, 'wb') as local_file:
                    self.ftp.retrbinary('RETR ' + str(REMOTE_DIR/name), local_file.write)
                Path(tempfile).rename(path/name)
            except Exception as e:
                _LOGGER.error(f'从{self.host}下载文件{name}失败: {e}')
                Path(tempfile).unlink()
        
def list_candidates(remote_files, local_files):
    remote_files = make_sure_series(remote_files)
    local_files = make_sure_list(local_files)
    return remote_files[~remote_files.isin(local_files)]

def _update_ibox_files(args):
    '''
    >>> set_id = '20835'
    >>> turbine_id = 's10001'
    >>> _update_ibox_files((set_id, turbine_id))
    '''
    rev = 0
    set_id, turbine_id = args
    with _FTP(set_id, turbine_id) as ftp:
        remote_files = ftp.list_remote_files()
        local_files = list_local_file(set_id, turbine_id)
        candidates = list_candidates(remote_files, local_files)
        ftp.download_files(candidates, OUTPATH)
    return rev

@log_it(_LOGGER)
def update_ibox_files(*args, **kwargs):
    task_id = kwargs.get('task_id', 'NA')
    df = PGFacade().read_model_device()[['set_id', 'device_id']].sort_values('device_id')
    failed = False
    for _, (set_id, device_id) in df.iterrows():
        _LOGGER.info(f'task_id={task_id} update_ibox_files: {set_id}, {device_id}')
        try:
            _update_ibox_files([set_id, device_id])
        except Exception as e:
            _LOGGER.error(f'task_id={task_id} update_ibox_files: {set_id}, {device_id}, errmsg:{str(e)}')
            failed = True
    if failed:
        raise ValueError('task_id={task_id} update_ibox_files 任务失败')
 
#%% main
if __name__ == "__main__":
    update_ibox_files()
    # set_id = '20835'
    # turbine_id = 's10025'
    # _update_ibox_files((set_id, turbine_id))