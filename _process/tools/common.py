import pandas as pd
import numpy as np
from typing import List, Union

from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb_facade import RSDBFC
from wtbonline._db.config import get_td_local_connector, get_td_remote_restapi
from wtbonline._common.utils import make_sure_list
from wtbonline._db.postgres_facade import PGFC
from wtbonline._db.rsdb.dao import RSDB

EPS = np.finfo(np.float32).eps

def concise(sql):
    ''' 去除多余的换行、空格字符 '''
    sql = pd.Series(sql).str.replace('\n', '').str.replace(' {2,}', ' ', regex=True)
    sql = sql.str.strip().squeeze()
    return sql

def get_all_table_tags(set_id=None, remote=False):
    if set_id is None:
        set_ids = RSDBFC.read_windfarm_configuration()['set_id'].unique()
    else:
        set_ids = make_sure_list(set_id)
    rev = []
    for i in set_ids:
        temp = TDFC.get_deviceID(i, remote).to_frame()
        temp.insert(0, 'set_id', i)
        rev.append(temp)
    rev = pd.concat(rev, ignore_index=True)
    rev.sort_values(['set_id', 'device'], inplace=True)
    return rev

def standard(set_id, df):
    ''' 按需增加turbine_id、测点名称、设备编号 '''
    df = df.copy()
    conf_df = RSDBFC.read_windfarm_configuration(set_id=set_id)
    if 'var_name' in df.columns and ('测点名称' not in df.columns) :
        point_df = RSDBFC.read_turbine_model_point(set_id=set_id)
        dct = {row['var_name']:row['point_name'] for _,row in point_df.iterrows()}
        df.insert(0, 'point_name', df['var_name'].replace(dct))
    df = pd.merge(df, conf_df[['set_id', 'turbine_id', 'map_id']], how='inner')
    df['device'] = df['turbine_id']     
    return df 

def get_dates_tsdb(turbine_id, remote=True):
    ''' 获取指定机组在时许数据库中的所有唯一日期
    >>> turbine_id = 's10003'
    >>> len(get_dates_tsdb(turbine_id, remote=True))>0
    True
    '''
    db = get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
    sql = f'select first(ts) as date from {db}.d_{turbine_id} interval(1d) sliding(1d)'
    sr = TDFC.query(sql=sql, remote=remote)['date']
    sr = pd.to_datetime(sr).dt.date
    sr = sr.drop_duplicates().sort_values()
    return sr

def get_date_range_tsdb(device_id=None, remote=True):
    '''
    # >>> get_date_range_tsdb(remote=True)
    #   set_id device_id device_name  start_date    end_date
    # 0  20835    s10003         A03  2022-12-18  2023-10-10
    # 1  20835    s10004         A04  2022-12-26  2023-10-10
    # >>> get_date_range_tsdb(remote=False)
    #   set_id device_id device_name  start_date    end_date
    # 1  20835    s10003         A03  2022-12-18  2023-10-10
    # 0  20835    s10004         A04  2022-12-26  2023-10-10
    >>> get_date_range_tsdb(device_id='s10003')
      set_id device_id device_name  start_date    end_date
    0  20835    s10003         A03  2022-12-18  2023-10-10
    '''
    columns = {'ts':['first', 'last']}
    device_df = PGFC.read_model_device(device_id=device_id)
    rev = []
    for _,row  in device_df.iterrows():
        df = TDFC.read(
            set_id=row['set_id'],
            device_id=row['device_id'],
            groupby='device',
            columns=columns,
            remote=remote
            )
        if 'set_id' not in (df.columns):
            df['set_id'] = row['set_id']
        if 'device_id' not in (df.columns):
            df['device_id'] = row['device_id']
        rev.append(df)
    rev = pd.concat(rev, ignore_index=True)
    rev = rev.rename(columns={'ts_first':'start_date', 'ts_last':'end_date'})
    rev['start_date'] = pd.to_datetime(rev['start_date']).dt.date
    rev['end_date'] = pd.to_datetime(rev['end_date']).dt.date 
    device_df = PGFC.read_model_device()[['device_id', 'device_name']]
    rev = pd.merge(rev, device_df, how='left')
    rev = rev.sort_values('device_id')    
    columns = ['set_id','device_id','device_name', 'start_date','end_date'] 
    return rev[columns]

def get_date_range_statistics_sample(device_id:Union[str, List[str]]=None):
    '''
    >>> get_date_range_statistics_sample()
      set_id device_id device_name  start_date    end_date
    0  20835    s10003         A03  2022-12-18  2023-10-10
    1  20835    s10004         A04  2022-12-26  2023-01-14
    >>> get_date_range_statistics_sample(device_id='s10003')
      set_id device_id device_name  start_date    end_date
    0  20835    s10003         A03  2022-12-18  2023-10-10
    '''
    rev = RSDBFC.read_statistics_sample(
        device_id=device_id, 
        columns={'bin':['min', 'max']},
        groupby=['set_id', 'device_id']
        )
    rev = rev.rename(columns={'bin_min':'start_date', 'bin_max':'end_date'})
    rev['start_date'] = pd.to_datetime(rev['start_date']).dt.date
    rev['end_date'] = pd.to_datetime(rev['end_date']).dt.date    
    device_df = PGFC.read_model_device()[['device_id', 'device_name']]
    rev = pd.merge(rev, device_df, how='left')   
    rev = rev.sort_values('device_id')
    columns = ['set_id','device_id','device_name', 'start_date','end_date'] 
    return rev[columns]

#%% test
if __name__ == "__main__":
    import doctest
    doctest.testmod()