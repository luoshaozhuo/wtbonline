# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
from typing import List, Union, Optional
import plotly.express as px 
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from wtbonline._process.tools.frequency import power_spectrum, amplitude_spectrum
from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list
from wtbonline._db.postgres_facade import PGFacade

#%% constants
TYPE_ = {
    'power_spectrum':power_spectrum, 
    'amplitude_spectrum':amplitude_spectrum
    }
DEVICE_DF = PGFacade.read_model_device().set_index('device_id')

#%% class
class Spectrum(Base):
    '''
    >>> spec = Spectrum()
    >>> fig = spec.plot(set_id='20835', device_ids=['s10003', 's10004'], start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''    
    def init(self, var_names:Optional[Union[List[str], str]]=[]):
        '''
        var_names : 最多支持两个变量
        '''
        var_names = make_sure_list(var_names)
        var_names = ['var_18000', 'var_18006'] if len(var_names)<1 else var_names
        self.var_names = var_names[:2]
        self.height = 600
        self.width = 900
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]]):
        # 加入转速用于计算参考频率
        var_names = var_names if 'var_94' in var_names else var_names + ['var_94']
        # 仅支持单个机组
        df = super().read_data(
            set_id=set_id, 
            device_ids=device_ids[0], 
            start_time=start_time, 
            end_time=end_time,
            var_names=var_names
            )
        if len(df)<1:
            raise ValueError(f'{device_ids[0]}在{start_time}至{end_time}时间段内查无数据')
        return df
    
    def get_title(self, set_id, device_ids, ytitles):
        return DEVICE_DF.loc[device_ids[0], 'device_name']
        
    def build(self, data, ytitles, **kwargs):
        # type_ 支持类型power_spectrum及amplitude_spectrum
        df = data
        try:
            type_ = kwargs.get('type_', 'power_spectrum')
            func = TYPE_[type_]
            ytitle_aug = '^2' if type_=='power_spectrum' else ''
        except:
            raise ValueError(f'type_必须是{list(TYPE_.keys())}之一')
        sample_spacing = kwargs.get('sample_spacing', 1)
        mean_rspd = df[f'var_94'].mean()
        base_freq = mean_rspd/60.0
        vlines = pd.Series(np.arange(1,6))*base_freq
        vlines = vlines[(vlines>0) & (vlines<(0.5/sample_spacing))]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        colors = px.colors.qualitative.Dark2
        for device_id, plot_df in df.groupby('device_id'):
            for i, var_name in enumerate(self.var_names):
                secondary_y=(i>0)
                fft_df = func(plot_df[var_name], sample_spacing=sample_spacing)
                fft_df = fft_df[fft_df['freq']>0]
                fig.add_trace(
                    go.Scatter(
                        x=fft_df['freq'], 
                        y=fft_df['amp'], 
                        mode='lines+markers',
                        name=DEVICE_DF.loc[device_id, 'device_name'],
                        marker=dict(size=3,opacity=0.5,color=colors[i]), 
                        line=dict(color=colors[i]), 
                        showlegend=False
                        ),
                    secondary_y=secondary_y
                    )
                fig.update_yaxes(title_text=ytitles[var_name]+ytitle_aug, secondary_y=secondary_y)
                if i>2:
                    break
            break
        fig.update_xaxes(title_text=f'频率 Hz @ {mean_rspd:.2f} rpm')
        # 加入特征频率
        for i,x in enumerate(vlines): 
            fig.add_vline(
                x=x, 
                annotation_text=f"{i+1}",
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                ) 
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()