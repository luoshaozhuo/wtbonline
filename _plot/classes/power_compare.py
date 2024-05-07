# author luosz
# created on 10.23.2023

from typing import List, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots
import numpy as np

from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list
from wtbonline._process.tools.filter import normal_production

#%% constants
COL_AUG = [
    'device_id', 'totalfaultbool_mode','totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'workmode_mode',
    'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique', 'pv_c'
    ]
DEVICE_DF = PGFacade.read_model_device().set_index('device_id')

#%% class
class PowerCompare(Base):
    '''
    >>> pc = PowerCompare()
    >>> fig = pc.plot(set_id='20080', device_ids='s10005', start_time='2023-10-01 00:00:00', end_time='2024-04-01 00:00:00')
    >>> fig.show(renderer='png')
    '''  
    def init(self, var_names=[]):
        ''' 定制的初始化过程 '''
        self.var_names = ['var_101_mean', 'var_102_mean', 'var_103_mean', 'var_246_mean', 'var_94_mean', 'var_363_mean']
        self.height = 600
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]]):
        var_names = make_sure_list(var_names)
        df = RSDBFacade.read_statistics_sample(
            set_id=set_id,
            device_id=device_ids,
            start_time=start_time,
            end_time=end_time,
            columns = list(set(COL_AUG+self.var_names)) ,
            )
        assert len(device_ids)==len(df['device_id'].unique()), f'部分机组查无数据，实际：{df["device_id"].unique().tolist()}，需求：{device_ids}'
        # 正常发电数据
        df = normal_production(df, reset_index=True)        
        df.rename(columns={'var_246_mean':'mean_power'}, inplace=True)
        df['mean_pitch_angle'] = df[['var_101_mean', 'var_102_mean', 'var_103_mean']].mean(axis=1)
        gearbox_ratio = RSDBFacade.read_windfarm_configuration(set_id=set_id)['gearbox_ratio'].iloc[0]
        df['rotor_speed'] =  df['var_94_mean']*gearbox_ratio
        df['rotor_torque'] =  df['mean_power']/(df['rotor_speed']*2*np.pi/60)
        return df[['mean_pitch_angle', 'mean_power', 'rotor_speed', 'device_id', 'rotor_torque', 'var_363_mean']]
    
    def get_ytitles(self, set_id):
        return []

    def get_title(self, set_id, device_ids, ytitles):
        if len(device_ids)==1:
            return DEVICE_DF['device_name'].loc[device_ids[0]]
        return '机组功率控制效果'

    def build(self, data, ytitles):
        df = data
        fig = make_subplots(2, 1, shared_xaxes=True, vertical_spacing=0.05)
        fig = make_subplots(
            rows=2, 
            cols=2,
            specs=[[{}, {"rowspan": 2}],[{}, None]],
            )
        
        showlegend = len(df['device_id'].unique())>1
        colors = px.colors.qualitative.Dark2
        i=0
        for device_id, plot_df in df.groupby('device_id'):
            fig.add_trace(
                go.Scatter(
                    x=plot_df['mean_power'],
                    y=plot_df['mean_pitch_angle'],
                    mode='markers',
                    name=device_id,
                    marker=dict(opacity=0.5, color=colors[i], size=3),
                    showlegend=showlegend,
                    ),
                row=1,
                col=1
                ) 
            fig.update_xaxes(title_text='10分钟平均桨距角 °', row=1, col=1)
            fig.update_yaxes(title_text='10分钟平均功率 kWh', row=1, col=1)
            
            fig.add_trace(
                go.Scatter(
                    x=plot_df['rotor_speed'],
                    y=plot_df['rotor_torque'],
                    mode='markers',
                    marker=dict(opacity=0.5, color=colors[i], size=3),
                    showlegend=False,
                    ),
                row=2,
                col=1
                ) 
            fig.update_xaxes(title_text='10分钟平均转速 rpm', row=2, col=1)
            fig.update_yaxes(title_text='10分钟平均叶轮扭矩 kNm', row=2, col=1)
            
            fig.add_trace(
                go.Scatter(
                    x=plot_df['var_363_mean'],
                    y=plot_df['mean_power'],
                    mode='markers',
                    marker=dict(opacity=0.5, color=colors[i], size=3),
                    showlegend=False,
                    ),
                row=1,
                col=2,
                ) 
            fig.update_xaxes(title_text='10分钟平均分向角 °', row=1, col=2)
            fig.update_yaxes(title_text='10分钟平均功率 kWh', row=1, col=2)         
            
            i += 1
        return fig
            
if __name__ == "__main__":
    import doctest
    doctest.testmod()