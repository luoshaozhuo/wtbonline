#%% import
import pandas as pd
from typing import Union, List
from pathlib import Path
from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from wtbonline._common.utils import make_sure_list, make_sure_series
from _db.rsdb_facade import RSDBFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._logging import get_logger
from wtbonline._process.preprocess import _LOGGER

#%% constant
# _LOGGER = get_logger('preprocess')
OUTPATH = Path('/var/local/wtbonline/ibox')
FILE_REGX = '^ibox.*\.txt$'
REMOTE_DIR = Path('/ram0')
TIME_OUT = 2

#%% function
def get_date(file_name:str):
    '''
    文件名类似'ibox19320303121212.txt'
    >>> get_date('ibox19320303121212.txt')
    ('1932', '03', '03')
    '''
    name = pd.Series(file_name)
    name = name.str.strip()
    name = name.str.replace('[a-zA-Z]', '', regex=True).iloc[0]
    return name[0:4], name[4:6], name[6:8]


def list_local_file(set_id:str, turbine_id:str)->List[str]:
    p = OUTPATH/set_id/turbine_id
    return [f for f in p.rglob(FILE_REGX)]


class _FTP():
    def __init__(self, set_id:str, turbine_id:str):
        self.set_id = set_id
        self.turbine_id = turbine_id
        self.host = ''
        self.port = None
        self.ftp = None
        self.username = ''
        self.password = ''
    
    def _initialize(self):
        host = RSDBFacade.read_windfarm_configuration(
            set_id=self.set_id, 
            turbine_id=self.turbine_id, 
            columns=['ip_address', 'ftp_port', 'ftp_username', 'ftp_password']
            )
        if len(host)<1:
            raise ValueError(f'{self.set_id} {self.turbine_id} 没有设置ip地址')
        self.host, self.port, self.username, self.password = host.iloc[0,:].tolist()
    
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
        self._initialize()
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
    try:
        with _FTP(set_id, turbine_id) as ftp:
            remote_files = ftp.list_remote_files()
            local_files = list_local_file(set_id, turbine_id)
            candidates = list_candidates(remote_files, local_files)
            ftp.download_files(candidates, OUTPATH)
    except Exception as e:
        _LOGGER.error(f'{set_id} {turbine_id}更新ibox文件出错: {e}')
        rev = 1
    return rev
    
def update_ibox_files(*args, **kwargs):
    executor = kwargs.get('executor', 'thread')
    max_worker = kwargs.get('max_worker', 1)
    import time
    confs = RSDBFacade.read_windfarm_configuration(columns=['set_id', 'turbine_id'])
    confs = [(i,j) for _,(i,j) in confs.iterrows()]
    start = time.time()
    pool_executor = ThreadPoolExecutor if executor=='thread' else ProcessPoolExecutor
    with pool_executor(max_workers=max_worker) as exec:
        results = list(exec.map(_update_ibox_files, confs))
    print(time.time()-start)
    if 1 in results:
        raise ValueError('更新ibox文件失败')
 

#%% main
if __name__ == "__main__":
    # update_ibox_files()
    set_id = '20835'
    turbine_id = 's10025'
    _update_ibox_files((set_id, turbine_id))