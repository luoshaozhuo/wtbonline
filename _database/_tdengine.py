# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:21:08 2023

@author: luosz

数据库操作函数
"""
# =============================================================================
# import
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

import os
import pandas as pd
import numpy as np
from collections.abc import Iterable
import base64
import requests
from pathlib import Path
import taos
import tempfile
import uuid


from _database import config as cfg
from _database import _mysql as msql

# =============================================================================
# constant
# =============================================================================
DATA_TYPE = {
    'F':'float32',
    'I':'category',
    'B':'bool'
    }

# =============================================================================
# class
# =============================================================================
class TAOS_Connector:
    def __init__(self, kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.database = kwargs.get('database')

    def connect(self):
        self.conn = taos.connect(host=self.host,
                                 user=self.user,
                                 password=self.password,
                                 port=self.port,
                                 database=self.database)

    def query(self, sql):
        ''' 从tdengine读取原始数据 '''
        rs = self.conn.query(sql)
        if rs.check_error()==None:
            ret = pd.DataFrame(rs.fetch_all(),
                               columns=[i.name for i in rs.fields])
        else:
            raise ValueError((sql, rs.errstr()))
        return ret

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *para):
        self.conn.close()

    def __del__(self):
        self.conn.close()

# =============================================================================
# funcion
# =============================================================================
def _to_list(x):
    if x is None:
        x = []
    elif isinstance(x, str) or (not isinstance(x, Iterable)):
        x = [x]
    else:
        x = list(x)
    return x

def _conver_dtype(df, set_id, point_df=None):
    if point_df==None:
        point_df = msql.read_model_point(set_id=set_id, select=1)
    else:
        point_df = point_df.copy()
    point_df['datatype'].replace(DATA_TYPE, inplace=True)
    point_df['var_name'] = point_df['var_name'].str.lower()
    point_df = point_df[point_df['var_name'].isin(df.columns)]
    df = df.astype({row['var_name']:row['datatype'] for _,row in point_df.iterrows()})
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts']).dt.tz_convert(tz='Asia/Shanghai')
    return df

def _change_column_name(df, set_id, col, point_df=None):
    point_df = point_df.copy()
    if point_df==None:
        point_df = msql.read_model_point(set_id=set_id, select=1)
    point_df['vn_lower'] = point_df['var_name'].str.lower()
    df.rename(columns=point_df.set_index('vn_lower')[col].to_dict(), inplace=True)


def split_csv(set_id, pathname, n=1500000):
    ''' 将select >>> file 导出的csv文件分拆成150万条一个的小文件
    要求文件名为f's{turbine_id}.csv', 子表名称f'd_s{turbin_id}', 超级表名称为
    f's_{set_id}'
    '''
    conf_df = msql.read_model_point(set_id=set_id, select=1)
    conf_df['var_name'] = conf_df['var_name'].str.lower()
    conf_df['datatype'] = conf_df['datatype'].replace({'F':float, 'B':int, 'I':int})

    pathname = Path(pathname)
    turbine_id = pathname.name.split('.')[0]
    path = pathname.parent
    names = pd._libs.lib.no_default
    for i in range(0,100):
        df = pd.read_csv(pathname,
                         nrows=n,
                         skiprows=n*i,
                         names=names)
        df.dropna(how='any', inplace=True)
        if i == 0:
            names = df.columns
        if df.shape[0]<1:
            break
        for _,row in conf_df.iterrows():
            df[row['var_name']] = df[row['var_name']].astype(row['datatype'])
        df.to_csv(path/f'{turbine_id}_{i}.csv', index=False)
        print(i, df.ts.min(), df.ts.max())

# =============================================================================
# db handler
# =============================================================================
def read_scada(set_id, turbine_id, start_time, end_time=None, point_name=None,
               var_name=None, offset='10min', limit=None, kwargs=cfg.LOCAL_DRIVER):
    # 字段名
    if not (point_name is None and var_name is None):
        point_name = _to_list(point_name)
        var_name = _to_list(var_name)
        colname = 'var_name' if len(var_name)>0 else 'point_name'
        col_sel = var_name if len(var_name)>0 else point_name
        if len(col_sel)<1:
            return pd.DataFrame(), pd.Series()
        _point_df = msql.read_model_point(set_id=set_id,
                                     **{colname:col_sel},
                                      select=1)
        # 按指定字段名排序
        _point_df.set_index(colname, drop=False, inplace=True)
        _point_df = _point_df.loc[col_sel,:]
    else:
        colname = 'var_name'
        _point_df = msql.read_model_point(set_id=set_id, select=1)
        _point_df.set_index(colname, drop=False, inplace=True)
        if limit is None:
            limit = 1
    # 时间范围
    start_time = start_time if start_time is None else pd.to_datetime(start_time)
    end_time = end_time if end_time is None else pd.to_datetime(end_time)
    if end_time is None:
        end_time = pd.to_datetime(start_time) + pd.Timedelta(offset)
    elif end_time==start_time:
        end_time = pd.to_datetime(start_time) + pd.Timedelta('1d')
    # 构造查询语句
    cols = ['ts', 'device'] + _point_df['var_name'].tolist()
    sql = f'''
        select {','.join(cols)} from s_{set_id}
        where ts>="{start_time}" and ts<"{end_time}"
    '''
    if isinstance(turbine_id, (list, tuple, pd.Series, np.ndarray)):
        turbine_id = pd.Series(turbine_id).astype(str)
        sql += f''' and device in ("{'","'.join(turbine_id)}")'''
    else:
        sql += f''' and device="{turbine_id}"'''
    sql = (sql+f' limit {limit}') if limit is not None else sql
    with TAOS_Connector(kwargs) as conn:
        df = conn.query(sql)
    df = _conver_dtype(df, set_id, _point_df)
    _change_column_name(df, set_id, colname, point_df=None)

    _point_df = _point_df[['point_name','unit']]
    _point_df['column'] = msql.get_column_name(_point_df)
    return df, _point_df

def execute(sql, kwargs):
    with TAOS_Connector(kwargs) as conn:
        rev = conn.query(sql)
    return rev

def call_rest_api(sql, set_id, kwargs):
    ''' 调用restApi，默认访问源数据库 '''
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', 6041)
    user = kwargs.get('user', 'root')
    password = kwargs.get('password', 'taosdata')
    database = kwargs.get('database')
    token = base64.b64encode(f"{user}:{password}".encode('utf-8'))
    token = str(token,'utf-8')
    headers = {'Authorization':f'Basic {token}'}
    url = f"http://{host}:{port}/rest/sql"
    url = url if database==None else url+f'/{database}'
    try:
        rec = requests.post(url, data=sql, headers=headers)
    except Exception as err:
        print(err, f'url:{url} sql:{sql[:500]} headers:{headers}')
        return None
    if rec.status_code == 200:
        json = rec.json()
        if 'head' in json.keys():
            rev = pd.DataFrame(json['data'], columns=json['head'])
            if rev.shape[0]>0:
                rev = _conver_dtype(rev, set_id)
            else:
                rev = None
        elif 'column_meta' in json.keys():
            temp = pd.DataFrame(json['column_meta'],
                                columns=['name', 'type', 'size'])
            rev = pd.DataFrame(json['data'], columns=temp['name'])
            if rev.shape[0]>0:
                rev = _conver_dtype(rev, set_id)
            else:
                rev = None
        else:
            rev = pd.Series(json)
    else:
        rev = None
        print(rec.request.url, rec.request.headers, rec.request.body,
              rec.status_code, rec.reason)
    return rev

def _normalize(sql):
    return pd.Series(sql).str.replace('\n +', ' ', regex=True).str.strip().squeeze()

def statement_export(start_time, database=None, set_id=None,
                         turbine_id=None, offset='1d'):
    ''' 构造查询语句 '''
    assert isinstance(set_id, (int, str)) and isinstance(turbine_id, (int, str))

    start_time = pd.to_datetime(start_time)
    end_time = start_time + pd.Timedelta(offset)
    columns = msql.read_model_point(set_id=set_id, select=1)['var_name'].tolist()
    columns = ['ts'] + columns

    sql = f'''
            select {','.join(columns)} from {database}.d_{turbine_id}
            where
            ts>="{start_time}" and ts<"{end_time}";
          '''
    return _normalize(sql)

def statement_creat_database(database):
    ''' 在本地tdengine建立数据库 '''
    sql = f'''
            CREATE DATABASE IF NOT EXISTS {database} REPLICA 1 DURATION 10 KEEP 36500
            BUFFER 96 MINROWS 100 MAXROWS 4096 WAL_FSYNC_PERIOD 3000 CACHEMODEL
            'last_row' COMP 2 PRECISION 'ms';
          '''
    return _normalize(sql)

def statement_creat_super_table(database, set_id):
    ''' 在本地tdengine建立超级表 '''
    point_df = msql.read_model_point(set_id=set_id, select=1)
    point_df['datatype'].replace({'F':'Float', 'I':'INT', 'B':'BOOL'}, inplace=True)
    columns = point_df['var_name']+' '+point_df['datatype']

    sql = f'''
            CREATE STABLE IF NOT EXISTS {database}.s_{set_id}
            (ts TIMESTAMP, {','.join(columns)})
            TAGS (device NCHAR(20));
         '''
    return _normalize(sql)

def statement_creat_sub_table(database, set_id):
    ''' 在本地tdengine建立子表 '''
    turbine_ids = msql.read_windfarm_configuration(set_id=set_id)['turbine_id']

    sql_lst=[]
    for tid in turbine_ids:
        temp = (f'''
                CREATE TABLE IF NOT EXISTS {database}.d_{tid}
                USING {database}.s_{set_id} TAGS ("{tid}");
                ''')
        sql_lst.append(_normalize(temp))
    return sql_lst

def statement_insert_from_csv(src_path, database, replace='/mnt/hgfs/taos/bxj'):
    ''' 构造tdengine语句，从csv文件，插入数据 '''
    sql_lst=[]
    src_path = src_path.replace('\\','/')
    replace = src_path if replace==None else replace
    for i in Path(src_path).glob('*.csv'):
        turbine_id = i.name.split('_')[0]
        pathname = i.as_posix().replace(src_path, replace)
        temp = (f'''
                insert into {database}.d_{turbine_id} file '{pathname}';
                ''')
        sql_lst.append(_normalize(temp))
    return sql_lst

def insert(df, table, kwargs):
    ''' 插入数据 '''
    df = df.copy()
    columns = df.select_dtypes(['datetimetz', 'datetime', 'datetime64']).columns
    for col in columns:
        df[col] = "'" + df[col].astype(str) + "'"

    pathname = Path(cfg.TEMP_DIR)/f'tmp_{uuid.uuid4().hex}.csv'
    try:
        df.to_csv(pathname, index=False)
        sql = f"insert into {kwargs['database']}.{table} file '{pathname.as_posix()}';"
        # print(sql)
        # sql.replace('\\','/')
        # print(sql)
        rev = execute(sql, kwargs)
    finally:
        pathname.unlink()

    return rev

def get_table_names(set_id, kwargs):
    ''' 根据tag获取table，需要用6041端口 '''
    sql = f'show table tags from s_{set_id}'
    return call_rest_api(sql, set_id=set_id, kwargs=kwargs).set_index('device')

def get_dates(set_id, turbine_id, kwargs):
    ''' 获取指定set_id，turbin_id的所有日期，需要用6041端口 '''
    tb_df = get_table_names(set_id, kwargs)
    if tb_df.shape[0]<1:
        print('no subtables of {set_id}')
    tbname = tb_df['tbname'].to_dict().get(turbine_id)
    if tbname==None:
        print('device:{turbine_id} not found')
        return pd.DataFrame()
    sql = f'select distinct(timetruncate(ts, 1d)) as ts from {tbname}'
    rev = call_rest_api(sql, set_id=set_id, kwargs=kwargs)
    if rev is None:
        print(f'empty talbe:{tbname}')
        return pd.DataFrame()
    rev.columns = ['date']
    rev['date'] = rev['date'].dt.date
    rev['table'] = tbname
    return rev.sort_values('date').reset_index(drop=True)

def initiate(dbname, set_id):
    kwarg = cfg.LOCAL_DRIVER
    kwarg.pop('database')
    
    sql = statement_creat_database(dbname)
    execute(sql, kwarg)

    sql = statement_creat_super_table(dbname, set_id)
    execute(sql, kwarg)

    sqls = statement_creat_sub_table(dbname, set_id)
    for i in sqls:
        execute(i, kwarg)