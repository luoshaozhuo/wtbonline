# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
from plotly.subplots import make_subplots

from wtbonline._plot.classes.base import Base


class BladePitchkick(Base):
    '''
    >>> bp = BladePitchkick()
    >>> fig = bp.plot(set_id='20835', device_ids='s10003', start_time='2023-10-01 00:00:00', end_time='2023-10-01 02:00:00')
    >>> fig.show(renderer='png')
    '''
    def init(self):
        self.var_names=['var_101', 'var_102', 'var_103', 'var_246', 'var_94', 'var_23569']
        self.height = 900
        self.width = 900   
    
    def build(self, df, ytitles):
        for device_id, plot_df in df.groupby('device_id'):
            fig = make_subplots(4, 1, shared_xaxes=True, vertical_spacing=0.05)
            # 桨距角
            for i,col in enumerate(['var_101', 'var_102', 'var_103']):
                fig.add_trace(
                    go.Scatter(
                        x=plot_df['ts'],
                        y=plot_df[col],
                        mode='lines',
                        opacity=0.5,
                        name=f'{i+1}#叶片实际角度',
                        showlegend=True
                        ),
                    row=1,
                    col=1,
                    )
            fig.update_yaxes(title_text='桨距角 °', row=1, col=1)
            # 转速
            var_name = 'var_246'
            fig.add_trace(
                go.Scatter(
                    x=plot_df['ts'],
                    y=plot_df[var_name],
                    mode='lines',
                    # name='电网有功功率',
                    showlegend=False
                    ),
                row=2,
                col=1,
                )
            fig.update_yaxes(title_text=ytitles[var_name], row=2, col=1)
            # 功率
            var_name = 'var_94'
            fig.add_trace(
                go.Scatter(
                    x=plot_df['ts'],
                    y=plot_df['var_94'],
                    mode='lines',
                    # name='风轮转速',
                    showlegend=False
                    ),
                row=3,
                col=1,
                )
            fig.update_yaxes(title_text=ytitles[var_name], row=3, col=1)
            # pitchkick触发状态
            var_name = 'var_23569'
            y = plot_df[var_name].fillna('false')
            fig.add_trace(
                go.Scatter(
                    x=plot_df['ts'],
                    y=y,
                    mode='lines',
                    # name='pitchkick触发状态',
                    showlegend=False
                    ),
                row=4,
                col=1,
                )
            fig.update_yaxes(title_text=ytitles[var_name], row=4, col=1)
            fig.update_xaxes(title_text='时间', row=4, col=1)
            break
        return fig
    
    # def _init(self):
    #     self.height = 800
    
    # def _initialize(self):
    #     '''
    #     >>> bp = BladePitchkick({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
    #     >>> bp.plot()
    #     '''
    #     for _,entity in self.target_df.iterrows():
    #         df = self._read_data(
    #             turbine_id=entity['turbine_id'],
    #             start_time=entity['start_time'],
    #             end_time=entity['end_time'],
    #             var_names=['var_101', 'var_102', 'var_103', 'var_246', 'var_94', 'var_23569']
    #             )
    #         fig = make_subplots(4, 1, shared_xaxes=True, vertical_spacing=0.05)
    #         # 桨距角
    #         for i,col in enumerate(['var_101', 'var_102', 'var_103']):
    #             fig.add_trace(
    #                 go.Scatter(
    #                     x=df['ts'],
    #                     y=df[col],
    #                     mode='lines',
    #                     opacity=0.5,
    #                     name=f'{i+1}#叶片实际角度',
    #                     # showlegend=False
    #                     ),
    #                 row=1,
    #                 col=1,
    #                 )
    #         fig.update_yaxes(title_text='桨距角 °', row=1, col=1)
    #         # 转速
    #         fig.add_trace(
    #             go.Scatter(
    #                 x=df['ts'],
    #                 y=df['var_246'],
    #                 mode='lines',
    #                 name='电网有功功率',
    #                 showlegend=False
    #                 ),
    #             row=2,
    #             col=1,
    #             )
    #         fig.update_yaxes(title_text='功率 kW', row=2, col=1)
    #         # 功率
    #         fig.add_trace(
    #             go.Scatter(
    #                 x=df['ts'],
    #                 y=df['var_94'],
    #                 mode='lines',
    #                 name='风轮转速',
    #                 showlegend=False
    #                 ),
    #             row=3,
    #             col=1,
    #             )
    #         fig.update_yaxes(title_text='转速 RPM', row=3, col=1)
    #         # pitchkick触发状态
    #         y = df['var_23569'].fillna('false')
    #         fig.add_trace(
    #             go.Scatter(
    #                 x=df['ts'],
    #                 y=y,
    #                 mode='lines',
    #                 name='pitchkick触发状态',
    #                 showlegend=False
    #                 ),
    #             row=4,
    #             col=1,
    #             )
    #         fig.update_yaxes(title_text='pitchkick触发状态', row=4, col=1)
    #         fig.update_xaxes(title_text='时间', row=4, col=1)
    #         self._tight_layout(fig)
    #         self.figs.append(fig)

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()