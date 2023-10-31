# author luosz
# created on 10.23.2023

from ast import pattern
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots


from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot.base import BaseFigure
from wtbonline._report.brief_report import darw_footer


class BladeAsynchronous(BaseFigure):
    def _initialize(self):
        '''
        >>> ba = BladeAsynchronous({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> ba.plot()
        '''
        var_names=['var_101', 'var_102', 'var_103']
        for _,entity in  self.target_df.iterrows():
            df = self._read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time'],
                var_names=var_names
                )
            point_df = self._read_model_point(entity['set_id'], var_names)
            fig = go.Figure()
            for col in var_names:
                fig.add_trace(
                    go.Scatter(
                        x=df['ts'], 
                        y=df[col], 
                        mode='lines',
                        marker=dict(size=3,opacity=0.5), 
                        name=point_df.loc[col, 'point_name']
                        )
                    )
            fig.layout.xaxis.update({'title': '时间'})
            fig.layout.yaxis.update({'title': '桨距角_°'})
            self._tight_layout(fig)
            self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()