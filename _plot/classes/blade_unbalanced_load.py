# author luosz
# created on 10.23.2023

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots

from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot.classes.base import BaseFigure


class BladeUnblacedLoad(BaseFigure):
    def _read_data(self, turbine_id, start_time, end_time):
        data_df = []
        for i in range(20):
            sql = f'''
                select 
                    ts, var_382, var_18000, var_18001, var_18002, var_18003, var_18004, var_18005, var_18008, var_18009, var_18010, var_18011 
                from
                    d_{turbine_id}
                where
                    ts >= '{start_time}'
                    and ts < '{end_time}'
                '''
            sql = self._concise(sql)
            temp = TDFC.query(sql, remote=True)
            if temp.shape[0]==0:
                break
            start_time = temp['ts'].max()
            data_df.append(temp)
        data_df = pd.concat(data_df, ignore_index=True)
        data_df['ts'] = pd.to_datetime(data_df['ts'])
        data_df.set_index('ts', drop=False, inplace=True)
        cols = ['var_18000', 'var_18001', 'var_18002', 'var_18003', 'var_18004', 'var_18005']
        mean_df = data_df[cols].rolling('180s').mean()
        x_fft, y_fft = self._amplitude_spectrum(data_df['var_382'], 1)
        fft_df = pd.DataFrame({'x':x_fft, 'y':y_fft})
        fft_df = fft_df[fft_df['x']>=0]
        
        count = self.samples
        data_df.reset_index(drop=True, inplace=True)
        data_df = data_df if data_df.shape[0]<count else data_df.sample(count).sort_values('ts')
        mean_df.reset_index(drop=False, inplace=True)
        mean_df = mean_df if mean_df.shape[0]<count else mean_df.sample(count).sort_values('ts')
        fft_df = fft_df if fft_df.shape[0]<count else fft_df.sample(count).sort_values('x')
        return data_df, mean_df, fft_df
    
    def _initialize(self):
        '''
        >>> bul = BladeUnblacedLoad({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
        >>> bul.plot()
        '''
        comb = [
            ('摆振', ['var_18000', 'var_18001', 'var_18002']), 
            ('挥舞', ['var_18003', 'var_18004', 'var_18005'])
            ]
        colors = px.colors.qualitative.Plotly
        for _,entity in  self.target_df.iterrows():
            showlegend = True
            fig = make_subplots(3, 2)
            data_df, mean_df, fft_df = self._read_data(
                turbine_id=entity['turbine_id'],
                start_time=entity['start_time'],
                end_time=entity['end_time']
                )
            nrow=1
            for key_,cols in comb:
                ncol=1
                for suffix,df in [('瞬时', data_df), ('180s平均', mean_df)]:
                    for i, column in enumerate(cols):
                        fig.add_trace(
                            go.Scatter(
                                x=df['ts'],
                                y=df[column],
                                mode='lines',
                                opacity=0.5,
                                name=f'叶片{i+1}',
                                showlegend=showlegend,
                                line=dict(color=colors[i])
                                ),
                            row=nrow,
                            col=ncol
                            )
                    showlegend=False
                    fig.update_xaxes(title_text='时间', row=nrow, col=ncol)
                    fig.update_yaxes(title_text=f'{key_}弯矩_{suffix} Nm', row=nrow, col=ncol)
                    ncol+=1
                nrow+=1
            # 机舱加速度
            fig.add_trace(
                go.Scatter(
                    x=fft_df['x'],
                    y=fft_df['y'],
                    mode='lines',
                    name=f'X方向',
                    line=dict(color=colors[3])
                    ),
                row=nrow,
                col=1
                )
            fig.update_xaxes(title_text='Hz', row=nrow, col=1)
            fig.update_yaxes(title_text='加速度 m/s', row=nrow, col=1)
            # 载荷检测系统波长
            cols = ['var_18008', 'var_18009', 'var_18010', 'var_18011']
            for i, col in enumerate(cols):
                fig.add_trace(
                    go.Scatter(
                        x=data_df['ts'],
                        y=data_df[col],
                        mode='lines',
                        opacity=0.5,
                        name=f'系统波长{i+1}',
                        line=dict(color=colors[4+i])
                        ),
                    row=nrow,
                    col=2
                    )
            fig.update_xaxes(title_text='时间', row=nrow, col=2)
            fig.update_yaxes(title_text='系统波长', row=nrow, col=2)
            self._tight_layout(fig)
                    
            self.figs.append(fig)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()