# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:19:56 2023

@author: luosz

计算turbine_model_points中stat_sample=1字段的样本统计值
"""

#%% import
import pandas as pd
import time
import numpy as np
import inspect

from wtbonline._db.common import make_sure_datetime, make_sure_dataframe
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb.dao import RSDB
import wtbonline._db.rsdb.model as model
from wtbonline._process.tools.time import bin
from wtbonline._process.tools.common import concise, get_all_table_tags
from wtbonline._process.tools.statistics import (
    numeric_statistics, category_statistics, stationarity, agg)
from wtbonline._process.tools import inspector as insp
from wtbonline._process.preprocess import get_dates_tsdb

from wtbonline._logging import get_logger, log_it

#%% constant
_LOGGER = get_logger('statistic')

#%% fucntion
def _validate(df, col1, col2, atol, rtol, _min=None, _max=None) -> int:
    ''' 检测是否超出阈值
    atol : float
        绝对阈值
    rtol : float
        相对阈值
    _min : float
        最小值
    _max : float
        最大值
    return : int, 1 或 0
        1=超出阈值
    '''
    rev = 0
    if col1 in df.columns and col2 in df.columns:
        if rtol != None:
            diff = abs(df[col1].median() - df[col2].median())
            ref =  abs(df[col1].median())
            rev = rev if diff<ref*rtol else 1
        if atol != None:
            diff = (df[col1].rolling(10).mean() - df[col2].rolling(10).mean()).abs().max()
            rev = rev if diff<atol else 1
        if _min != None:
            rev = rev if rev>=_min else 1
        if _max != None:
            rev = rev if rev<=_max else 1
    return rev

def validate_measurement(df, gearbox_ratio) -> int:
    ''' 利用冗余传感器验证测量数据 
    十进制数的每一位代表一个检测项目，对应位为1表示此项检测不通过，全0表示所有检测通过
    '''
    df = df.copy()
    df['rptspd'] = df['var_94']*gearbox_ratio
    if 'var_2732' in df.columns:
        df['torque'] = df['var_2732']*2
    rev = 0
    # var_101 1#叶片实际角度, var_104 1#叶片冗余变桨角度
    rev += _validate(df, 'var_101', 'var_104', 2, None)
    # var_102 2#叶片实际角度, var_105 1#叶片冗余变桨角度
    rev += _validate(df, 'var_102', 'var_105', 2, None)*10
    # var_103 3#叶片实际角度, var_106 1#叶片冗余变桨角度
    rev += _validate(df, 'var_103', 'var_106', 2, None)*100
    # var_355 1#风速计瞬时风速, var_356 2#风速计瞬时风速
    rev += _validate(df, 'var_355', 'var_356', None, 0.1, 0, 100)*1000
    # var_226 发电机转矩, var_2732 变频器1发电机转矩
    rev += _validate(df, 'var_226', 'torque', None, 0.05)*10000
    # , var_2731 变频器1发电机转速反馈, var_94 风轮转速
    rev += _validate(df, 'var_2731', 'rptspd', None, 0.05)*100000
    return rev


def statistic_sample(df, set_id:str, turbine_id:str, bin_length:str='10min')->pd.DataFrame:
    ''' 计算统计量 
    >>> set_id='20835'
    >>> turbine_id='s10001'
    >>> start_time=make_sure_datetime('2023-07-01')
    >>> df, _ = TDFC.read(
    ...     set_id=set_id,
    ...     turbine_id=turbine_id, 
    ...     start_time=start_time,
    ...     end_time=start_time+pd.Timedelta('1d'),
    ...     remote=False
    ...     )
    >>> stat_df = statistic_sample(df, set_id, turbine_id)
    >>> stat_df.shape
    (144, 160)
    >>> stat_df['create_time'] = pd.Timestamp.now()
    >>> RSDBInterface.insert(stat_df, 'statistics_sample')
    '''
    df = make_sure_dataframe(df)
    if len(df)<10:
        return pd.DataFrame()
    df['bin'] = bin(df['ts'])

    point_df = RSDBInterface.read_turbine_model_point(set_id=set_id, stat_sample=1)
    cols = point_df['var_name'].str.lower().tolist() 
    cols += ['ts', 'bin']

    conf_df = RSDBInterface.read_windfarm_configuration(set_id=set_id, turbine_id=turbine_id)
    gearbox_ratio = conf_df['gearbox_ratio'].squeeze()

    sub_df = df[cols]
    f_col = sub_df.select_dtypes(float).columns
    f_stats = numeric_statistics()
    c_col = sub_df.select_dtypes(['bool','category', 'int']).columns
    c_stats = category_statistics()

    validation = validate_measurement(df, gearbox_ratio)

    rev = []
    for _bin,grp in sub_df.groupby('bin'):
        a = agg(grp[f_col], f_stats)
        b = agg(grp[c_col], c_stats)
        c = pd.Series({
            'nobs':grp.shape[0], 
            'bin':_bin,
            })
        d = stationarity(grp['var_355'])
        rev.append(pd.concat([a,b,c,d]))
    rev = pd.DataFrame(rev)
    rev['validation'] = validation
    rev['set_id'] = set_id
    rev['turbine_id'] = turbine_id
    rev.replace({np.nan:None}, inplace=True)
    rev.replace({np.inf:None}, inplace=True)
    rev.replace({-1*np.inf:None}, inplace=True)
    return rev

def dates_in_statistic_sample(set_id, turbine_id):
    '''
    >>> set_id, turbine_id = '20835', 's10001'
    >>> _ = dates_in_statistic_sample(set_id, turbine_id)
    '''
    sql = f'''
        select DISTINCT date(bin) as dt from statistics_sample 
        where
        set_id='{set_id}' and turbine_id='{turbine_id}'
        '''
    return RSDB.read_sql(sql)['dt']

def statistic_daily(set_id, turbine_id, date):
    dt = pd.to_datetime(date)
    sql = f'''
        select 
            UNIQUE(faultcode) as faultcode
        from
            d_{turbine_id}
        where
            ts>='{dt}'
            and ts<'{dt+pd.Timedelta('1d')}'
        '''
    sql = concise(sql)
    faultcode = ','.join(TDFC.query(sql)['faultcode'].astype(str))
    sql = f'''
        select 
            '{set_id}',
            '{turbine_id}',
            '{date}',
            COUNT(ts),
            last(totalenergy)-first(totalenergy) as energy_output,
            '{faultcode}'
        from
            d_{turbine_id}
        where
            ts>='{dt}'
            and ts<'{dt+pd.Timedelta('1d')}'
        '''
    sql = concise(sql)
    return TDFC.query(sql)


@log_it(_LOGGER, True)
def udpate_statistic_daily():
    columns = ['set_id', 'turbine_id', 'date', 'count_sample', 'energy_output', 'fault_codes']
    conf_df = RSDBInterface.read_windfarm_configuration()[['set_id', 'turbine_id']]
    for _, (set_id, turbine_id) in conf_df.iterrows(): 
        exist_dates = RSDBInterface.read_statistics_daily(set_id=set_id, turbine_id=turbine_id, columns='date')['date']
        tsdb_dates = get_dates_tsdb(turbine_id, remote=False)
        tsdb_dates.index =  tsdb_dates
        date_lst = tsdb_dates.drop(exist_dates, errors='ignore')
        if len(date_lst)<1:
            continue
        
        df = []    
        for date in date_lst:
            df.append(statistic_daily(set_id, turbine_id, date).iloc[0].tolist())
        df = pd.DataFrame(df, columns=columns)
        df['create_time'] = pd.Timestamp.now()
        RSDBInterface.insert(df, 'statistics_daily')
 
            
@log_it(_LOGGER, True)
def udpate_statistic_fault():
    candidate_df = get_all_table_tags()
    objs = []
    for i,j in inspect.getmembers(insp, inspect.isclass):
        if str(j).find('Inspector')>-1 and str(j).find('Base')==-1:
            objs.append(j())
    if candidate_df.shape[0]<1 or len(objs)<1:
        return
    replace_dct = RSDBInterface.read_turbine_fault_type()
    replace_dct = {row['name']:row['id'] for _,row in replace_dct.iterrows()}
    
    table_columns = ['set_id', 'turbine_id', 'date', 'timestamp', 'fault_id', 'create_time']
    columns = ['set_id', 'turbine_id', 'timestamp', 'type']
    sql_tsdb = f"select first(ts) as ts from d_%s"
    sql_rsdb = "select max(date) as date from statistics_fault where turbine_id='%s'"
    for _, (set_id, turbine_id) in candidate_df[['set_id','device']].iterrows():  
        start_time = RSDB.read_sql(sql_rsdb%turbine_id)['date'].iloc[0]
        if start_time is not None:
            start_time = pd.to_datetime(pd.to_datetime(start_time).date()) + pd.Timedelta('1d')
        else:
            start_time = TDFC.query(sql_tsdb%turbine_id)['ts'].iloc[0]
        end_time = pd.to_datetime((pd.Timestamp.now()-pd.Timedelta('1d')).date())
        
        df = []    
        for obj in objs:
            temp = obj.inspect(set_id, turbine_id, start_time, end_time)
            if temp.shape[0]>0:
                temp['type'] = obj.name
                temp.rename(columns={'ts':'timestamp'}, inplace=True)
                df += temp[columns].to_dict('split')['data']
        if len(df)<1:
            continue
        
        df = pd.DataFrame(df, columns=columns)
        df['fault_id'] = df['type'].replace(replace_dct)
        df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        df['create_time'] = pd.Timestamp.now()
        df.sort_values('date', inplace=True)
        RSDBInterface.insert(df[table_columns], 'statistics_fault')
        

@log_it(_LOGGER, True)
def update_statistic_sample(*args, **kwargs):
    ''' 本地sample查缺 
    # >>> update_statistic_sample()
    '''
    task_id = kwargs.get('task_id', 'NA')
    for i in range(10):
        df = RSDBInterface.read_windfarm_configuration()[['set_id', 'turbine_id']]
        if len(df)>0:
            break
        _LOGGER.warning('update_statistic_sample: windfarm_configuration 查询失败，2秒后重试')
        time.sleep(2)
    if len(df)==0:
        raise ValueError('update_statistic_sample: windfarm_configuration 查询失败')
    for _, (set_id, turbine_id) in df.iterrows():
        _LOGGER.info(f'update_statistic_sample: {set_id}, {turbine_id}')
        # 本地tsdb已存在的数据日期
        tsdb_dates = get_dates_tsdb(turbine_id, remote=False)
        statistics_dates = dates_in_statistic_sample(set_id, turbine_id)
        # statistics_sample表
        candidates = tsdb_dates[~tsdb_dates.isin(statistics_dates)]
        for dt in candidates:
            _LOGGER.info(f'task_id={task_id} update_statistic_sample: {set_id}, {turbine_id}, {dt}')
            dt = make_sure_datetime(dt)
            df, _ = TDFC.read(
                set_id=set_id,
                turbine_id=turbine_id, 
                start_time=dt,
                end_time=dt+pd.Timedelta('1d'),
                remote=False,
                remove_tz=True,
                )
            stat_df = statistic_sample(df, set_id, turbine_id)
            if len(stat_df)<1:
                return
            stat_df['create_time'] = pd.Timestamp.now()
            RSDBInterface.insert(stat_df, 'statistics_sample')
            del df, stat_df, _


#%% main
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()