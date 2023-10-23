from typing import Union, List, Any
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px 

from wtbonline._db.rsdb_interface import RSDBInterface


class BaseFigure():     
    def __init__(self):
        self.fig = None
    
    def initialize(self):
        raise NotImplemented() 
    
    def standard(self, set_id, df):
        ''' 按需增加turbine_id、测点名称、设备编号 '''
        cols = ['map_id', 'turbine_id']
        conf_df = RSDBInterface.read_windfarm_configuration(set_id=set_id, columns=cols)
        df = pd.merge(df, conf_df, how='inner')
        return df 
    
    def check(self, target_df):
        if not isinstance(target_df, (pd.DataFrame, dict)) :
            raise ValueError('target_df必须是DataFrame或dict')
        if isinstance(target_df, dict):
            try:
                target_df = pd.DataFrame(target_df)
            except:
                target_df = pd.DataFrame(target_df, index=[0])
        target_df = target_df.rename(columns={
            '机型编号':'set_id',
            '风机编号':'map_id',
            '开始日期':'start_time',
            '结束日期':'end_time',
            'deive':'turbine_id',
            '图例号':'name'
            })
        cols_compulsory = pd.Series(['set_id', 'start_time', 'end_time'])
        cols_optional = pd.Series(['turbine_id', 'map_id'])
        if not cols_compulsory.isin(target_df).all():
            raise ValueError(f'target_df必须包含如下字段：{cols_compulsory}')
        if not cols_optional.isin(target_df).any():
            raise ValueError(f'target_df必须包含如下字段中的一个：{cols_optional}')
        
        ret = []
        for set_id,grp in target_df.groupby('set_id'):
            ret.append(self.standard(set_id, grp))
        ret = pd.concat(ret, ignore_index=True)
        if ret.shape[0]<1:
            raise ValueError('target_df经过标准化处理后为空')
        
        if 'name' not in ret.columns:
            ret.insert(0, 'name', ret['turbine_id'])
        
        return ret
    
    def construct(self):
        raise NotImplemented()    
    
    def plot(self, renderer=None):
        if self.fig is not None:
            self.fig.show(renderer=renderer)
        
    def tight_layout(self, fig):
        fig.update_layout(
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1)
            )

class PowerCurve(BaseFigure):
    def __init__(self, target_df=None):
        if target_df is not None:
            self.initialize(target_df)
    
    def read_data(self, set_id, turbine_id, start_date, end_date):
        df = RSDBInterface.read_statistics_sample(
            set_id=set_id,
            turbine_id=turbine_id,
            start_time=start_date,
            end_time=end_date,
            columns = ['turbine_id', 'var_355_mean', 'var_246_mean', 'totalfaultbool_mode',
                    'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'workmode_mode',
                    'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean'],
            )
        # 正常发电数据
        df = df[
            (df['totalfaultbool_mode']=='False') &
            (df['totalfaultbool_nunique']==1) &
            (df['ongrid_mode']=='True') & 
            (df['ongrid_nunique']==1) & 
            (df['limitpowbool_mode']=='False') &
            (df['limitpowbool_nunique']==1) &
            (df['workmode_mode']=='32') &
            (df['workmode_nunique']==1) 
            ]
        df.rename(columns={'var_355_mean':'mean_wind_speed', 'var_246_mean':'mean_power'}, inplace=True)
        # 15°空气密度
        df['mean_wind_speed'] = df['mean_wind_speed']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
        return df[['mean_wind_speed', 'mean_power']]
    
    def initialize(self, target_df:Union[pd.DataFrame, dict]):
        '''
        Arguments:
            target_df -- 
                包含四个字段：set_id, turbine_id, start_date, end_date，如果是list，按此顺序排序
                皮如果，[[set_id, turbine_id, start_date, end_date，]...]
        >>> fig = PowerCurve({'set_id':'20835', 'map_id':'A01', 'start_time':'2023-05-01', 'end_time':'2023-06-01'})
        >>> fig.plot()
        '''
        fig = go.Figure()
        target_df = self.check(target_df)
        for i,row in  target_df.iterrows():
            color = px.colors.qualitative.Plotly[i]
            df = self.read_data(row['set_id'], row['turbine_id'], row['start_time'], row['end_time'])
            wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
            df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
            power_curve = df.groupby('wspd')['mean_power'].median().reset_index()
            mean_df = power_curve.groupby('wspd')['mean_power'].median().reset_index()
            df = df.sample(5000) if df.shape[0]>5000 else df
            fig.add_trace(
                go.Scatter(
                    x=mean_df['wspd'],
                    y=mean_df['mean_power'],
                    line=dict(color=color),
                    mode='lines',
                    name=row['name']
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=df['mean_wind_speed'],
                    y=df['mean_power'],
                    mode='markers',
                    name=row['name'],
                    marker=dict(opacity=0.1, color=color)
                    )
                ) 
        fig.layout.xaxis.update({'title': '风速 m/s'})
        fig.layout.yaxis.update({'title': '功率 kW'})
        self.tight_layout(fig)
        self.fig = fig
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()