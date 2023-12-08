import pandas as pd

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise
from wtbonline._process.tools import inspector as insp
from wtbonline._process.tools.common import get_dates_tsdb

from wtbonline._logging import log_it
from wtbonline._process.statistics import _LOGGER


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
def udpate_statistic_daily(*args, **kwargs):
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
 
if __name__ == '__main__':
    udpate_statistic_daily()