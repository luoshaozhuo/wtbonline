           

#%% import
import pandas as pd
import inspect

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._process.tools.common import get_all_table_tags
from wtbonline._process.tools import inspector as insp

from wtbonline._logging import log_it
from wtbonline._process.statistics import _LOGGER

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
        # 从statistics_fault最后一条记录的起始时间开始搜索，若没有记录，从头搜索
        _LOGGER.info(f'故障统计 {set_id} {turbine_id}')
        start_time = RSDB.read_sql(sql_rsdb%turbine_id)['date'].iloc[0]
        try:
            if start_time is not None:
                start_time = pd.to_datetime(pd.to_datetime(start_time).date()) + pd.Timedelta('1d')
            else:
                start_time = TDFC.query(sql_tsdb%turbine_id)['ts'].iloc[0]
        except Exception as e:
            _LOGGER.error(f'无法确定{set_id} {turbine_id}的数据记录开始时间, {e}')
            continue
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
        try:
            RSDBInterface.insert(df[table_columns], 'statistics_fault')
        except Exception as e:
            _LOGGER.error(f'入库失败{set_id} {turbine_id}, {e}')
        
if __name__ == '__main__':
    udpate_statistic_fault()