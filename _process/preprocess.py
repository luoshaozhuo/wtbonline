#%% import
import pandas as pd
from typing import Union
from datetime import date
import time 


from wtbonline._db.common import make_sure_datetime
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.time import resample
from wtbonline._logging import get_logger, log_it
from wtbonline._db.config import get_td_local_connector, get_td_remote_restapi

#%% constant
_LOGGER = get_logger('preprocess')

#%% function
def statistic_accumulation(df):
    ''' 计算统计量 '''
    return pd.DataFrame([df.max()])

def statistic_operation(df):
    ''' 计算统计量 '''
    pass

def extract(set_id:str, turbine_id:str, dt:Union[str, pd.Timestamp, date], 
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
    >>> extract('20835', 's10001', '2023-05-01').shape
    (86372, 80)
    '''
    dt = pd.Timestamp(dt)
    start_time = dt - pd.Timedelta(offset)
    end_time = dt + pd.Timedelta('1d') + pd.Timedelta(offset)
    # tdengine 2.2.2.0 对restapi查询数据有限制，默认每次10240条
    df = []
    var_name = RSDBInterface.read_turbine_model_point(set_id=set_id, select=1)['var_name']
    var_name = var_name.str.lower()
    for i in range(10):
        temp, _ = TDFC.read(set_id=set_id, turbine_id=turbine_id, 
                        start_time=start_time, end_time=end_time,
                        var_name=var_name, orderby='ts', remote=True)
        start_time = str(temp['ts'].max().tz_localize(None))
        df.append(temp)
        if temp.shape[0]<10200:
            break
    df = pd.concat(df, ignore_index=True).drop_duplicates('ts').sort_values('ts')
    df.drop_duplicates('ts', inplace=True)

    rev = pd.DataFrame()
    if df.shape[0]<10:
        print(f'not enough entries: {turbine_id}, {dt}')
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

def get_dates_tsdb(turbine_id, remote=True):
    ''' 获取指定机组在时许数据库中的所有唯一日期
    >>> turbine_id = 's10001'
    >>> len(get_dates_tsdb(turbine_id, remote=True))>0
    True
    '''
    # sql = f'select distinct(timetruncate(ts, 1d)) as date from d_{turbine_id}'
    db =get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
    sql = f'select first(ts) as date from {db}.d_{turbine_id} interval(1d) sliding(1d)'
    sr = TDFC.query(sql=sql, remote=remote)['date']
    sr = pd.to_datetime(sr).dt.date
    sr = sr.drop_duplicates().sort_values()
    return sr

def load_tsdb(set_id, turbine_id, date):
    ''' 抽取数据到本地TSDB
    >>> set_id='20835'
    >>> turbine_id='s10001'
    >>> start_time = pd.to_datetime('2023-07-01 00:00:00')
    >>> end_time = start_time + pd.Timedelta('1d')
    >>> n = extract(set_id, turbine_id, start_time).shape[0]
    >>> load_tsdb(set_id, turbine_id, start_time)
    >>> df,_ = TDFC.read(set_id=set_id, turbine_id=turbine_id, start_time=start_time, end_time=end_time)
    >>> n == df.shape[0]
    True
    '''
    df = extract(set_id, turbine_id, date)
    TDFC.write(df, set_id=set_id, turbine_id=turbine_id)

@log_it(_LOGGER, True)
def update_tsdb(*args, **kwargs):
    ''' 本地TSDB查缺 '''
    task_id = kwargs.get('task_id', 'NA')
    for i in range(10):
        try:
            df = RSDBInterface.read_windfarm_configuration()[['set_id', 'turbine_id']]
            if len(df)>0:
                break
        except Exception as e:
            _LOGGER.warning(f'update_tsdb: windfarm_configuration 查询失败，稍后重试，错误信息：{str(e)}')
        time.sleep(2)
    if len(df)==0:
        raise ValueError('update_tsdb: windfarm_configuration 查询失败')
    for _, (set_id, turbine_id) in df.iterrows():
        _LOGGER.info(f'update_tsdb: {set_id}, {turbine_id}')
        dtrm = get_dates_tsdb(turbine_id, remote=True) 
        dtlc = get_dates_tsdb(turbine_id, remote=False)
        dts = dtrm[~dtrm.isin(dtlc)]
        for date in dts:
            # 不更新当天数据
            if date==pd.Timestamp.now().date():
                continue
            print(set_id, turbine_id, date)
            try:
                _LOGGER.info(f'task_id={task_id} update_tsdb: {set_id}, {turbine_id}, {date}')
                load_tsdb(set_id, turbine_id, date)
            except:
                _LOGGER.error(f'failed to update_tsdb: {set_id}, {turbine_id}, {date}')
                raise 

@log_it(_LOGGER, True)
def init_tdengine(*args, **kwargs):
    TDFC.init_database()
    
@log_it(_LOGGER, True)
def heart_beat(*args, **kwargs):
     _LOGGER.info('heart_beat')


# #%% main
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()