           

#%% import
from tkinter import S
from typing import Union
import pandas as pd
import datetime

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._process.tools.common import get_all_table_tags
from wtbonline._process.inspector import INSPECTORS
from wtbonline._common.utils import make_sure_datetime
from wtbonline._logging import log_it
from wtbonline._process.statistics import _LOGGER

_type = Union[str, datetime.date, pd.Timestamp]

@log_it(_LOGGER, True)
def udpate_statistic_fault(*args, **kwargs):
    '''
    所有统计均在本地tdengine内进行
    '''
    task_id = kwargs.get('task_id', 'NA')
    set_id = kwargs.get('set_id', None)
    start_time = kwargs.get('start_time', None)
    if not start_time in [None, '']:
        start_time = pd.to_datetime(start_time)
    end_time = kwargs.get('end_time', None)
    if not end_time in [None, '']:
        end_time = pd.to_datetime(end_time)
    else:
        end = pd.to_datetime((pd.Timestamp.now()-pd.Timedelta('1d')))

    # 获取所有set_id, turbine_id组合
    candidate_df = get_all_table_tags(set_id=set_id)
    if len(INSPECTORS)<1:
        return
    
    replace_dct = RSDBInterface.read_turbine_fault_type()
    replace_dct = {row['name']:str(row['id']) for _,row in replace_dct.iterrows()}
    
    table_columns = ['set_id', 'turbine_id', 'date', 'timestamp', 'fault_id', 'create_time']
    columns = ['set_id', 'turbine_id', 'timestamp', 'type']
    sql_tsdb = f"select first(ts) as ts from d_%s"
    sql_rsdb = "select max(date) as date from statistics_fault where turbine_id='%s'"
    for _, (set_id, turbine_id) in candidate_df[['set_id','device']].iterrows():  
        # 从statistics_fault最后一条记录的起始时间开始搜索，若没有记录，从头搜索
        start = start_time
        if start in (None, ''):
            try:
                sql = sql_rsdb%turbine_id
                start = RSDB.read_sql(sql_rsdb%turbine_id)['date'].iloc[0]
                if start is not None:
                    start = pd.to_datetime(start) + pd.Timedelta('1d')
                else:
                    sql = sql_tsdb%turbine_id
                    start = TDFC.query(sql)['ts'].iloc[0]
            except Exception as e:
                _LOGGER.error(f'task_id={task_id} 无法从statistics_fault或windfarm确定{set_id} {turbine_id}的数据记录开始时间, {sql}, {e}')
                continue
            
        # 无论start_time以及end_time是否指定时间，都是按天统计
        ranges = pd.date_range(start=start.date(), end=end.date(), freq='1D')
        for d_start in ranges:
            d_end = d_start + pd.Timedelta('1d')            
            _LOGGER.info(f'task_id={task_id} 故障统计 {set_id} {turbine_id} {d_start} - {d_end}')
            
            df = []
            for i in INSPECTORS:
                inspector = INSPECTORS[i]
                try:
                    temp = inspector.inspect(set_id=set_id, turbine_id=turbine_id, start_time=d_start, end_time=d_end)
                except Exception as e:
                    _LOGGER.error(f'task_id={task_id} 统计数据失败{set_id} {turbine_id} {d_start}-{d_end} \n {e}')
                    raise
                    continue
                if temp.shape[0]>0:
                    temp['type'] = inspector.name
                    temp.rename(columns={'ts':'timestamp'}, inplace=True)
                    df += temp[columns].to_dict('split')['data'] 
                del temp         
            if len(df)<1:
                continue
            df = pd.DataFrame(df, columns=columns)
            # 先repalce成str，再转int，否则会有future warning
            df['fault_id'] = df['type'].replace(replace_dct).astype(int)
            df['date'] = d_start
            df.sort_values('timestamp', inplace=True)
            df.drop_duplicates(['date', 'fault_id'], keep='first', inplace=True)
            df['create_time'] = pd.Timestamp.now()
            try:
                RSDBInterface.insert(df[table_columns], 'statistics_fault')
            except Exception as e:
                _LOGGER.error(f'task_id={task_id} 入库失败{set_id} {turbine_id}  {d_start} - {d_end} \n {e}')
                continue

if __name__ == '__main__':
    # udpate_statistic_fault()
    udpate_statistic_fault(end_time=None, delta=20, size=3000, minimum=20, task_id='2024-03-03-513867')