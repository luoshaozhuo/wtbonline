
from wtbonline._process.inspector.base import BaseInspector
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise


class BladeAsynchronousInspector(BaseInspector):
    def _initalize(self):
        self.name = '叶片桨距角不同步'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id=set_id, turbine_id=turbine_id, start_time=start_time, end_time=end_time)
        return rev

    def _stat_tsdb(self, *, set_id, start_time, end_time, turbine_id=None):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_asynchronous').iloc[0]
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select
                '{set_id}' as set_id,
                device,
                TIMETRUNCATE(ts, 1d) as date,
                first(ts) as `ts`, 
                var_101,
                var_102,
                var_103
            from 
                {from_clause}
            where 
                faultcode=4128 
                and ts>"{start_time}"
                and ts<"{end_time}"
            group by
                device,
                TIMETRUNCATE(ts, 1d)
            order by 
                device,
                date
        '''
        sql = concise(sql)
        rev = self._standard(set_id, TDFC.query(sql, remote=False))
        rev['diff12'] = rev['var_101'] - rev['var_102']
        rev['diff13'] = rev['var_101'] - rev['var_103']
        rev['diff23'] = rev['var_102'] - rev['var_103']
        rev['value'] = rev[['diff12', 'diff13', 'diff23']].max(axis=1)
        rev['bound'] = row['upper_bound']            
        rev['var_name'] =  'blade_edgewise'
        rev['name'] = row['name']
        return rev[self.columns]