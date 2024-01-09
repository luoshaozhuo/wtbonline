import pandas as pd

from wtbonline._process.inspector.base import BaseInspector
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise


class BladeFlapwiseOverLoadedInspector(BaseInspector):
    '''
    >>> BladeFlapwiseOverLoadedInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    
    def _initalize(self):
        self.name = '叶根摆挥舞矩超限'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_flapwise(set_id, turbine_id, start_time, end_time)
        return rev
    
    def _stat_flapwise(self, set_id, turbine_id, start_time, end_time):
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_flapwise').iloc[0]
        sql = f'''
            select 
                '{set_id}' as set_id,
                device,
                TIMETRUNCATE(ts, 1d) as date,
                last(ts) as `ts`, 
                var_18003,
                var_18004,
                var_18005,
                faultcode
            from 
                {from_clause} 
            where 
                (faultCode=30011
                or faultCode=30018)
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
        rev = self._standard(set_id, TDFC.query(sql))
        if rev.shape[0]>0:
            rev['value'] = rev[['var_18003', 'var_18004', 'var_18005']].max(axis=1)
            rev['bound'] = row['upper_bound']
            idxs = rev[rev['faultcode']=='30018'].index
            rev.loc[idxs, 'value'] = rev.loc[idxs, ['var_18003', 'var_18004', 'var_18005']].min(axis=1)
            rev.loc[idxs, 'bound'] = row['lower_bound']

            rev['var_name'] =  'blade_edgewise'
            rev['name'] = row['name']
        else:
            rev = pd.DataFrame(columns=self.columns)
        return rev[self.columns]
