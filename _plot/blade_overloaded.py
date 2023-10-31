# author luosz
# created on 10.23.2023

from ast import pattern
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._plot.base import BaseFigure


class BladeOverloaded(BaseFigure):
    def _initialize(self):
        '''
        >>> bo = BladeOverloaded({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> bo.plot()
        '''
        comb = [
            ('摆振弯矩_Nm', ['var_18000', 'var_18001', 'var_18002'], 1, 1), 
            ('挥舞弯矩_Nm', ['var_18003', 'var_18004', 'var_18005'], 1, 2),
            ('实际角度_°', ['var_101', 'var_102', 'var_103'], 2, 1),
            ]
        comb_2 = [
            ('系统波长', ['var_18012', 'var_18013', 'var_18014', 'var_18015'], 2, 2), 
            ('加速度_m/s2', ['var_382', 'var_383'], 3, 1),
            ]
        var_names=[
            'ts', 'var_101', 'var_102', 'var_103', 'var_382', 'var_383', 'var_23507',
            'var_18000', 'var_18001', 'var_18002', 'var_18003', 'var_18004', 'var_18005',
            'var_18012', 'var_18013', 'var_18014', 'var_18015', 'var_18006']
        colors = px.colors.qualitative.Plotly
        for _,entity in  self.target_df.iterrows():
            showlegend = True
            df = self._read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time'],
                var_names=var_names
                )
            point_df = self._read_model_point(entity['set_id'], var_names)
            
            fig = make_subplots(
                rows=3, 
                cols=2, 
                specs=[
                    [{'type' : 'xy'},{'type' : 'xy'}], 
                    [{'type' : 'xy'},{'type' : 'xy'}],
                    [{'type' : 'xy'},{'type' : 'polar'}]
                    ]
                )
            for key_,cols,nrow,ncol in comb:
                for i, column in enumerate(cols):
                    fig.add_trace(
                        go.Scatter(
                            x=df['ts'],
                            y=df[column],
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
                            x=df['ts'],
                            y=df[column],
                            mode='lines',
                            opacity=0.5,
                            name=point_df.loc[column, 'point_name'],
                            showlegend=showlegend,
                            line=dict(color=colors[i])
                            ),
                        row=nrow,
                        col=ncol
                        )
                showlegend=False
                fig.update_xaxes(title_text='时间', row=nrow, col=ncol)
                fig.update_yaxes(title_text=key_, row=nrow, col=ncol)
            #极坐标图
            fig.add_trace(
                go.Scatterpolar(
                    theta=df['var_18006'], 
                    r=df['var_18000']-df['var_18000'].mean(), 
                    mode='markers',
                    marker=dict(size=3, opacity=0.5),
                    name=point_df.loc['var_18000', 'point_name'],
                    ),
                row=3,
                col=2
                )
            self._tight_layout(fig)
                    
            self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()