# author luosz
# created on 10.23.2023

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._plot.classes.base import Base


class BladeOverloaded(Base):
    '''
    >>> bo = BladeOverloaded()
    >>> fig = bo.plot(set_id='20835', device_ids=['s10003', 's10004'], start_time='2023-05-01 00:00:00', end_time='2023-05-01 02:00:00')
    >>> fig.show(renderer='png')
    '''
    def init(self, var_names=[]):
        self.var_names=(
            ['var_18000', 'var_18001', 'var_18002'] +
            ['var_18003', 'var_18004', 'var_18005', 'var_18006'] +
            ['var_18012', 'var_18013', 'var_18014', 'var_18015'] + 
            ['var_101', 'var_102', 'var_103'] +
            ['var_382', 'var_383']
            )
        self.height = 900
        self.width = 900
    
    def build(self, df, ytitles):
        comb = [
            ('摆振弯矩_Nm', ['var_18000', 'var_18001', 'var_18002'], 1, 1), 
            ('挥舞弯矩_Nm', ['var_18003', 'var_18004', 'var_18005'], 1, 2),
            ('实际角度_°', ['var_101', 'var_102', 'var_103'], 2, 1),
            ]
        comb_2 = [
            ('系统波长', ['var_18012', 'var_18013', 'var_18014', 'var_18015'], 2, 2), 
            ('加速度_m/s2', ['var_382', 'var_383'], 3, 1),
            ]
        fig = make_subplots(
            rows=3, 
            cols=2, 
            specs=[
                [{'type' : 'xy'},{'type' : 'xy'}], 
                [{'type' : 'xy'},{'type' : 'xy'}],
                [{'type' : 'xy'},{'type' : 'polar'}]
                ],
            )
        colors = px.colors.qualitative.Plotly
        for device_id, plot_df in df.groupby('device_id'):    
            fig = make_subplots(
                rows=3, 
                cols=2, 
                specs=[
                    [{'type' : 'xy'},{'type' : 'xy'}], 
                    [{'type' : 'xy'},{'type' : 'xy'}],
                    [{'type' : 'xy'},{'type' : 'polar'}]
                    ]
                )
            showlegend = True
            for key_,cols,nrow,ncol in comb:
                for i, column in enumerate(cols):
                    fig.add_trace(
                        go.Scatter(
                            x=plot_df['ts'],
                            y=plot_df[column],
                            mode='lines',
                            opacity=0.5,
                            name=f'叶片{i+1}',
                            showlegend=showlegend,
                            line=dict(color=colors[i])
                            ),
                        row=nrow,
                        col=ncol
                        )
                showlegend=False
                fig.update_xaxes(title_text='时间', row=nrow, col=ncol)
                fig.update_yaxes(title_text=key_, row=nrow, col=ncol)
            # 载荷检测系统波长及振动加速度
            for key_,cols,nrow,ncol in comb_2:
                for i, column in enumerate(cols):
                    fig.add_trace(
                        go.Scatter(
                            x=plot_df['ts'],
                            y=plot_df[column],
                            mode='lines',
                            opacity=0.5,
                            showlegend=False,
                            line=dict(color=colors[i])
                            ),
                        row=nrow,
                        col=ncol
                        )
                fig.update_xaxes(title_text='时间', row=nrow, col=ncol)
                fig.update_yaxes(title_text=key_, row=nrow, col=ncol)
            #极坐标图
            fig.add_trace(
                go.Scatterpolar(
                    theta=plot_df['var_18006'], 
                    r=plot_df['var_18000']-plot_df['var_18000'].mean(), 
                    mode='markers',
                    marker=dict(size=3, opacity=0.5),
                    showlegend=False
                    ),
                row=3,
                col=2
                )
            # 只支持画一组数据
            break
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()