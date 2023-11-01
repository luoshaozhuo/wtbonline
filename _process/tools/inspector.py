from sys import set_int_max_str_digits
import pandas as pd
from itertools import product
from typing import Union
from datetime import date

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import make_sure_list, concise


class BaseInspector():
    def __init__(self):
        # 故障统计字段名
        self.var_names = []
        # 故障统计字段名对应的限值表内的字段名
        self.vars_bound = []
        # 统计函数
        self.funcs = []
        self.sliding = None
        self.interval = None
        # 故障名
        self.name = None
        # 输出字段名
        self.columns = ['map_id', 'turbine_id', 'device', 'date', 'ts', 'var_name', 'name', 'value', 'bound']
        self._initalize()
    
    def _initalize(self):
        raise NotImplementedError()
    
    def inspect(self, set_id:str, turbine_id:str, start_time:Union[str, date], end_time:Union[str, date]):
        ''' 在指定日期内探寻有发生故障的日期 '''
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)
        return self._inspect(set_id, turbine_id, start_time, end_time)
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=self.vars_bound)
        raw_df = self._stat_tsdb(set_id, start_time, end_time, turbine_id=turbine_id)
        rev = self._exceed(raw_df, bound_df)
        rev['set_id'] = set_id
        return rev    
    
    def _exceed(self, raw_df, bound_df):
        ''' 判断是否超限 '''     
        if raw_df.shape[0]<1:
            return pd.DataFrame(columns=self.columns)
        
        bound_df = bound_df.rename(columns={'lower_bound':'_min', 'upper_bound':'_max'})
        value_vars = bound_df.filter(axis=1, regex='.*_(max|min)$').columns
        id_vars = bound_df.columns[~bound_df.columns.isin(value_vars)]
        bound_melt = bound_df.melt(id_vars, value_vars, value_name='bound')
        bound_melt['variable'] = bound_melt['var_name']+bound_melt['variable']
        
        rev = pd.merge(raw_df, bound_melt[['variable', 'name', 'bound']], how='inner', on='variable')
        idxs = []
        temp = rev[rev['variable'].str.match('.*_max')].index
        if len(temp)>0:
            sub = rev.loc[temp]
            idxs += sub[sub['value']>sub['bound']].index.tolist()    
        temp = rev[rev['variable'].str.match('.*min')].index
        if len(temp)>0:
            sub = rev.loc[temp]
            idxs += sub[sub['value']<sub['bound']].index.tolist()     
        rev = rev.iloc[idxs]
        if rev.shape[0]>0: 
            rev = rev.sort_values('map_id').reset_index(drop=True)
        return rev[self.columns]
    
    def _condition_normal(self):
        ''' 并网，发电，无故障 '''
        return f'''
            and ongrid=1
            and workmode=32
            and faultcode=0
            '''
            
    def _condition(self):
        return self._condition_normal()
    
    
    def _stat_tsdb(self, set_id, start_time, end_time, turbine_id=None):
        ''' 在tsdb上执行统计计算 
        returns, pd.DataFrame, 'device', 'date', 'dt', 'variable', 'name', 'var_name'
        '''
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = []
        for col,func in product(self.var_names, self.funcs):
            temp = f'''
                select 
                    device, 
                    ts,
                    TIMETRUNCATE(ts, 1d) as date,
                    '{col}' as `var_name`,
                    '{col}_{func}' as `variable`,
                    {func}({col}) as `value`
                from
                    {from_clause}
                where
                    ts>='{start_time}'
                    and ts<'{end_time}'
                    {self._condition()}
                group by 
                    device,
                    TIMETRUNCATE(ts, 1d)
                '''
            if self.interval is not None:
                temp += f' interval({self.interval})'
                if self.sliding is not None:
                    temp += f' sliding({self.sliding})'
            temp = concise(temp)
            sql.append(temp)
        sql = ' UNION ALL '.join(sql)
        sql = concise(sql)
        df = self._standard(set_id, TDFC.query(sql, remote=False))
        return df

    def _standard(self, set_id, df):
        ''' 按需增加turbine_id、测点名称、设备编号 '''
        df = df.copy()
        if 'var_name' in df.columns and ('测点名称' not in df.columns) :
            point_df = RSDBInterface.read_turbine_model_point(set_id=set_id)
            dct = {row['var_name']:row['point_name'] for _,row in point_df.iterrows()}
            df.insert(0, 'point_name', df['var_name'].replace(dct))
        if 'device' in df.columns and  ('turbine_id' not in df.columns):
            df.insert(0, 'turbine_id', df['device'])    
        if 'turbine_id' in df.columns and ('map_id' not in df.columns):
            conf_df = RSDBInterface.read_windfarm_configuration(set_id=set_id)
            dct = {row['turbine_id']:row['map_id'] for _,row in conf_df.iterrows()}
            df.insert(0, 'map_id', df['turbine_id'].replace(dct))  
        return df 

class GearBoxInspector(BaseInspector):
    '''
    >>> GearBoxInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    def _initalize(self):
        self.var_names = ['var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '齿轮箱关键参数超限'
        
class MainBearingInspector(BaseInspector):
    def _initalize(self):
        self.var_names = ['var_171', 'var_172', 'abs(var_171-var_172)']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '主轴承关键参数超限'

class GeneratorInspector(BaseInspector):
    def _initalize(self):
        self.var_names = ['var_206', 'var_207', 'var_208', 'var_209', 'var_210', 'var_211']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '发电机关键参数超限'

class ConvertorInspector(BaseInspector):
    '''
    >>> ConvertorInspector().inspect('20835', 's10001', '2023-08-01', '2023-09-01')
    '''
    def _initalize(self):
        self.var_names = ['var_15004', 'var_15005', 'var_15006', 'var_12016']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '变流器关键参数超限'   

df = ConvertorInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
pass

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

class BladeEdgewiseOverLoadedInspector(BaseInspector):
    '''
    >>> BladeEdgewiseOverLoadedInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    
    def _initalize(self):
        self.name = '叶根摆振弯矩超限'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_edgewise(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_edgewise(self, set_id, turbine_id, start_time, end_time):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_edgewise').iloc[0]
        bound = row.loc['upper_bound']*0.1
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select 
                TIMETRUNCATE(ts, 1d) as date,     
                ts,
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
        rev = self._standard(set_id, TDFC.query(sql))
        rev['var_name'] =  'blade_edgewise'
        rev['bound'] = bound
        rev['name'] = row['name']
        return rev[self.columns]


class BladeFlapwiseOverLoadedInspector(BaseInspector):
    '''
    >>> BladeFlapwiseOverLoadedInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    
    def _initalize(self):
        self.name = '叶根摆挥舞矩超限'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_flapwise(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_flapwise(self, set_id, turbine_id, start_time, end_time):
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_flapwise').iloc[0]
        sql = f'''
            select 
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
        rev['value'] = rev[['var_18003', 'var_18004', 'var_18005']].max(axis=1)
        rev['bound'] = row['upper_bound']
        idxs = rev[rev['faultcode']=='30018'].index
        rev.loc[idxs, 'value'] = rev.loc[idxs, ['var_18003', 'var_18004', 'var_18005']].min(axis=1)
        rev.loc[idxs, 'bound'] = row['lower_bound']
            
        rev['var_name'] =  'blade_edgewise'
        rev['name'] = row['name']
        return rev[self.columns]


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


class BladeAsynchronousInspector(BaseInspector):
    def _initalize(self):
        self.name = '叶片桨距角不同步'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_tsdb(self, set_id, turbine_id, start_time, end_time):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='blade_asynchronous').iloc[0]
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select 
                device,
                TIMETRUNCATE(ts, 1d) as date,
                last(ts) as `ts`, 
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
        rev = self._standard(set_id, TDFC.query(sql))
        rev['diff12'] = rev['var_101'] - rev['var_102']
        rev['diff13'] = rev['var_101'] - rev['var_103']
        rev['diff23'] = rev['var_102'] - rev['var_103']
        rev['value'] = rev[['diff12', 'diff13', 'diff23']].max(axis=1)
        rev['bound'] = row['upper_bound']            
        rev['var_name'] =  'blade_edgewise'
        rev['name'] = row['name']
        return rev[self.columns]
    

class HubAzimuthInspector(BaseInspector):
    def _initalize(self):
        self.name = '风轮方位角异常'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_tsdb(self, set_id, turbine_id, start_time, end_time):
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select 
                device,
                TIMETRUNCATE(ts, 1d) as date,
                last(ts) as ts
            from 
                {from_clause}
            where 
                (faultcode=30014
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


class OverPowerInspector(BaseInspector):
    def _initalize(self):
        self.name = '发电机发电功率超高'
    
    def _inspect(self, set_id, turbine_id, start_time, end_time):
        rev = self._stat_tsdb(set_id, turbine_id, start_time, end_time)
        rev.insert(0, 'set_id', set_id)
        return rev
    
    def _stat_tsdb(self, set_id, turbine_id, start_time, end_time):
        row = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name='var_246').iloc[0]
        from_clause = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select
                TIMETRUNCATE(ts, 1d) as date,
                last(ts) as `ts`, 
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


def inpector_fatory(name):
    dct = {'gearbox':GearBoxInspector,
           'mainbreaing':MainBearingInspector,
           'generator':GeneratorInspector,
           'convertor':ConvertorInspector,
           'blade_unbalance_load':BladeUnbalanceLoadInspector,
           'blade_asynchronous':BladeAsynchronousInspector,
           'blade_edgewise_overloaded':BladeEdgewiseOverLoadedInspector,
           'blade_flapwise_overloaded':BladeFlapwiseOverLoadedInspector,
           'blade_pitchkick':BladePitchkickInspector,
           'hub_azimuth':HubAzimuthInspector,
           'over_power':OverPowerInspector}
    rev = getattr(dct, name, None)
    if rev is None:
        raise ValueError(f'inspector {name} not defined. available inspector are, {", ".join(dct.keys())}')
    return rev