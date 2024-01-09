
from wtbonline._process.inspector.base import BaseInspector
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise


class HubAzimuthInspector(BaseInspector):
    def _initalize(self):
        self.name = '风轮方位角异常'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id=set_id, turbine_id=turbine_id, start_time=start_time, end_time=end_time)
        return rev
    
    def _stat_tsdb(self, *, set_id, start_time, end_time, turbine_id=None):
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select 
                '{set_id}' as set_id,
                device,
                TIMETRUNCATE(ts, 1d) as date,
                first(ts) as ts
            from 
                {from_clause}
            where 
                (faultcode=30017
                or faultcode=30024) 
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
        rev['value'] = None
        rev['bound'] = None           
        rev['var_name'] =  None
        rev['name'] = None
        return rev[self.columns]