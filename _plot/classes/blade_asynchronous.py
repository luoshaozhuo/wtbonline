# author luosz
# created on 10.23.2023

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from wtbonline._plot.classes.base import Base

class BladeAsynchronous(Base):
    '''
    >>> ba = BladeAsynchronous()
    >>> fig = ba.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 02:00:00')
    >>> fig.show(renderer='png')
    '''
    def init(self):
        self.var_names=['var_101', 'var_102', 'var_103', 'var_18028', 'var_18029', 'var_18030']
        self.height = self.row_height*2
        
    def build(self, df, ytitles):
        nrow = len(ytitles)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        assert df.shape[0]>1, '没有绘图数据'
        colors = px.colors.qualitative.Dark2
        var_names = ['var_101', 'var_102', 'var_103', 'var_18028', 'var_18029', 'var_18030']
        for i, var_name in enumerate(var_names):
            fig.add_trace(
                go.Scatter(
                    x=df['ts'], 
                    y=df[var_name],
                    mode='lines+markers',           
                    marker={'opacity':0.5, 'size':4, 'color':colors[i]},
                    name=ytitles[i],
                    ),
                row=1 if i<3 else 2, 
                col=1)
            fig.update_yaxes(title_text='实际角度 °' if i<3 else '参考角度 °', row=i+1, col=1)
        fig.update_xaxes(title_text='时间', row=nrow, col=1)
        return fig
     
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()