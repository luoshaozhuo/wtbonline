# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:21:08 2023

@author: luosz

数据库操作类
"""
#%%
# =============================================================================
# import
# =============================================================================
import pandas as pd
import base64
import requests
import taos

# =============================================================================
# class
# =============================================================================
class TDEngine_Base():
    def __init__(self, **kwargs):
        self._host = kwargs.get('host')
        self._port = kwargs.get('port')
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self._database = kwargs.get('database', None)
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
    @property
    def user(self):
        return self._user
    
    @property
    def password(self):
        return self._password
    
    @property
    def database(self):
        return self._database

class TDEngine_RestAPI(TDEngine_Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        url = f"http://{self.host}:{self.port}/rest/sql/{self.database}"
        if self.database==None:
            url += '/?tz=Asia/Shanghai'
        else:
            url += f'/{self.database}?tz=Asia/Shanghai'
        self._url  = url
        token = base64.b64encode(f"{self.user}:{self.password}".encode('utf-8'))
        token = str(token,'utf-8')
        self._headers = {'Authorization':f'Basic {token}'}

    def query(self, sql):
        ''' 调用restApi，默认访问源数据库 
        >>> from wtbonline._db.config import get_td_remote_restapi
        >>> taos = TDEngine_RestAPI(**get_td_remote_restapi())
        >>> rs = taos.query('show databases')
        >>> len(rs)>0
        True
        '''
        sql = pd.Series(sql).str.replace('\n', '').str.replace(' {2,}', ' ', regex=True)
        sql = sql.str.strip().squeeze()
        rec = requests.post(self._url, data=sql, headers=self._headers, timeout=600)
        if rec.status_code == 200:
            json = rec.json()
            if 'head' in json.keys():
                rev = pd.DataFrame(json['data'], columns=json['head'])
            elif 'column_meta' in json.keys():
                temp = pd.DataFrame(json['column_meta'],
                                    columns=['name', 'type', 'size'])
                rev = pd.DataFrame(json['data'], columns=temp['name'])
            else:
                rev = pd.Series(json)
        else:
            raise ValueError((str(rec.content, encoding='utf8'), sql))
        return rev    

class TDEngine_Connector(TDEngine_Base):
    def _connect(self):
        return taos.connect(host=self.host,
                            user=self.user,
                            password=self.password,
                            port=self.port,
                            database=self.database)

    def query(self, sql):
        ''' 从tdengine读取原始数据 
        >>> from wtbonline._db.config import get_td_local_connector
        >>> connector = get_td_local_connector().copy()
        >>> connector['database']=None
        >>> tdec = TDEngine_Connector(**connector)
        >>> rs = tdec.query('show databases')  
        >>> len(rs)>0
        True
        '''
        conn = self._connect()
        sql = pd.Series(sql).str.replace('\n', '').str.replace(' {2,}', ' ', regex=True)
        sql = sql.str.strip().squeeze()
        try:
            rs = conn.query(sql)
        except Exception as e:
            raise ValueError((str(e), sql))
        finally:
            conn.close()
        if rs.check_error()==None:
            ret = pd.DataFrame(rs.fetch_all(),
                               columns=[i.name for i in rs.fields])
        else:
            raise ValueError((rs.errstr(), sql))
        return ret

# %%
if __name__ == "__main__":
    import doctest
    doctest.testmod()

