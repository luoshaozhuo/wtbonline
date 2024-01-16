import pandas as pd

from wtbonline._process.inspector.base import BaseInspector
from wtbonline._process.tools.common import concise
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.rsdb_interface import RSDBInterface

class BladeEdgewiseOverLoadedInspector(BaseInspector):
    '''
    >>> BladeEdgewiseOverLoadedInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    
    def _initalize(self):
        self.name = '叶根摆振弯矩超限'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_edgewise(set_id, turbine_id, start_time, end_time)
        return rev
    
    def _stat_edgewise(self, set_id, turbine_id, start_time, end_time):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_edgewise').iloc[0]
        bound = row.loc['upper_bound']
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select 
                TIMETRUNCATE(ts, 1d) as date,     
                ts,
                '{set_id}' as set_id,
                device,
                max(torque) as `value`
            from
                (
                    select
                        ts,
                        device,
                        CASE 
                            WHEN (CASE WHEN x < y THEN y ELSE x END) < z
                            THEN z
                            ELSE (CASE WHEN x < y THEN y ELSE x END)
                            END AS `torque`
                    from
                        (
                            select
                                ts,
                                device,
                                abs(var_18000) as x,
                                abs(var_18001) as y,
                                abs(var_18002) as z
                            from 
                                {from_clause}      
                            where 
                                ongrid=1
                                and workmode=32
                                and ts>='{start_time}'
                                and ts<'{end_time}'        
                            )
                    )
            where
                torque > {bound}
            group by
                device,
                TIMETRUNCATE(ts, 1d)
            order by
                device,
                date
            ''' 
        sql = concise(sql)
        rev = self._standard(set_id, TDFC.query(sql, remote=False))
        if rev.shape[0]>0:
            rev['var_name'] =  'blade_edgewise'
            rev['bound'] = bound
            rev['name'] = row['name']
        else:
            rev = pd.DataFrame(columns=self.columns)
        return rev[self.columns]
