
from wtbonline._process.inspector.base import BaseInspector
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise


class OverPowerInspector(BaseInspector):
    def _initalize(self):
        self.name = '发电机发电功率超高'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    # def _stat_tsdb(self, set_id, turbine_id, start_time, end_time):
    def _stat_tsdb(self, set_id, start_time, end_time, turbine_id=None):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='var_246').iloc[0]
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select
                TIMETRUNCATE(ts, 1d) as date,
                first(ts) as `ts`, 
                device,
                var_246 as `value`
            from 
                {from_clause}
            where 
                faultcode=24010 
                and ts > '{start_time}'
                and ts < '{end_time}'
            group by 
                device,
                TIMETRUNCATE(ts, 1d) 
            order by
                device,
                date
        '''
        sql = concise(sql)
        rev = self._standard(set_id, TDFC.query(sql))
        rev['bound'] = row['upper_bound']           
        rev['var_name'] = 'var_246'
        rev['name'] = row['name']
        return rev[self.columns]
