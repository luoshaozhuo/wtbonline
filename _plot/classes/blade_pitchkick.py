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
    def init(self, var_names=[]):
        self.var_names=['var_101', 'var_102', 'var_103', 'var_246', 'var_94', 'var_23569']
        self.height = 900
        self.width = 900   
    
    def build(self, data, ytitles):
        df = data
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
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()