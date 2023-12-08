# author luosz
# created on 10.23.2023

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from wtbonline._plot.classes.base import BaseFigure


class BladeAsynchronous(BaseFigure):
    def _initialize(self):
        '''
        >>> ba = BladeAsynchronous({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> ba.plot()
        '''
        var_names=['var_101', 'var_102', 'var_103', 'var_18028', 'var_18029', 'var_18030']
        for _,entity in  self.target_df.iterrows():
            df = self._read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time'],
                var_names=var_names
                )
            point_df = self._read_model_point(entity['set_id'], var_names)
            fig = make_subplots(2,1,vertical_spacing=0.05, shared_xaxes=True)
            for i,col in enumerate(var_names):
                fig.add_trace(
                    go.Scatter(
                        x=df['ts'], 
                        y=df[col], 
                        mode='lines',
                        marker=dict(size=3,opacity=0.5), 
                        name=point_df.loc[col, 'point_name']
                        ),
                    row=i//3+1,
                    col=1
                    )
            fig.update_yaxes(title_text='桨距角 °', row=1, col=1)
            fig.update_yaxes(title_text='参考桨距角 °', row=2, col=1)
            fig.update_xaxes(title_text='时间', row=2, col=1)    
            self._tight_layout(fig)
            self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()