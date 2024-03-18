# author luosz
# created on 10.23.2023

from typing import List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._plot.classes.base import Base


class PowerCurve(Base):
    '''
    >>> pc = PowerCurve()
    >>> fig = pc.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-10-01 00:00:00')
    >>> fig.show(renderer='png')
    '''  
    def init(self):
        ''' 定制的初始化过程 '''
        self.height = 600
    
    def get_ytitles(self, set_id):
        return []
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str):
        df = RSDBFacade.read_statistics_sample(
            set_id=set_id,
            device_id=device_ids,
            start_time=start_time,
            end_time=end_time,
            columns = ['turbine_id', 'var_355_mean', 'var_246_mean', 'totalfaultbool_mode',
                    'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'workmode_mode',
                    'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean', 'bin'],
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
        wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        power_curve = df.groupby('wspd')['mean_power'].median().reset_index()
        mean_df = power_curve.groupby('wspd')['mean_power'].median().reset_index()
        df = df.sample(self.samples) if df.shape[0]>self.samples else df
        return df, mean_df
    
    def build(self, df, ytitles):
        fig = go.Figure()
        colors = px.colors.qualitative.Dark2
        i=0
        for device_id, plot_df in df.groupby('device_id'):
            fig.add_trace(
                go.Scatter(
                    x=plot_df['wspd'],
                    y=plot_df['mean_power'],
                    line=dict(color=colors[i]),
                    mode='lines',
                    name=device_id,
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=df['mean_wind_speed'],
                    y=df['mean_power'],
                    mode='markers',
                    showlegend=False,
                    marker=dict(opacity=0.5, color=colors[i]),
                    hovertemplate =
                    '<i>mean_power</i>: %{y:.2f}'+
                    '<br><i>mean_wind_speed</i>: %{x:.2f}<br>'+
                    '<b>%{text}</b>',
                    text = [f'datetime: {i}' for i in df['bin']],           
                    )
                )
        fig.layout.xaxis.update({'title': '10分钟平均风速 m/s'})
        fig.layout.yaxis.update({'title': '10分钟平均电网有功功率 kW'})
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()