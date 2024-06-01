# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
from typing import List, Union, Optional
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list

#%% constants

#%% class
class Polar(Base):
    '''
    >>> cls = Polar()
    >>> fig = cls.plot(set_id='20835', device_ids=['s10003', 's10004'], start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''    
    def init(self, var_names:Optional[Union[List[str], str]]=[]):
        '''
        var_names : 必须指定两个变量
        '''
        var_names = make_sure_list(var_names)
        var_names = ['var_18000', 'var_18006'] if len(var_names)<1 else var_names
        assert len(var_names)==2, '散点图必须指定两个var_name，其中第一个是x坐标，第二个是y坐标'
        self.var_names = var_names[:2]
        self.height = 700
        self.width = 700
    
    def get_title(self, set_id, device_ids, ytitles):
        return f'r={ytitles.iloc[0]}, theta={ytitles.iloc[1]}'
    
    def build(self, data, ytitles):
        df = data
        fig = make_subplots()
        colors = px.colors.qualitative.Dark2
        i=0
        for device_id, plot_df in df.groupby('device_id'):
            fig.add_trace(
                go.Scatterpolar(
                    theta=plot_df[self.var_names[0]], 
                    r=plot_df[self.var_names[1]],
                    mode='markers',           
                    marker={'opacity':0.5, 'size':4, 'color':colors[i%len(colors)]},
                    name=self.devie_df.loc[device_id, 'device_name'],
                    showlegend=True
                    )
                )
            i += 1
        return fig
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()