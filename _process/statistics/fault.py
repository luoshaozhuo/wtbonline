           

#%% import
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
    task_id = kwargs.get('task_id', 'NA')
    start_time = kwargs.get('start_time', None)
    end_time = kwargs.get('end_time', None)

    candidate_df = get_all_table_tags()
    if len(INSPECTORS)<1:
        return
    replace_dct = RSDBInterface.read_turbine_fault_type()
    replace_dct = {row['name']:row['id'] for _,row in replace_dct.iterrows()}
    
    table_columns = ['set_id', 'turbine_id', 'date', 'timestamp', 'fault_id', 'create_time']
    columns = ['set_id', 'turbine_id', 'timestamp', 'type']
    sql_tsdb = f"select first(ts) as ts from d_%s"
    sql_rsdb = "select max(date) as date from statistics_fault where turbine_id='%s'"
    for _, (set_id, turbine_id) in candidate_df[['set_id','device']].iterrows():  
        # 从statistics_fault最后一条记录的起始时间开始搜索，若没有记录，从头搜索
        _LOGGER.info(f'task_id={task_id} 故障统计 {set_id} {turbine_id}')
        if start_time is None:
            start_time = RSDB.read_sql(sql_rsdb%turbine_id)['date'].iloc[0]
            try:
                if start_time is not None:
                    start_time = pd.to_datetime(pd.to_datetime(start_time).date()) + pd.Timedelta('1d')
                else:
                    start_time = TDFC.query(sql_tsdb%turbine_id)['ts'].iloc[0]
            except Exception as e:
                _LOGGER.error(f'task_id={task_id} 无法确定{set_id} {turbine_id}的数据记录开始时间, {e}')
                continue
        
        if end_time is None:
            end_time = pd.to_datetime((pd.Timestamp.now()-pd.Timedelta('1d')).date())
        
        df = []    
        for i in INSPECTORS:
            inspector = INSPECTORS[i]
            try:
                temp = inspector.inspect(set_id, turbine_id, start_time, end_time)
            except Exception as e:
                _LOGGER.error(f'task_id={task_id} 统计数据失败{set_id} {turbine_id}, {e}')
                continue
            if temp.shape[0]>0:
                temp['type'] = inspector.name
                temp.rename(columns={'ts':'timestamp'}, inplace=True)
                df += temp[columns].to_dict('split')['data'] 
            del temp         
        if len(df)<1:
            continue
        
        df = pd.DataFrame(df, columns=columns)
        df['fault_id'] = df['type'].replace(replace_dct)
        df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        df.sort_values('timestamp', inplace=True)
        df.drop_duplicates(['date', 'fault_id'], keep='first', inplace=True)
        df['create_time'] = pd.Timestamp.now()
        try:
            RSDBInterface.insert(df[table_columns], 'statistics_fault')
        except Exception as e:
            _LOGGER.error(f'task_id={task_id} 入库失败{set_id} {turbine_id}, {e}')
            continue

if __name__ == '__main__':
    udpate_statistic_fault()