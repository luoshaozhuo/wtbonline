# author luosz
# created on 10.23.2023


import plotly.graph_objects as go

from wtbonline._plot.base import BaseFigure


class GeneratorOverload(BaseFigure):
    def initialize(self):
        '''
        >>> govl = GeneratorOverload({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> govl.plot()
        '''
        for _,entity in  self.target_df.iterrows():
            df = self.read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time'],
                var_names=['var_246']
                )
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df['ts'], 
                    y=df['var_246'], 
                    mode='lines',
                    marker=dict(size=3,opacity=0.5), 
                    )
                )
            fig.layout.xaxis.update({'title': '时间'})
            fig.layout.yaxis.update({'title': '电网有功功率 kW'})
            self.tight_layout(fig)
            self.figs.append(fig)

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()