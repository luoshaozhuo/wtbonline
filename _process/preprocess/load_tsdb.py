#%% import
import pandas as pd
from typing import Union
from datetime import date
import time 

from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.time import resample
from wtbonline._logging import log_it
from wtbonline._process.preprocess import _LOGGER
from wtbonline._process.tools.common import get_dates_tsdb

#%% function
def extract(set_id:str, device_id:str, dt:Union[str, pd.Timestamp, date], 
            offset:str='1min', rule:str='1s', limit:int=2)->pd.DataFrame:
    ''' 按天从源数据库读入数据，重采样
    dt : str | date
        目标日期，如'2020-11-11'
    offset : str
        时间偏移量，设定为1min时，实际从数库读取数据时间跨度为
        '2020-11-10 23:59:00'至'2020-11-12 0:01:00'
    rule : str
        重采样周期
    limit : int
        连续最大插值数据条数
    bin_length : str
        每个bin的时间长度
    >>> set_id = '20835'
    >>> turbine_id = 's10001'
    >>> dt = '2023-05-04'
    >>> extract('20835', 's10003', '2023-06-01').shape
    (86394, 79)
    '''
    dt = pd.Timestamp(dt)
    start_time = dt - pd.Timedelta(offset)
    end_time = dt + pd.Timedelta('1d') + pd.Timedelta(offset)
    df = []
    var_name = RSDBFacade.read_turbine_model_point()['var_name']
    df = TDFC.read(
        set_id=set_id, 
        device_id=device_id, 
        start_time=start_time, 
        end_time=end_time,
        columns=var_name, 
        orderby='ts',
        remote=True
        )
    
    rev = pd.DataFrame()
    if df.shape[0]<10:
        print(f'not enough entries: {device_id}, {dt}')
        return rev
    rev = resample(df, rule=rule, limit=limit)

    if rev.shape[0]<1:
        print('no data left after resample')
        return rev
    rev = rev[rev['ts'].dt.date == dt.date()]

    if rev.shape[0]<1:
        print('no data left after trimming')
        return rev
   
    return rev

def load_tsdb(set_id:str, device_id:str, dt:Union[str, date]):
    ''' 抽取数据到本地TSDB
    >>> set_id='20625'
    >>> device_id='d10003'
    >>> start_time = pd.to_datetime('2023-12-26 00:00:00')
    >>> end_time = start_time + pd.Timedelta('1d')
    >>> n = extract(set_id, device_id, start_time).shape[0]
    >>> load_tsdb(set_id, device_id, start_time)
    >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time)
    >>> n == df.shape[0]
    True
    '''
    df = extract(set_id=set_id, device_id=device_id, dt=dt)
    TDFC.write(df, set_id=set_id, device_id=device_id)

@log_it(_LOGGER, True)
def update_tsdb(*args, **kwargs):
    ''' 本地TSDB查缺 '''
    task_id = kwargs.get('task_id', 'NA')
    for i in range(10):
        try:
            df = PGFacade.read_model_device()[['set_id', 'device_id']]
            if len(df)>0:
                break
        except Exception as e:
            _LOGGER.warning(f'update_tsdb: windfarm_configuration 查询失败，稍后重试，错误信息：{str(e)}')
        time.sleep(1)
    if len(df)==0:
        raise ValueError('update_tsdb: windfarm_configuration 查询失败')
    for _, (set_id, device_id) in df.iterrows():
        _LOGGER.info(f'update_tsdb: {set_id}, {device_id}')
        try:
            dtrm = get_dates_tsdb(device_id, remote=True) 
            dtlc = get_dates_tsdb(device_id, remote=False)
        except  Exception as e:
            _LOGGER.error(f'failed to update_tsdb: {set_id}, {device_id}. \n Error msg: {e}')
            continue
        dts = dtrm[~dtrm.isin(dtlc)]
        for date in dts:
            # 不更新当天数据
            if date>=pd.Timestamp.now().date():
                continue
            print(set_id, device_id, date)
            try:
                _LOGGER.info(f'task_id={task_id} update_tsdb: {set_id}, {device_id}, {date}')
                load_tsdb(set_id, device_id, date)
            except:
                _LOGGER.error(f'failed to update_tsdb: {set_id}, {device_id}, {date}')
                raise 
            
#%%
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    update_tsdb()