# author luosz
# created on 10.23.2023

#%% import
from typing import List, Union
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from wtbonline._common.utils import make_sure_list
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.rsdb_facade import RSDBFacade

#%%
DEVICE_DF = PGFacade().read_model_device().set_index('device_id')

#%% class
class Base():
    '''
    >>> base = Base()
    >>> fig = base.plot(set_id='20835', device_ids=['s10003', 's10004'], start_time='2023-05-01 00:00:00', end_time='2023-05-01 02:00:00')
    >>> fig.show(renderer='png')
    '''
    def __init__(self, nsamples:int=3600, samplling_rate:int=1, row_height=300, width=900, showlegend=True):
        '''
        target_df -- 目标数据集
            必须包含set_id,device_id,start_time,end_time'，
        samples -- 最大绘图点数
        '''
        self.RSDBFC = RSDBFacade()
        self.nsamples = nsamples
        self.samplling_rate = samplling_rate
        self.row_height = row_height
        self.showlegend=showlegend
        self.width = width
        
    def init(self, var_names=['totalfaultbool', 'workmode', 'limitpowbool']):
        ''' 定制的初始化过程 '''
        self.var_names = make_sure_list(var_names)
        self.height = max(self.row_height*len(var_names), self.row_height*1.5)
        self.mode='lines+markers'
    
    def plot(self, set_id:str, device_ids:Union[str, List[str]], start_time:str, end_time:str, title=None, **kwargs):
        if not hasattr(self, 'var_names'):
            self.init()
        device_ids = make_sure_list(device_ids)
        data = self.read_data(set_id=set_id, device_ids=device_ids, start_time=start_time, end_time=end_time, var_names=self.var_names)
        ytitles = self.get_ytitles(set_id=set_id)
        title = self.get_title(set_id=set_id, device_ids=device_ids, ytitles=ytitles) if title is None else title
        fig = self.build(data=data, ytitles=ytitles, **kwargs)
        self.tight_layout(fig, title)
        return fig
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]]):
        ''' 读取数据，默认从远程tsdb读取
        row : set_id, device_id, start_time, end_time
        '''
        var_names = list(set(make_sure_list(var_names)))
        device_ids = list(set(make_sure_list(device_ids)))
        df = []
        for device_id in device_ids:
            temp = TDFC.read(
                set_id=set_id,
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                columns=var_names,
                sample=self.nsamples,
                remote=True,
                )
            temp['device_id'] = device_id
            df.append(temp)
        df = pd.concat(df, ignore_index=True)
        df = df.sort_values('ts')
        df = df[['ts', 'device_id']+var_names]
        if len(device_ids)!=len(df['device_id'].unique()):
            raise ValueError(f'部分机组查无数据，实际：{df["device_id"].unique().tolist()}，需求：{device_ids}')
        return df
    
    def get_ytitles(self, set_id):
        df = TDFC._get_variable_info(set_id, self.var_names).drop_duplicates()
        return df.set_index('column')['name']
    
    def get_title(self, set_id, device_ids, ytitles):
        return '时间序列'

    def build(self, data, ytitles):
        df = data
        nrow = len(ytitles) 
        fig = make_subplots(rows=nrow, cols=1, shared_xaxes=True, vertical_spacing=10/self.height)
        colors = px.colors.qualitative.Dark2
        for i in range(len(self.var_names)):
            var_name = self.var_names[i]
            j=0
            for device_id, plot_df in df.groupby('device_id'):
                fig.add_trace(
                    go.Scatter(
                        x=plot_df['ts'], 
                        y=plot_df[var_name],
                        mode=self.mode,           
                        marker={'opacity':0.5, 'size':4, 'color':colors[j%len(colors)]},
                        line={'color':colors[j%len(colors)]},
                        name=DEVICE_DF.loc[device_id, 'device_name'],
                        showlegend=(i==0)
                        ),
                    row=i+1, 
                    col=1)
                j=j+1
            fig.update_yaxes(title_text=ytitles[var_name], row=i+1, col=1)
            fig.update_yaxes(
                title=dict(text=ytitles[var_name], font=dict(size=12)), 
                automargin=True,
                row=i+1, 
                col=1)
        fig.update_xaxes(
            title=dict(text='时间', font=dict(size=12)), 
            row=nrow, 
            col=1)
        return fig

    def tight_layout(self, fig, title):
        fig.update_layout(
            title=dict(text=title, font=dict(size=15), x=0.1, y=1-5/self.height, xanchor='left', yanchor='top', automargin=True),
            height=self.height,
            width=self.width,
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1+10/self.height,
                xanchor="right",
                x=1),
            showlegend=self.showlegend,
            margin=dict(l=20, r=20, t=20 if title in ('', None) else 70, b=20),
            hovermode="x unified"
            )  

if __name__ == '__main__':
    import doctest
    doctest.testmod()