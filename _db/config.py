# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:02:37 2023

@author: luosz

数据库引擎配置

若项目名变更，需要修改_db里面的根路径名，如：
from wtbonline._db.config import RSDB_URI
改为
from packgename._db.config import RSDB_URI
"""

# =============================================================================
# import
# =============================================================================
from urllib.parse import quote_plus
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from cryptography.fernet import Fernet 

# =============================================================================
# constant
# =============================================================================
_key = b'c63v5A2xjKjBXgVNJmXEWIjqMQmxMNaxoKvU5M5Hyfc='

def get_rsdb_uri():
    return f'mysql+pymysql://root:{quote_plus("Root666@mysql")}@mysql:3306/online'

RSDB_URI = get_rsdb_uri() 

def get_td_local_connector():
    '''
    >>> get_td_local_connector().keys()
    dict_keys(['host', 'port', 'user', 'password', 'database'])
    '''
    fn = Fernet(_key)
    sr = pd.read_sql(
        '''
        select host, port, user, password, `database` 
        from app_server
        where name='tdengine' and remote=0 and type='native'
        ''', 
        create_engine(RSDB_URI)
        ).squeeze()
    password = fn.decrypt(bytes(sr['password'], encoding='utf'))
    sr['password'] = str(password, encoding='utf')
    return sr.to_dict()

TD_LOCAL_CONNECTOR = get_td_local_connector()

def get_td_remote_restapi():
    '''
    >>> get_td_remote_restapi().keys()
    dict_keys(['host', 'port', 'user', 'password', 'database'])
    '''
    fn = Fernet(_key)
    sr = pd.read_sql(
        '''
        select host, port, user, password, `database` 
        from app_server
        where name='tdengine' and remote=1 and type='restapi'
        ''', 
        create_engine(RSDB_URI)
        ).squeeze()
    password = fn.decrypt(bytes(sr['password'], encoding='utf'))
    sr['password'] = str(password, encoding='utf')
    return sr.to_dict()

TD_REMOTE_RESTAPI = get_td_remote_restapi()

def get_temp_dir():
    '''
    >>> isinstance(TEMP_DIR, Path)
    True
    '''
    path = pd.read_sql(
        '''
        select value 
        from app_configuration
        where `key`='tempdir'
        ''', 
        create_engine(RSDB_URI)
        ).squeeze()
    path = Path(path)
    path.mkdir(exist_ok=True)
    return path
TEMP_DIR = get_temp_dir()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
