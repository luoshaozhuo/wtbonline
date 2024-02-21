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
        notification = dmc.Notification(
            id=f"simple_notify_{np.random.randint(0, 100)}",
            title=note_title,
            action="show",
            autoClose=False,
            message=f'func={func.__name__},args={args},{kwargs},errmsg={e}',
            color='red',
            icon=DashIconify(icon="mdi:alert-rhombus", width=20),
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
    df, note = dash_try(note_title=cfg.NOTIFICATION_TITLE_DBQUERY, func=func, *args, **kwargs)
    if df is not None and len(df)==0:
        note = dmc.Notification(
            id=f"simple_notify_{np.random.randint(0, 100)}",
            title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA,
            action="show",
            autoClose=False,
            message=f'func={func.__name__},args={args},{kwargs}',
            color='yellow',
            icon=dmc.DashIconify(icon="mdi:question-mark-circle-outline", width=20),
            )
    return df, note

if __name__ == "__main__":
    import doctest
    doctest.testmod()