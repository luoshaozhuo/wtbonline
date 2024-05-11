# author luosz
# created on 10.23.2023

from typing import List, Union
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._process.tools.filter import normal_production

#%% constant
COL_AUG = ['device_id', 'totalfaultbool_mode', 'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'pv_c',
           'workmode_mode', 'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean', 'bin']

#%% class
class PowerCurve(Base):
    '''
    >>> pc = PowerCurve()
    >>> fig = pc.plot(set_id='20625', device_ids=['d10003'], start_time='2023-05-01 00:00:00', end_time='2024-10-01 00:00:00')
    >>> fig.show(renderer='png')
    '''  
    def init(self, var_names=[]):
        ''' 定制的初始化过程 '''
        self.height = 600
        self.var_names = ['winspd_mean', 'var_246_mean']
    
    def get_ytitles(self, set_id):
        return []
    
    def get_title(self, set_id, device_ids, ytitles):
        return '功率曲线'
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]], width=1):
        var_names = make_sure_list(var_names)
        device_ids = make_sure_list(device_ids)
        df = RSDBFacade.read_statistics_sample(
            set_id=set_id,
            device_id=device_ids,
            start_time=start_time,
            end_time=end_time,
            columns = list(set(COL_AUG+var_names)),
            )
        if len(device_ids)!=len(df['device_id'].unique()):
            raise ValueError(f'部分机组查无数据，实际：{df["device_id"].unique().tolist()}，需求：{device_ids}')
        # 正常发电数据
        df = normal_production(df)
        df = df.rename(columns={'winspd_mean':'mean_wind_speed', 'var_246_mean':'mean_power'})
        # 15°空气密度
        df['mean_wind_speed'] = df['mean_wind_speed']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
        wspd = pd.cut(df['mean_wind_speed'],  np.arange(3-width/2.0,26,width))
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        df = df.dropna(subset=['wspd'])
        power_curve = df.groupby(['wspd', 'device_id'])['mean_power'].median().reset_index()
        sample_df = []
        for _, grp in df.groupby('device_id'):
            sample_df.append(grp.sample(self.nsamples) if grp.shape[0]>self.nsamples else grp)
        sample_df = pd.concat(sample_df, ignore_index=True)
        # 读取保证功率曲线
        power_curve_ref = PGFacade.read_model_powercurve_current(set_id=set_id)
        return sample_df, power_curve, power_curve_ref
    
    def build(self, data, ytitles):
        df, power_curve, power_curve_ref = data
        fig = go.Figure()
        colors = px.colors.qualitative.Dark2
        i=0
        for device_id in power_curve['device_id'].unique():
            df_sub = df[df['device_id']==device_id]
            pc_sub = power_curve[power_curve['device_id']==device_id]
            fig.add_trace(
                go.Scatter(
                    x=pc_sub['wspd'],
                    y=pc_sub['mean_power'],
                    line=dict(color=colors[i]),
                    mode='lines',
                    name=device_id,
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=df_sub['mean_wind_speed'],
                    y=df_sub['mean_power'],
                    mode='markers',
                    showlegend=False,
                    marker=dict(opacity=0.3, color=colors[i], size=3),
                    hovertemplate =
                    '<i>mean_power</i>: %{y:.2f}'+
                    '<br><i>mean_wind_speed</i>: %{x:.2f}<br>'+
                    '<b>%{text}</b>',
                    text = [f'datetime: {i}' for i in df['bin']],           
                    )
                )
            i=i+1
        if len(power_curve_ref)>0:
            fig.add_trace(
                go.Scatter(
                    x=power_curve_ref['mean_wind_speed'],
                    y=power_curve_ref['mean_power'],
                    line=dict(color=colors[-1]),
                    mode='lines',
                    name='参考功率曲线',
                    )
                )            
        fig.layout.xaxis.update({'title': '10分钟平均风速 m/s'})
        fig.layout.yaxis.update({'title': '10分钟平均电网有功功率 kW'})
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()