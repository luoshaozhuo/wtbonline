import pandas as pd
from collections.abc import Iterable
from typing import Union, Optional
import numpy as np
import datetime

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import no_update

import wtbonline.configure as cfg
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
import wtbonline._common.dash_component as cmpt
from wtbonline._process.tools.filter import filter_for_modeling

def make_sure_dict(x)->dict:
    '''
    >>> make_sure_dict(1)
    {}
    >>> make_sure_dict({'a':1})
    {'a': 1}
    >>> make_sure_dict(pd.Series([1,2]))
    {0: 1, 1: 2}
    >>> make_sure_dict(pd.DataFrame([['a','b'],[1,2]]))
    {'a': 'b', 1: 2}
    >>> make_sure_dict(None)
    {}
    '''
    if isinstance(x, dict):
        return x
    
    if isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze()
        elif x.shape[1]==2:
            x = {row[0]:row[1] for _,row in x.iterrows()}
    if isinstance(x, pd.Series):
        x = x.to_dict()
    if not isinstance(x, dict):
        x = {}
    return x

def make_sure_dataframe(x)->pd.DataFrame:
    '''
    >>> make_sure_dataframe(1)
    Empty DataFrame
    Columns: []
    Index: []
    >>> make_sure_dataframe({'a':1,'b':2})
       a  b
    1  1  2
    >>> make_sure_dataframe(pd.Series([1,2], name='x'))
       x
    0  1
    1  2
    >>> make_sure_dataframe(pd.DataFrame([['a','b'],[1,2]]))
       0  1
    0  a  b
    1  1  2
    >>> make_sure_dataframe(None)
    Empty DataFrame
    Columns: []
    Index: []
    '''
    if isinstance(x, pd.DataFrame):
        return x
    
    if isinstance(x, dict):
        x = pd.DataFrame(x, index=[1])
    elif isinstance(x, (list, tuple)):
        x = pd.DataFrame(x, index=np.arange(len(x)))
    elif isinstance(x, pd.Series):
        x = x.to_frame()
    elif isinstance(x, np.ndarray):
        x = pd.DataFrame(x)
    
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame()
    return x

def make_sure_series(x)->pd.Series:
    '''
    # >>> make_sure_series(1)
    # 0    1
    # dtype: int64
    # >>> make_sure_series({'a':1})
    # a    1
    # dtype: int64
    # >>> make_sure_series(pd.Series([1,2], name='x'))
    # 0    1
    # 1    2
    # Name: x, dtype: int64
    >>> make_sure_series(pd.DataFrame([['a','b'],[1,2]]))
    0
    a    b
    1    2
    Name: 1, dtype: object
    >>> make_sure_series(None)
    Series([], dtype: object)
    '''
    if isinstance(x, pd.Series):
        return x

    if isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze()
        elif x.shape[1]==2:
            x = x.set_index(x.columns[0]).squeeze()
        else:
            x = pd.Series()
    elif x is None:
        x = pd.Series()
    elif isinstance(x, str):
        x = pd.Series(x)
    elif isinstance(x, Iterable):
        x = pd.Series([i for i in x])
    else:
        x = pd.Series([x])
    return x

def make_sure_list(x)->list:
    ''' 确保输入参数是一个list 
    >>> make_sure_list('abc')
    ['abc']
    >>> make_sure_list(1)
    [1]
    >>> make_sure_list(pd.Series([1,2]))
    [1, 2]
    >>> make_sure_list(pd.DataFrame([1,2]))
    [1, 2]
    >>> make_sure_list(pd.DataFrame([[1,2],[3,4]]))
    [[1, 3], [2, 4]]
    '''
    if isinstance(x, list):
        rev = x
    elif x is None:
        x = []
    elif isinstance(x, str):
        x = [x]
    elif hasattr(x, 'tolist'):
        x = x.tolist()
    elif isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze().tolist()
        else:
            x = [x[i].tolist() for i in x]        
    elif isinstance(x, Iterable):
        x = [i for i in x]
    else:
        x = [x]
    return x

def make_sure_datetime(
        x:Union[str, Iterable]
        )->Optional[Union[pd.Timestamp, list[pd.Timestamp], pd.Series]]:
    '''
    >>> type(make_sure_datetime('2020-10-01'))
    <class 'pandas._libs.tslibs.timestamps.Timestamp'>
    >>> a,b = make_sure_datetime(['2020-10-01', '2020-10-02'])
    >>> type(a)
    <class 'pandas._libs.tslibs.timestamps.Timestamp'>
    '''
    if isinstance(x, (pd.Timestamp, datetime.date)):
        rev = x
    elif isinstance(x, str):
        rev = pd.to_datetime(x)
    elif isinstance(x, (list, tuple)):
        rev = pd.to_datetime(x).tolist()
    elif isinstance(x, pd.Series):
        rev = pd.to_datetime(x)
    elif isinstance(x, pd.DataFrame):
        x = x.squeeze()
        if isinstance(x, pd.Series):
            rev = pd.to_datetime(x.squeeze())
        else:
            rev = None
    else:
        rev = None
    return rev

def dash_get_component_id(suffix, prefix=''):
    '''
    用于dash pages，将prefix及suffix拼接成控件ID
    '''
    return prefix + '_' + suffix

def dash_try(note_title, func, *args, **kwargs):
    '''
    用于dash pages，返回func的运行结果及dash-mantine-component的notification控件
    '''
    try:
        rs = func(*args, **kwargs)
        notification = no_update
    except Exception as e:
        rs = None
        notification = cmpt.notification(
            title=note_title,
            msg=f'func={func.__name__},args={args},{kwargs},errmsg={e}',
            _type='error'
            )     
    return rs, notification    

def dash_make_datetime(date:str, time:str):
    '''
    用于dash pages，拼接日期及时间
    两个参数都是dash-mantine-component的datepicker及timeinput控件的value值
    date: 如2024-12-02
    time: 如2024-12-02T12:34:56
    '''
    return date + ' ' + time.split('T')[1]

def interchage_mapid_and_tid(map_id=None, turbine_id=None):
    assert not (map_id is None and turbine_id is None), 'neither map_id or turbine_id is specified'
    if map_id is not None:
        cond = cfg.WINDFARM_CONFIGURATION['map_id']==map_id
        col = 'turbine_id'
    elif turbine_id is None:
        cond = cfg.WINDFARM_CONFIGURATION['turbie_id']==turbine_id
        col = 'map_id'
    rev = cfg.WINDFARM_CONFIGURATION[cond]
    return rev[col].iloc[0] if len(rev)>0 else None

def get_fault_id(name):
    df = cfg.WINDFARM_FAULT_TYPE[cfg.WINDFARM_FAULT_TYPE['name']==name]
    if len(df)>0:
        rev = df['id'].iloc[0]
    else:
        rev = None
    return rev

def dash_dbquery(func, *args, **kwargs):
    df, note = dash_try(note_title=cfg.NOTIFICATION_TITLE_DBQUERY_FAIL, func=func, *args, **kwargs)
    if df is not None and len(df)==0:
        note = cmpt.notification(
            title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA,
            msg=f'func={func.__name__},args={args},{kwargs}',
            _type='warning'
            )
    return df, note

def read_raw_data(
        set_id:str, 
        map_id:str, 
        point_name:Union[str, tuple[str]], 
        start_time:pd.Timestamp,
        end_time:pd.Timestamp,
        sample_cnt:int=20000,
        remote=False,
        ):
    point_name = make_sure_list(point_name)
    turbine_id = interchage_mapid_and_tid(map_id=map_id)
    start_time = make_sure_datetime(start_time)
    end_time = make_sure_datetime(end_time)
    diff = (end_time - start_time).value/10**9
    
    if diff<=sample_cnt or remote==True:
        df = []
        # 远程数据库有可能限制每次查询的数据量
        for _ in range(30):
            tmp, desc_df = TDFC.read(
                set_id=set_id, 
                turbine_id=turbine_id,
                start_time=start_time,
                end_time=end_time,
                point_name=point_name,
                limit=sample_cnt,
                remote=remote
                )
            if len(tmp)>0:
                df.append(tmp)
                start_time=tmp['ts'].max()+pd.Timedelta('0.0001s')
            else:
                break
        df = pd.concat(df, ignore_index=True) 
        df = df.sample(sample_cnt) if len(df)>sample_cnt else df  
        df.sort_values('ts', inplace=True)
        desc_df.set_index('point_name', inplace=True, drop=False)
    else:
        interval = f'{int(diff/60/20)}m'
        cnt = min(int(sample_cnt/20), 1000)
        desc_df = RSDBInterface.read_turbine_model_point(set_id=set_id, point_name=point_name)
        desc_df['var_name'] = desc_df['var_name'].str.lower() 
        desc_df.set_index('point_name', inplace=True, drop=False)
        desc_df['column'] = desc_df['point_name'] + '_' + desc_df['unit']
        sql = f'''
            select sample(ts,{cnt}) as ts,{','.join(desc_df['var_name'])} from windfarm.d_{turbine_id}
            where
            ts>='{start_time}' and ts<'{end_time}'
            interval({interval})
            sliding({interval})
            '''
        sql = pd.Series(sql).str.replace('\n *', ' ', regex=True).squeeze().strip()
        df = TDFC.query(sql, remote=remote)
        df.sort_values('ts', inplace=True)
    return df, desc_df

def read_scatter_matrix_anormaly(
        set_id:str, 
        *,
        turbine_id:str=None, 
        map_id:str=None, 
        columns:Union[str, list[str]]=None, 
        sample_cnt:int=5000,
        df:pd.DataFrame=None
        ):
    '''
    读取所有异常数据，以及抽样正常数据（经过滤），总数不超过sample_cnt
    >>> set_id = '20835'
    >>> map_id = 'A03'
    >>> columns=tuple(['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean','var_382_mean', 'var_383_mean'])
    >>> df = read_scatter_matrix_anormaly(set_id, map_id=map_id, columns=columns)
    '''
    assert columns is not None, '没有指定字段'
    turbine_id = turbine_id if turbine_id is not None else interchage_mapid_and_tid(map_id=map_id)
    columns = make_sure_list(columns)
    columns = tuple(columns + ['id', 'bin'])
    columns_aug = tuple([
        'set_id', 'turbine_id', 'pv_c', 'validation',
        'limitpowbool_mode' ,'limitpowbool_nunique',
        'workmode_mode', 'workmode_nunique', 'ongrid_mode', 'ongrid_nunique',
        'totalfaultbool_mode', 'totalfaultbool_nunique',
        ])
    # 读取所有统计数据
    # filter会筛除大部分数据，所以用4倍sample_cnt来采样
    if df is None or len(df)<1:
        rev = RSDBInterface.read_statistics_sample(
            set_id=set_id, turbine_id=turbine_id, columns=tuple(columns+columns_aug), limit=4*sample_cnt, random=True
            )
        rev = filter_for_modeling(rev).loc[:, columns]
    else:
        rev = df
    # 合并异常数据
    idx = RSDBInterface.read_model_anormaly(
        set_id=set_id, turbine_id=turbine_id
        ).drop_duplicates('sample_id')['sample_id']
    if len(idx)>0:
        df = RSDBInterface.read_statistics_sample(id_=idx, columns=rev.columns)
        rev = pd.concat([df, rev], ignore_index=True)
    rev = rev.drop_duplicates('id').set_index('id', drop=False)
    rev.insert(0, 'is_suspector', -1)
    rev.loc[idx, 'is_suspector'] = 1
    # 增加标签字段
    df = RSDBInterface.read_model_label(set_id=set_id, turbine_id=turbine_id)
    df = df.sort_values('create_time').drop_duplicates('sample_id', keep='last')
    rev = pd.merge(
        df[['sample_id', 'is_anomaly']], 
        rev.reset_index(drop=True), 
        left_on='sample_id', 
        right_on='id', 
        how='right'
        ).drop(columns=['sample_id'])
    rev['is_anomaly'] = rev['is_anomaly'].fillna(0)
    # 抽样
    sub_anormal = rev[rev['is_anomaly']==1]
    count = sample_cnt - len(sub_anormal)
    sub_normal = rev[rev['is_anomaly']==0]
    sub_normal = sub_normal.sample(count) if sub_normal.shape[0]>count else sub_normal
    rev = pd.concat([sub_normal, sub_anormal], ignore_index=True)
    return rev

set_id = '20835'
map_id = 'A03'
columns=tuple(['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean','var_382_mean', 'var_383_mean'])
df = read_scatter_matrix_anormaly(set_id, map_id=map_id, columns=columns)


if __name__ == "__main__":
    import doctest
    doctest.testmod()