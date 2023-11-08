#%% import
import pdb
import pandas as pd
from typing import Union, List
from datetime import date
import time 
import os
from pathlib import Path
import requests
from requests.exceptions import Timeout
from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor


from wtbonline._common.utils import make_sure_list, make_sure_series
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.time import resample
from wtbonline._logging import get_logger, log_it
from wtbonline._db.config import get_td_local_connector, get_td_remote_restapi

#%% constant
_LOGGER = get_logger('preprocess')
OUTPATH = Path('/var/local/wtbonline/ibox')
FILE_REGX = '^ibox.*\.txt$'
REMOTE_DIR = '/ram0'
TIME_OUT = 10

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
    def __init__(self, set_id:str, turbine_id:str , username:str='', password:str=''):
        self.set_id = set_id
        self.turbine_id = turbine_id
        self.host = ''
        self.ftp = None
        self.username = username
        self.password = password
    
    def _initialize(self):
        host = RSDBInterface.read_windfarm_configuration(
            set_id=self.set_id, 
            turbine_id=self.turbine_id, 
            columns='ip_address')
        if len(host)<1:
            raise ValueError(f'{self.set_id} {self.turbine_id} 没有设置ip地址')
        self.host = host['ip_address'].iloc[0]
    
    def _quit(self):
        if self.ftp is not None:
            try:
                self.ftp.quit()
            except:
                pass
        self.ftp = None
    
    def _login(self):
        self.ftp = FTP(self.host, timeout=TIME_OUT)
        self.ftp.login(self.username, self.password)
        
    def __enter__(self):
        self._quit()
        self._initialize()
        self._login()
        return self
    
    def __exit__(self):
        self._quit()
        
    def list_remote_files(self)->List[str]:
        self.ftp.cwd(REMOTE_DIR)
        file_list = self.ftp.nlst()
        return file_list

    def download_files(self, file_names:Union[str, List[str]], local_root):
        file_names = make_sure_list(file_names)
        local_root = Path(local_root)/self.set_id/self.turbine_id
        for name in file_names:
            try:
                y,m,d = get_date(name)
                path = local_root/y/m/d
                tempfile = path/(name+'.tmp')
                with open(tempfile, 'wb') as local_file:
                    self.ftp.retrbinary('RETR ' + REMOTE_DIR/name, local_file.write)
                Path(tempfile).rename(path/name)
            except Exception as e:
                _LOGGER.error(f'从{self.host}下载文件{name}失败: {e}')
                Path(tempfile).unlink()
        
def list_candidates(remote_files, local_files):
    remote_files = make_sure_series(remote_files)
    local_files = make_sure_list(local_files)
    return remote_files[~remote_files.isin(local_files)]

def _update_ibox_files(args):
    set_id, turbine_id = args
    try:
        with _FTP(set_id, turbine_id) as ftp:
            remote_files = ftp.list_remote_files()
            local_files = list_local_file(set_id, turbine_id)
            candidates = list_candidates(remote_files, local_files)
            ftp.download_files(candidates)
    except Exception as e:
        _LOGGER.error(f'{set_id} {turbine_id}更新ibox文件出错: {e}')
    
@log_it(_LOGGER, True)
def update_ibox_files():
    confs = RSDBInterface.read_windfarm_configuration(columns=['set_id', 'turbine_id'])
    confs = [(i,j) for _,(i,j) in confs.iterrows()]
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(_update_ibox_files, confs))
    if None in results:
        raise ValueError('更新ibox文件失败')
 

#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()