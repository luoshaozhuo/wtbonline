import pandas as pd
from itertools import product
from typing import Union
from datetime import date

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise

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