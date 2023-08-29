# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 13:31:22 2023

@author: luosz

从2.x版本的tdengine中读取数据，存入3.x的tdengine中
"""
# =============================================================================
# improt
# =============================================================================
import base64
import requests
import pandas as pd

from _database.config import SOURCE, LOCAL
from _database import operate as op

# =============================================================================
# constant
# =============================================================================
DB_NAME = 'scada'

# =============================================================================
# CONSTANTS
# =============================================================================
def call_rest_api(sql, host=SOURCE['host'], port=SOURCE['port'], 
                  user=SOURCE['user'], password=SOURCE['password']):
    ''' 调用restApi，默认访问源数据库 '''
    token = base64.b64encode(f"{user}:{password}".encode('utf-8'))
    token = str(token,'utf-8')
    headers={'Authorization':f'Basic {token}'}
    url = f"http://{host}:{port}/rest/sql/{DB_NAME}"
    rec = requests.post(url, data=sql, headers=headers)
    if rec.status_code == 200:
        json = rec.json()
        if 'head' in json.keys():
            df = pd.DataFrame(json['data'], columns=json['head'])
        else:
            df = pd.DataFrame(json)
    else:
        df = None
        print(rec.request.url, rec.request.headers, rec.request.body, 
              rec.status_code, rec.reason)
    return df

def construct_export_sql(start_time, set_id=None, turbine_id=None, offset='1d'):
    ''' 构造查询语句 '''
    assert isinstance(set_id, (int, str)) and isinstance(turbine_id, (int, str))
    
    start_time = pd.to_datetime(start_time)
    end_time = start_time + pd.Timedelta(offset)
    columns = op.read_model_point(set_id=set_id, select=1)['var_name'].tolist()
    columns = ['ts'] + columns
    
    sql = f'''
            select {','.join(columns)} from {DB_NAME}.d_{turbine_id} 
            where 
            ts>="{start_time}" and ts<"{end_time}"
          '''
    return sql

def creat_database():
    ''' 在本地tdengine建立数据库 '''
    sql = '''
            CREATE DATABASE IF NOT EXISTS scada REPLICA 1 DURATION 10 KEEP 36500 
            BUFFER 96 MINROWS 100 MAXROWS 4096 WAL_FSYNC_PERIOD 3000 CACHEMODEL 
            'last_row' COMP 2 PRECISION 'ms'
          '''    
    call_rest_api(sql, **LOCAL)

def construct_column_name(point_df):
    assert point_df['datatype'].hasnans==False
    point_df['datatype'].replace({'F':'Float', 'I':'INT', 'B':'BOOL'}, inplace=True)
    columns = point_df['var_name']+' '+point_df['datatype']
    return columns

def creat_super_table(set_id):
    ''' 在本地tdengine建立超级表 '''
    point_df = op.read_model_point(set_id=set_id, select=1)
    columns = construct_column_name(point_df)
    
    sql = f'''
            CREATE TABLE IF NOT EXISTS s_{set_id} 
            (ts TIMESTAMP, {','.join(columns)}) 
            TAGS (device NCHAR(20))
         '''   
    _ = call_rest_api(sql, **LOCAL)    
    
def creat_sub_table(set_id):
    ''' 在本地tdengine建立子表 '''
    turbine_ids = op.read_windfarm_configuration(set_id=set_id)['turbine_id']
    
    for tid in turbine_ids:
        sql = f'''
                CREATE TABLE IF NOT EXISTS d_{tid} 
                USING {DB_NAME}.s_{set_id} TAGS ("{tid}")
             '''
        _ = call_rest_api(sql, **LOCAL) 

def split_csv(set_id, turbine_id, n=1500000):
    ''' 将select >>> file 导出的csv文件分拆成150万条一个的小文件 
    要求文件名为f's{turbine_id}.csv', 子表名称f'd_s{turbin_id}', 超级表名称为
    f's_{set_id}'，函数返回数据导入语句
    '''
    conf_df = op.read_model_point(set_id=10050, select=1)
    conf_df['var_name'] = conf_df['var_name'].str.lower()
    conf_df['datatype'] = conf_df['datatype'].replace({'F':float, 'B':int, 'I':int})
    
    names = pd._libs.lib.no_default
    sql = f'CREATE TABLE IF NOT EXISTS scada.d_s{turbine_id} USING scada.s_10050 TAGS ("s{turbine_id}");'
    for i in range(0,24):
        df = pd.read_csv(r'D:\ll\scripts\app\data\s10005.csv', 
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
        df.to_csv(fr'D:\ll\scripts\app\data\s{turbine_id}-{i}.csv', index=False)
        sql += f"insert into scada.d_s{turbine_id} file '/home/source/dump/data/s{turbine_id}-{i}.csv';"
        print(i, df.ts.min(), df.ts.max())
    return sql


