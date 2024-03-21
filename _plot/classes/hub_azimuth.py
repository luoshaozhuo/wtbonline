# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
import plotly.express as px 
from wtbonline._plot.classes.base import Base


class HubAzimuth(Base):
    '''
    >>> ha = HubAzimuth()
    >>> fig = ha.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''    
    def init(self, var_names=[]):
        self.var_names=['var_18000', 'var_18006']
        self.height = 400
        self.width = 900
        self.mode = 'markers'
    
    def build(self, data, ytitles):
        df = data
        fig = go.Figure()
        colors = px.colors.qualitative.Dark2
        i=0
        for device_id, plot_df in df.groupby('device_id'):
            fig.add_trace(
                go.Scatter(
                    x=plot_df['var_18006'], 
                    y=plot_df['var_18000'], 
                    mode='markers',
                    name=device_id,
                    marker=dict(size=3,opacity=0.5,color=colors[i]), 
                    )
                )
            i=i+1
        fig.layout.xaxis.update({'title': ytitles['var_18006']})
        fig.layout.yaxis.update({'title': ytitles['var_18000']})
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()