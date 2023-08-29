# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:02:37 2023

@author: luosz

数据库引擎配置
"""
# =============================================================================
# import
# =============================================================================
from urllib.parse import quote_plus
from platform import platform

# =============================================================================
# constant
# =============================================================================
LOCAL_DRIVER = {'host':'taos', 'port':6030, 
                'user':'root', 'password':'taosdata', 
                'database':'windfarm'}
LOCAL_ADAPTER = LOCAL_DRIVER.copy()
LOCAL_ADAPTER['port'] = 6041

SOURCE_DRIVER = {'host':'source', 'port':6030, 
                 'user':'root', 'password':'taosdata',
                 'database':'scada'}
SOURCE_ADAPTER = SOURCE_DRIVER.copy()
SOURCE_ADAPTER['port'] = 6041

URI = f'mysql+pymysql://root:{quote_plus("Root85@mysql")}@mysql:3306/online'
URI_WITHOUT_DB = f'mysql+pymysql://root:{quote_plus("Root85@mysql")}@mysql:3306'

if platform().startswith('Windows'):
    TEMP_DIR = 'd:/'
else:
    TEMP_DIR = '/tmp'