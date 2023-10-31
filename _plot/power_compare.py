# author luosz
# created on 10.23.2023

import plotly.graph_objects as go
import plotly.express as px 

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._plot.base import BaseFigure


class PowerCompare(BaseFigure):
    def _read_data(self, set_id, turbine_id, start_time, end_time):
        df = RSDBInterface.read_statistics_sample(
            set_id=set_id,
            turbine_id=turbine_id,
            start_time=start_time,
            end_time=end_time,
            columns = ['turbine_id', 'var_101_mean', 'var_102_mean', 'var_103_mean', 'var_246_mean', 'totalfaultbool_mode',
                    'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'workmode_mode',
                    'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique'],
            )
        # 正常发电数据
        df = df[
            (df['totalfaultbool_mode']=='False') &
            (df['totalfaultbool_nunique']==1) &
            (df['ongrid_mode']=='True') & 
            (df['ongrid_nunique']==1) & 
            (df['limitpowbool_mode']=='False') &
            (df['limitpowbool_nunique']==1) &
            (df['workmode_mode']=='32') &
            (df['workmode_nunique']==1) 
            ]        
        df.rename(columns={'var_246_mean':'mean_power'}, inplace=True)
        df['mean_pitch_angle'] = df[['var_101_mean', 'var_102_mean', 'var_103_mean']].mean(axis=1)
        return df[['mean_pitch_angle', 'mean_power']]
    
    def _initialize(self):
        '''
        >>> pc = PowerCompare({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-06-01'})
        >>> pc.plot()
        '''
        fig = go.Figure()
        for i,row in  self.target_df.iterrows():
            color = px.colors.qualitative.Plotly[i]
            df = self._read_data(row['set_id'], row['turbine_id'], row['start_time'], row['end_time'])
            fig.add_trace(
                go.Scatter(
                    x=df['mean_power'],
                    y=df['mean_pitch_angle'],
                    mode='markers',
                    name=row['name'],
                    marker=dict(opacity=0.1, color=color),
                    showlegend=True,
                    )
                ) 
        fig.layout.xaxis.update({'title': '10分钟平均电网有功功率 kW'})
        fig.layout.yaxis.update({'title': '10分钟平均桨距角 °'})
        self._tight_layout(fig)
        
        self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()