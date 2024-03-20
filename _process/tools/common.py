import pandas as pd
import numpy as np
from typing import List, Union

from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.config import get_td_local_connector, get_td_remote_restapi
from wtbonline._process.model.anormlay import OUTPATH
from wtbonline._common.utils import make_sure_list, make_sure_dataframe

EPS = np.finfo(np.float32).eps

def concise(sql):
    ''' 去除多余的换行、空格字符 '''
    sql = pd.Series(sql).str.replace('\n', '').str.replace(' {2,}', ' ', regex=True)
    sql = sql.str.strip().squeeze()
    return sql

def get_all_table_tags(set_id=None, remote=False):
    if set_id is None:
        set_ids = RSDBFacade.read_windfarm_configuration()['set_id'].unique()
    else:
        set_ids = make_sure_list(set_id)
    rev = []
    for i in set_ids:
        temp = TDFC.get_table_tags(i, remote).to_frame()
        temp.insert(0, 'set_id', i)
        rev.append(temp)
    rev = pd.concat(rev, ignore_index=True)
    rev.sort_values(['set_id', 'device'], inplace=True)
    return rev

def standard(set_id, df):
    ''' 按需增加turbine_id、测点名称、设备编号 '''
    df = df.copy()
    conf_df = RSDBFacade.read_windfarm_configuration(set_id=set_id)
    if 'var_name' in df.columns and ('测点名称' not in df.columns) :
        point_df = RSDBFacade.read_turbine_model_point(set_id=set_id)
        dct = {row['var_name']:row['point_name'] for _,row in point_df.iterrows()}
        df.insert(0, 'point_name', df['var_name'].replace(dct))
    df = pd.merge(df, conf_df[['set_id', 'turbine_id', 'map_id']], how='inner')
    df['device'] = df['turbine_id']     
    return df 

def get_dates_tsdb(turbine_id, remote=True):
    ''' 获取指定机组在时许数据库中的所有唯一日期
    >>> turbine_id = 's10001'
    >>> len(get_dates_tsdb(turbine_id, remote=True))>0
    True
    '''
    db = get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
    sql = f'select first(ts) as date from {db}.d_{turbine_id} interval(1d) sliding(1d)'
    sr = TDFC.query(sql=sql, remote=remote)['date']
    sr = pd.to_datetime(sr).dt.date
    sr = sr.drop_duplicates().sort_values()
    return sr

def get_min_date_tsdb(set_id, device_id:Union[str, List[str]]=None, remote=True):
    '''
    >>> get_min_date_tsdb(set_id='20835', remote=True)
             date device_id
    0  2022-12-18    s10003
    1  2022-12-26    s10004
    >>> get_min_date_tsdb(set_id='20835', remote=False)
             date device_id
    0  2022-12-18    s10003
    1  2022-12-26    s10004
    '''
    device_id = make_sure_dataframe(device_id)
    db = get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
    columns = ['first(ts) as date'] if remote==True else ['first(ts) as date', 'device'] 
    sql = f'''select {','.join(columns)} from {db}.s_{set_id} group by device'''  
    rev = TDFC.query(sql=sql, remote=remote)
    rev['date'] = pd.to_datetime(rev['date']).dt.date
    if len(device_id)>0:
        rev = pd.merge(device_id, rev, how='left')
    rev = rev.sort_values('device').reset_index(drop=True)
    rev.rename(columns={'device':'device_id'}, inplace=True)
    return rev


#%% test
if __name__ == "__main__":
    import doctest
    doctest.testmod()