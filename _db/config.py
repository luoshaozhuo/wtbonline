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
_host = 'mysql'
_port = 3306
_dbname = 'online'
_user = 'root'
_passwordd = quote_plus("Root666@mysql")

SESSION_TIMEOUT = 3000

def get_rsdb_uri():
    return f'mysql+pymysql://{_user}:{_passwordd}@{_host}:{_port}/{_dbname}'

RSDB_URI = get_rsdb_uri() 

def get_postgres_uri():
    '''
    >>> _ = get_postgres_uri()
    '''
    fn = Fernet(_key)
    sr = pd.read_sql(
        '''
        select host, port, user, password, `database` 
        from app_server
        where name='postgres' and remote=1
        ''', 
        create_engine(RSDB_URI)
        ).squeeze()
    password = fn.decrypt(bytes(sr['password'], encoding='utf'))
    sr['password'] = quote_plus(str(password, encoding='utf'))
    return f'postgresql://{sr["user"]}:{sr["password"]}@{sr["host"]}:{sr["port"]}/{sr["database"]}'

POSTGRES_URI = get_postgres_uri()


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

def get_temp_dir():
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
