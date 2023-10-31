# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
from wtbonline._plot.base import BaseFigure


class HubAzimuth(BaseFigure):
    def _initialize(self):
        '''
        >>> ha = HubAzimuth({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> ha.plot()
        '''
        for _,entity in  self.target_df.iterrows():
            df = self._read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time'],
                var_names=['var_18000', 'var_18006']
                )
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df['var_18006'], 
                    y=df['var_18000'], 
                    mode='markers',
                    marker=dict(size=3,opacity=0.5), 
                    )
                )
            fig.layout.xaxis.update({'title': '风轮方位角 °'})
            fig.layout.yaxis.update({'title': '叶片1摆振弯矩 Nm'})
            self._tight_layout(fig)
            self.figs.append(fig)

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()