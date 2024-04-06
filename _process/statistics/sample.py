# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:19:56 2023

@author: luosz

计算turbine_model_points中stat_sample=1字段的样本统计值
"""

#%% import
from contourpy import SerialContourGenerator
import pandas as pd
import time
import numpy as np

from wtbonline._common.utils import make_sure_datetime, make_sure_dataframe
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._process.tools.time import bin
from wtbonline._process.tools.statistics import numeric_statistics, category_statistics, stationarity, agg
from wtbonline._process.tools.common import get_dates_tsdb
from wtbonline._process.statistics import _LOGGER
from wtbonline._db.postgres_facade import PGFacade

# constants
POINT_DF = RSDBFacade.read_turbine_model_point()
ALL_COLS = POINT_DF['var_name'].to_list()
F_COLS = POINT_DF[POINT_DF['datatype']=='F']['var_name'].to_list()
B_COLS = POINT_DF[POINT_DF['datatype']=='B']['var_name'].to_list()
I_COLS = POINT_DF[POINT_DF['datatype']=='I']['var_name'].to_list()

#%% fucntion
def statistic_sample(df, set_id, device_id, bin_length:str='10min')->pd.DataFrame:
    ''' 计算统计量 
    >>> set_id='20835'
    >>> device_id='s10003'
    >>> start_time=make_sure_datetime('2023-07-01')
    >>> df = TDFC.read(
    ...     set_id=set_id,
    ...     device_id=device_id, 
    ...     start_time=start_time,
    ...     end_time=start_time+pd.Timedelta('1d'),
    ...     remote=False
    ...     )
    >>> stat_df = statistic_sample(df, set_id, device_id)
    '''
    df = make_sure_dataframe(df).copy()
    if len(df)<10:
        return pd.DataFrame()
    df['bin'] = bin(df['ts'], length=bin_length)
    f_stats = numeric_statistics()
    c_stats = category_statistics()
    rev = []
    for _bin,grp in df.groupby('bin'):
        a = agg(grp[F_COLS], f_stats)
        b = agg(grp[B_COLS+I_COLS], c_stats)
        c = pd.Series({
            'nobs':grp.shape[0], 
            'bin':_bin,
            })
        d = stationarity(grp['winspd'])
        rev.append(pd.concat([a,b,c,d]))
    rev = pd.DataFrame(rev)
    rev['set_id'] = set_id
    rev['device_id'] = device_id
    rev.replace({np.nan:None}, inplace=True)
    rev.replace({np.inf:None}, inplace=True)
    rev.replace({-1*np.inf:None}, inplace=True)
    return rev

def dates_in_statistic_sample(set_id, device_id):
    '''
    >>> set_id, device_id = '20835', 's10003'
    >>> _ = dates_in_statistic_sample(set_id, device_id)
    '''
    sql = f'''
        select DISTINCT date(bin) as dt from statistics_sample 
        where
        set_id='{set_id}' and device_id='{device_id}'
        '''
    return RSDB.read_sql(sql)['dt'] 

def update_statistic_sample(*args, **kwargs):
    ''' 本地sample查缺  '''
    task_id = kwargs.get('task_id', 'NA')
    device_df = PGFacade.read_model_device()[['set_id', 'device_id']]
    for _, (set_id, device_id) in device_df.iterrows():
        _LOGGER.info(f'task_id={task_id} update_statistic_sample: {set_id}, {device_id}')
        tsdb_dates = get_dates_tsdb(device_id, remote=False)
        statistics_dates = dates_in_statistic_sample(set_id, device_id)
        candidates = tsdb_dates[~tsdb_dates.isin(statistics_dates)]
        for dt in candidates:
            _LOGGER.info(f'task_id={task_id} update_statistic_sample: {set_id}, {device_id}, {dt}')
            dt = make_sure_datetime(dt)
            df = TDFC.read(
                set_id=set_id,
                device_id=device_id, 
                start_time=dt,
                end_time=dt+pd.Timedelta('1d'),
                remote=False,
                )
            stat_df = statistic_sample(df, set_id, device_id)
            if len(stat_df)<1:
                return
            stat_df['create_time'] = pd.Timestamp.now()
            RSDBFacade.insert(stat_df, 'statistics_sample')
            del df, stat_df

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    update_statistic_sample()