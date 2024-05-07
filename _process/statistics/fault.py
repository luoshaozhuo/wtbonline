           

#%% import
import pandas as pd

from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb.dao import RSDBDAO
from wtbonline._common.utils import make_sure_datetime, make_sure_list
from wtbonline._process.statistics import _LOGGER
from wtbonline._db.config import get_td_remote_restapi
from wtbonline._logging import log_it

#%% constant
RSDB = RSDBDAO()

FAULT_TYPE_DF = RSDBFacade.read_turbine_fault_type().dropna(subset=['type','value'], how='any')
WINDFARM_CONF = RSDBFacade.read_windfarm_configuration().set_index('set_id', drop=False)
TD_DATABASE = get_td_remote_restapi()['database']

#%% fcuntion
def latest_record(device_id):
    '''
    >>> _ = latest_record('s10003')
    '''
    sql = f'''
        select fault_type, max(end_time) as end_time 
        from statistics_fault 
        where device_id='{device_id}'
        group by fault_type
        '''
    df = RSDB.read_sql(sql).set_index('fault_type',drop=False)
    return {row['fault_type']:row['end_time'] for _,row in df.iterrows()}

def read(device_id, fault_type, value, index=None, start_time=None):
    '''
    >>> read('s10003', 'flag', 'true', 'var_23569', '2023-10-10').columns.tolist()
    ['device_id', 'fault_type', 'val', 'begin_tm', 'end_tm']
    >>> read('s10003', 'alarm', [28012, 20051]).shape[0]>1
    True
    >>> read('s10003', 'msg', [16010]).shape[0]>1
    True
    >>> read('s10003', 'fault', 4263).shape[0]>1
    True
    '''
    columns = ['device_id', 'fault_type', 'val', 'begin_tm', 'end_tm']
    if fault_type=='flag':
        assert index is not None, 'fault_type=flag时，index不能为None'
        where = f'where ts>"{make_sure_datetime(start_time)}"' if start_time is not None else ''
        sql_inner = (      
            f'SELECT FIRST(ts) as begin_tm, Last(ts) as end_tm, {make_sure_list(index)[0]} as val '
            f'from {TD_DATABASE}.d_{device_id} '
            f'{where}'
            f'STATE_WINDOW({index}) '
            )
        sql = f'''select * from ({sql_inner}) b where b.val={value}'''
        df = TDFC.query(sql, remote=True)
        df['device_id'] = device_id
        df['val'] = df['val'].astype(bool).astype(str).str.lower()
    else:
        value = value.split(',')
        if fault_type=='msg':
            df = PGFacade.read_data_msg(device_id=device_id, val=value, start_time=start_time)
        elif fault_type=='alarm':
            df = PGFacade.read_data_alarm(device_id=device_id, val=value, start_time=start_time)
        elif fault_type=='fault':
            df = PGFacade.read_data_fault(device_id=device_id, val=value, start_time=start_time)
        else:
            raise ValueError(f'不支持的故障类型{fault_type}')
    df['begin_tm'] = pd.to_datetime(df['begin_tm'])
    df['end_tm'] = pd.to_datetime(df['end_tm'])
    df['fault_type'] = fault_type
    df = df.sort_values('begin_tm')
    return df[columns]

def do_statistic(set_id, device_id):
    '''
    >>> do_statistic('20835', 's10003')
    '''
    tsdb_columns = TDFC.get_filed(set_id=set_id, remote=True)
    dct = latest_record(device_id=device_id)
    is_offshore = WINDFARM_CONF.loc[set_id, 'is_offshore']
    fault_type_subdf = FAULT_TYPE_DF[FAULT_TYPE_DF['is_offshore']==is_offshore]
    df = []
    for _,row in fault_type_subdf.iterrows():
        if row['type']=='flag' and not row['index'] in tsdb_columns:
            continue
        temp = read(
            device_id=device_id, 
            fault_type=row['type'], 
            value=row['value'], 
            index=row['index'],
            start_time=dct.get(row['type'], None)
            )
        if len(temp)<1:
            continue
        temp.insert(0, 'fault_id', row['id'])
        df.append(temp)
    if len(df)<1:
        return
    df = pd.concat(df, ignore_index=True)
    df['set_id'] = set_id
    df['create_time'] = pd.Timestamp.now()
    df.rename(columns={'begin_tm':'start_time', 'end_tm':'end_time', 'val':'value'}, inplace=True)
    df['end_time'] = df['end_time'].where(~df['end_time'].isna(), df['start_time'])
    df.dropna(how='any', inplace=True)
    if df.shape[0]>0:
        RSDBFacade.insert(df, tbname='statistics_fault')

@log_it(_LOGGER)
def udpate_statistic_fault(*args, **kwargs):
    task_id = kwargs.get('task_id', 'NA')
    set_id = kwargs.get('set_id', None)    
    device_df = PGFacade.read_model_device()
    err_msg = []
    for _,row in device_df.iterrows():
        set_id = row['set_id']
        device_id=row['device_id']
        _LOGGER.info(f'task_id={task_id} udpate_statistic_fault: {set_id}, {device_id}')
        try:
            do_statistic(set_id=set_id, device_id=device_id)
        except Exception as e:
            err_msg.append(f'{task_id} {device_id} 故障统计失败 {e}')
            continue
    if len(err_msg)>0:
        raise ValueError('\n'.join(err_msg))
    
    
if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    udpate_statistic_fault()