
import pandas as pd

from wtbonline._process.inspector.base import BaseInspector
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise


class BladePitchkickInspector(BaseInspector):
    def _initalize(self):
        self.name = '叶片pitchkick'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_tsdb(self, set_id, turbine_id, start_time, end_time):
        st = start_time
        rev = []
        while True:
            sql = f'''
                select 
                    device,
                    ts
                from
                    {f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'}
                where 
                    var_23569='true'
                    and ts>'{st}'
                    and ts<'{end_time}'
                '''
            sql =concise(sql)
            df = TDFC.query(sql, remote=True)
            if df.shape[0]>0:
                rev.append(df)
            if df.shape[0]<10000:
                break
            st = rev[-1]['ts'].max()
        if len(rev)>0:
            rev = pd.concat(rev, ignore_index=True)
            rev['date'] = rev['ts'].dt.date
            rev = rev.groupby(['device', 'date'])['ts'].last().reset_index()
            rev = self._standard(set_id, rev)
            rev['value'] = 'True'
            rev['bound'] = 'True'  
            rev['var_name'] =  'pitchkick'
            rev['name'] = 'pitchkick'
            rev = rev[self.columns]
        else:
            rev = pd.DataFrame(columns=self.columns)
        return rev

