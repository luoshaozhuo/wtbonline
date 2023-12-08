from itertools import product
import pandas as pd

from wtbonline._process.inspector.base import BaseInspector
from wtbonline._process.tools.common import make_sure_list, concise
from wtbonline._db.tsdb_facade import TDFC


class BladeUnbalanceLoadInspector(BaseInspector):
    '''
    >>> BladeUnbalanceLoadInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    
    def _initalize(self):
        self.vars_bound = ['blade_flapwise_diff', 'blade_edgewise_diff']
        self.name = '叶根载荷不平衡'
    
    def _stat_tsdb(self, set_id, start_time, end_time, turbine_id=None):
        devices = make_sure_list(turbine_id)
        if len(devices)<1:
            sql = f'SHOW TABLE TAGS FROM s_{set_id}'
            devices = TDFC.query(sql)['device']
        
        cols = ['var_18000', 'var_18001', 'var_18002',  'var_18003',  'var_18004',  'var_18005', 'workmode']
        vars = [f'{f}({v}) as `{v}_{f}`' for v, f in product(cols, ['avg'])]
        vars += ['min(cast(ongrid AS INT)) as ongrid']
        raw_df = []
        for turbine_id in devices:
            sql = f'''
                select 
                    a.ts,
                    abs(a.var_18000_avg-a.var_18001_avg) as `blade_edgewise_diff12`,
                    abs(a.var_18000_avg-a.var_18002_avg) as `blade_edgewise_diff13`,
                    abs(a.var_18001_avg-a.var_18002_avg) as `blade_edgewise_diff23`,
                    abs(a.var_18003_avg-a.var_18004_avg) as `blade_flapwise_diff12`,
                    abs(a.var_18003_avg-a.var_18005_avg) as `blade_flapwise_diff13`,
                    abs(a.var_18004_avg-a.var_18005_avg) as `blade_flapwise_diff23`
                from
                    (
                        select
                            last(ts) as ts, 
                            count(ts) as cnt, 
                            {', '.join(vars)} 
                        from 
                            d_{turbine_id} 
                        where 
                            ts>='{start_time}' 
                            and ts<'{end_time}'
                        INTERVAL(3m)
                        SLIDING(1m)
                    ) a
                where
                    a.cnt>150
                    and a.workmode_avg=32
                    and a.ongrid=1
                '''
            sql = concise(sql)
            df = self._standard(set_id, TDFC.query(sql, remote=False))

            df['blade_edgewise_diff_max'] = df[['blade_edgewise_diff12', 'blade_edgewise_diff13', 'blade_edgewise_diff23']].max(axis=1)
            df['blade_flapwise_diff_max'] = df[['blade_flapwise_diff12', 'blade_flapwise_diff13', 'blade_flapwise_diff23']].max(axis=1)
            
            df['date'] = df['ts'].dt.date
            df = df.melt(
                    id_vars=['date', 'ts'], 
                    value_vars=['blade_edgewise_diff_max', 'blade_flapwise_diff_max'], 
                    var_name='variable', 
                    value_name='value'
                    )
            indexs = df.groupby(['date', 'variable'])[['value']].idxmax().squeeze()
            df['device'] = turbine_id
            df = df.loc[indexs]
            raw_df.append(df)
        raw_df = pd.concat(raw_df, ignore_index=True)
        if raw_df.shape[0]>0:
            raw_df['var_name'] = raw_df['variable'].str.rsplit('_', n=1, expand=True).iloc[:,0]
        raw_df = self._standard(set_id, raw_df)
        return raw_df