# author luosz
# created on 10.23.2023

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px 

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._plot.classes.base import BaseFigure


class PowerCurve(BaseFigure):
    def _read_data(self, set_id, turbine_id, start_time, end_time):
        df = RSDBInterface.read_statistics_sample(
            set_id=set_id,
            turbine_id=turbine_id,
            start_time=start_time,
            end_time=end_time,
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
        wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        power_curve = df.groupby('wspd')['mean_power'].median().reset_index()
        mean_df = power_curve.groupby('wspd')['mean_power'].median().reset_index()
        df = df.sample(self.samples) if df.shape[0]>self.samples else df
        return df, mean_df
    
    def _initialize(self):
        '''
        >>> fig = PowerCurve({'set_id':'20835', 'map_id':'A01', 'start_time':'2023-05-01', 'end_time':'2023-06-01'})
        >>> fig.plot()
        '''
        fig = go.Figure()
        for i,row in  self.target_df.iterrows():
            color = px.colors.qualitative.Plotly[i]
            df, mean_df = self._read_data(row['set_id'], row['turbine_id'], row['start_time'], row['end_time'])
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
        fig.layout.xaxis.update({'title': '10分钟平均风速 m/s'})
        fig.layout.yaxis.update({'title': '10分钟平均电网有功功率 kW'})
        self._tight_layout(fig)
        
        self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()