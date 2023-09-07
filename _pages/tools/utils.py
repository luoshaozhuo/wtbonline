# -*- coding: utf-8 -*-
"""
Created on Mon Nov 4 09:28:04 2023

@author: luosz

数据操作工具集，加上缓存机制
"""

import pandas as pd
from typing import List, Union
from functools import lru_cache

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC 
from wtbonline._db.common import make_sure_list
from wtbonline._process.modelling import data_filter
from wtbonline._logging import get_logger, log_it

_LOGGER = get_logger('page')
_CACHE_SIZE_SMALL = 100
_CACHE_SIZE_MEDIAN = 10000
_CACHE_SIZE_LARGE = 250000


@lru_cache(maxsize=_CACHE_SIZE_SMALL)
def mapid_to_tid(set_id, map_id:Union[str, tuple[str]]):
    '''
    >>> set_id='20835'
    >>> map_id=['F001', 'F002']
    >>> len(mapid_to_tid(set_id, map_id))==2
    True
    >>> isinstance(mapid_to_tid(set_id, map_id[0]), str)
    True
    '''
    map_id = make_sure_list(map_id)
    df = RSDBInterface.read_windfarm_configuration(
        set_id=set_id, 
        map_id=map_id,
        )
    assert df.shape[0]==len(map_id), f'{map_id}找不到对应的turbine_id'
    return df['turbine_id'].squeeze()

@lru_cache(maxsize=_CACHE_SIZE_SMALL)
def available_variable(set_id:str):
    df = RSDBInterface.read_turbine_model_point(
        set_id=set_id, 
        columns=['var_name', 'point_name', 'datatype'],
        select=1
        )
    df['var_name'] = df['var_name'].str.lower()
    df.drop_duplicates()
    rev_all = [{'label':i['point_name'], 'value':i['var_name']} for _,i in df.iterrows()]
    rev_all += [{'label':'', 'value':''}]
    df = df[df['datatype']=='F']
    rev_float = [{'label':i['point_name'], 'value':i['var_name']} for _,i in df.iterrows()]
    rev_float += [{'label':'', 'value':''}]
    return rev_all, rev_float

@lru_cache(maxsize=_CACHE_SIZE_SMALL)
def var_name_to_point_name(
        set_id:str, 
        var_name:Union[str, tuple[str]]=None, 
        point_name:Union[str, tuple[str]]=None
        ):
    var_name = make_sure_list(var_name)
    point_name = make_sure_list(point_name)
    assert len(var_name)>0 or len(point_name)>0
    
    df = RSDBInterface.read_turbine_model_point(
        set_id=set_id, 
        columns=['var_name', 'point_name', 'datatype'],
        select=1
        )
    df['var_name'] = df['var_name'].str.lower()
    df.drop_duplicates()
    
    if len(var_name)>0:
        df = df.set_index('var_name')
        rev = df.loc[var_name]['point_name'].tolist()
    else:
        df = df.set_index('point_name')
        rev = df.loc[point_name]['var_name'].tolist()
    return rev


def read_sample_ts(sample_id:int, var_name:Union[str, tuple[str]]):
    '''
    >>> sample_id=2342
    >>> point_name = ['var_355', 'var_101']
    >>> _ = read_sample_ts(sample_id, point_name)
    '''
    columns = ['set_id', 'turbine_id', 'bin']
    sample =  RSDBInterface.read_statistics_sample(
        id_=sample_id, 
        columns=columns
        ).squeeze()
    var_name= pd.Series(make_sure_list(var_name)).drop_duplicates().dropna()
    df,point_df = tdfc_read_cache(
        set_id=sample['set_id'],
        turbine_id=sample['turbine_id'],
        start_time=sample['bin'],
        end_time=sample['bin']+pd.Timedelta('10m'),
        )
    df = df[var_name.tolist() + ['ts', 'device']]
    point_df = point_df.set_index('var_name', drop=False).loc[var_name]
    return df, point_df


def read_scatter_matrix_anormaly(
        set_id:str, 
        *,
        turbine_id:str=None, 
        map_id:str=None, 
        columns:Union[str, tuple[str]]=None, 
        sample_cnt:int=5000
        ):
    assert columns is not None
    turbine_id = turbine_id if turbine_id is not None else mapid_to_tid(set_id, map_id)
    columns_aug = tuple([
        'id', 'set_id', 'turbine_id', 'pv_c', 'validation',
        'limitpowbool_mode' ,'limitpowbool_nunique',
        'workmode_mode', 'workmode_nunique',
        'totalfaultbool_mode', 'totalfaultbool_nunique',
        ])
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, turbine_id=turbine_id, columns=columns+columns_aug,
        ).set_index('id', drop=False)
    df = data_filter(df).loc[:, columns+ tuple(['id'])]
    
    df.insert(0, 'is_anormaly', 0)
    idx = RSDBInterface.read_model_anormaly(
        set_id=set_id, turbine_id=turbine_id
        ).drop_duplicates('sample_id')['sample_id']
    idx = idx[idx.isin(df.index)]
    df.loc[idx, 'is_anormaly'] = 1
    
    sub_normal = df[df['is_anormaly']==0]
    sub_normal = sub_normal.sample(sample_cnt) if sub_normal.shape[0]>sample_cnt else sub_normal
    sub_anormal = df[df['is_anormaly']==1]
    df = pd.concat([sub_normal, sub_anormal], ignore_index=True)
    return df


def read_anormaly_without_label(
        set_id:str, 
        turbine_id:str=None, 
        map_id:str=None, 
        labeled:bool=False
        ):
    '''
    >>> set_id = '20835'
    >>> turbine_id = 's10001'
    >>> _ = read_anormaly_without_label(set_id, turbine_id)
    '''
    turbine_id = turbine_id if turbine_id is not None else mapid_to_tid(set_id, map_id)
    rev = RSDBInterface.read_model_anormaly(
        set_id=set_id, turbine_id=turbine_id
        ).drop_duplicates('sample_id')
    if labeled == False:
        df = (
            RSDBInterface.read_model_label(set_id=set_id, turbine_id=turbine_id)
                .drop_duplicates('sample_id')
            )
        rev = rev[~rev['sample_id'].isin(df['sample_id'])]
    return rev


def read_sample_label(sample_id:str):
    sr = RSDBInterface.read_model_label(sample_id=sample_id).squeeze()
    if len(sr)<1:
        rev = 0
    else:
        rev = sr['is_anormaly']
    return rev


def read_raw_data(
        set_id:str, 
        map_id:str, 
        point_name:Union[str, tuple[str]], 
        start_time:pd.Timestamp,
        end_time:pd.Timestamp,
        sample_cnt:int=20000
        ):
    turbine_id = mapid_to_tid(set_id, map_id)
    df, desc_df = TDFC.read(
        set_id=set_id, 
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        point_name=point_name,
        limit = sample_cnt
        )
    desc_df.set_index('point_name', inplace=True, drop=False)
    return df, desc_df


@lru_cache(maxsize=_CACHE_SIZE_LARGE)
def tdfc_read_cache(set_id, turbine_id, start_time, end_time):
    var_name = (
        RSDBInterface.read_turbine_model_point(select=1, columns=['var_name'])
        .drop_duplicates()
        .squeeze()
        .str.lower()
        )
    df,point_df = TDFC.read(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        var_name=var_name
        )
    return df,point_df 


@log_it(_LOGGER, True)    
def update_cache(*args, **kwargs):
    mapid_to_tid.cache_clear()
    tdfc_read_cache.cache_clear()
    delta = RSDBInterface.read_app_configuration(key_='cache_days')
    delta = int(delta['value'].iloc[0])
    anomaly_ids = (
        RSDBInterface.read_model_anormaly(columns=['sample_id'])
        .drop_duplicates()
        .squeeze()
        )
    anomaly_df = (RSDBInterface.read_statistics_sample(
            id_=anomaly_ids,
            columns=['set_id', 'turbine_id', 'bin']
            )
        .drop_duplicates()
        .squeeze()
        )
    sample_df = (
        RSDBInterface.read_statistics_sample(
            columns=['set_id', 'turbine_id', 'bin'],
            start_time=pd.Timestamp.now()-pd.Timedelta(f'{delta}d'))
        .drop_duplicates()
        .squeeze()
        )
    df = pd.concat([anomaly_df, sample_df], ignore_index=True)
    df.drop_duplicates(inplace=True)
    
    for _, row in df.iterrows():
        print(row['turbine_id'], row['bin'])
        _ = tdfc_read_cache(
            set_id=row['set_id'],
            turbine_id=row['turbine_id'],
            start_time=row['bin'],
            end_time=row['bin']+pd.Timedelta('10m'),
            )


# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()