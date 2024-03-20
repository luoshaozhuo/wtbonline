# author luosz
# created on 10.23.2023

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot.classes.base import Base
from wtbonline._process.tools.frequency import power_spectrum
from wtbonline._plot.functions import power_spectrum


class BladeUnblacedLoad(Base):
    '''
    >>> bu = BladeUnblacedLoad()
    >>> fig = bu.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''
    def init(self, var_names=[]):
        self.var_names = ['var_382', 'var_18000', 'var_18001', 'var_18002', 'var_18003', 'var_18004', 'var_18005', 'var_18008', 'var_18009', 'var_18010', 'var_18011']
        self.height = 900
        self.width = 900
    
    def build(self, df, ytitles):
        comb = [
            ('摆振', ['var_18000', 'var_18001', 'var_18002']), 
            ('挥舞', ['var_18003', 'var_18004', 'var_18005'])
            ]
        colors = px.colors.qualitative.Dark2 
        for device_id, plot_df in df.groupby('device_id'):
            showlegend = True
            fig = make_subplots(3, 2)
            nrow=1
            for key_,var_names in comb:
                for i, var_name in enumerate(var_names):
                    fig.add_trace(
                        go.Scatter(
                            x=plot_df['ts'],
                            y=plot_df[var_name],
                            mode='lines',
                            opacity=0.5,
                            name=f'叶片{i+1}',
                            showlegend=showlegend,
                            line=dict(color=colors[i])
                            ),
                        row=nrow,
                        col=1
                        )
                    mean_sr = plot_df.set_index('ts')[var_name].rolling('180s').mean()
                    fig.add_trace(
                        go.Scatter(
                            x=mean_sr.index.tolist(),
                            y=mean_sr.values,
                            mode='lines',
                            opacity=0.5,
                            showlegend=False,
                            line=dict(color=colors[i])
                            ),
                        row=nrow,
                        col=2
                        ) 
                    fig.update_xaxes(title_text='时间', row=nrow, col=1)
                    fig.update_xaxes(title_text='时间', row=nrow, col=2)
                    fig.update_yaxes(title_text=f'{key_}弯矩_瞬时 Nm', row=nrow, col=1) 
                    fig.update_yaxes(title_text=f'{key_}弯矩_180s时均 Nm', row=nrow, col=2) 
                showlegend = False
                nrow+=1
            # 机舱加速度x向功率谱
            var_name = 'var_382'
            fft_df = power_spectrum(plot_df[var_name], sample_spacing=1)
            fft_df = fft_df[fft_df['freq']>=0]
            fig.add_trace(
                go.Scatter(
                    x=fft_df['freq'],
                    y=fft_df['amp'],
                    mode='lines',
                    showlegend=False,
                    line=dict(color=colors[3])
                    ),
                row=nrow,
                col=1
                )
            fig.update_xaxes(title_text='Hz', row=3, col=1)
            fig.update_yaxes(title_text=ytitles[var_name]+'**2', row=3, col=1)
            # 载荷检测系统波长
            cols = ['var_18008', 'var_18009', 'var_18010', 'var_18011']
            for i, col in enumerate(cols):
                fig.add_trace(
                    go.Scatter(
                        x=plot_df['ts'],
                        y=plot_df[col],
                        mode='lines',
                        opacity=0.5,
                        name=f'系统波长{i+1}',
                        line=dict(color=colors[4+i])
                        ),
                    row=nrow,
                    col=2
                    )
            fig.update_xaxes(title_text='时间', row=3, col=2)
            fig.update_yaxes(title_text='系统波长', row=3, col=2)          
            break
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()