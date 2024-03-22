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

#%% class
class Base():
    '''
    >>> base = Base()
    >>> fig = base.plot(set_id='20835', device_ids=['s10003', 's10004'], start_time='2023-05-01 00:00:00', end_time='2023-05-01 02:00:00')
    >>> fig.init(var_names=['var_101', 'var_102'])
    >>> fig.show(renderer='png')
    '''
    def __init__(self, nsamples:int=3600, samplling_rate:int=1, row_height=200, showlegend=True):
        '''
        target_df -- 目标数据集
            必须包含set_id,device_id,start_time,end_time'，
        samples -- 最大绘图点数
        '''
        self.nsamples = nsamples
        self.samplling_rate = samplling_rate
        self.row_height = row_height
        self.showlegend=showlegend
        self.width = 900  
        self.init()
        
    def init(self, var_names=[]):
        ''' 定制的初始化过程 '''
        self.var_names = var_names
        self.height = self.row_height*len(var_names)
    
    def plot(self, set_id:str, device_ids:Union[str, List[str]], start_time:str, end_time:str, **kwargs):
        device_ids = make_sure_list(device_ids)
        data = self.read_data(set_id=set_id, device_ids=device_ids, start_time=start_time, end_time=end_time, **kwargs)
        ytitles = self.get_ytitles(set_id=set_id)
        title = self.get_title(set_id=set_id, device_ids=device_ids)
        fig = self.build(data=data, ytitles=ytitles)
        self.tight_layout(fig, title)
        return fig
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, **kwargs):
        ''' 读取数据，默认从远程tsdb读取
        row : set_id, device_id, start_time, end_time
        '''
        assert len(self.var_names), '没指定需要读取的变量名'
        device_ids = make_sure_list(device_ids)
        df = []
        for device_id in device_ids:
            temp = TDFC.read(
                set_id=set_id,
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                columns=self.var_names,
                sample=self.nsamples,
                remote=True,
                )
            temp['device_id'] = device_id
            df.append(temp)
        df = pd.concat(df, ignore_index=True)
        df = df.sort_values('ts')
        df = df[['ts', 'device_id']+self.var_names]
        assert df.shape[0]>1, '没有绘图数据'
        return df
    
    def get_ytitles(self, set_id):
        df = TDFC._get_variable_info(set_id, self.var_names)
        return df.set_index('var_name')['name']
    
    def get_title(self, set_id, device_ids):
        return device_ids[0] if len(device_ids)==1 else set_id

    def build(self, data, ytitles):
        df = data
        nrow = len(ytitles)
        fig = make_subplots(rows=nrow, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        colors = px.colors.qualitative.Dark2
        for i in range(len(self.var_names)):
            var_name = self.var_names[i]
            j=0
            for device_id, plot_df in df.groupby('device_id'):
                fig.add_trace(
                    go.Scatter(
                        x=plot_df['ts'], 
                        y=plot_df[var_name],
                        mode='lines+markers',           
                        marker={'opacity':0.5, 'size':4, 'color':colors[j%len(colors)]},
                        name=device_id,
                        showlegend=i==0
                        ),
                    row=i+1, 
                    col=1)
                j=j+1
            fig.update_yaxes(title_text=ytitles[var_name], row=i+1, col=1)
        fig.update_xaxes(title_text='时间', row=nrow, col=1)
        return fig

    def tight_layout(self, fig, title):
        fig.update_layout(
            title=dict(text=title, font=dict(size=15), xanchor='center', yanchor='top', x=0.5, y=0.99),
            height=self.height,
            width=self.width,
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1),
            showlegend=self.showlegend,
            margin=dict(l=20, r=20, t=20 if title in ('', None) else 70, b=20),
            hovermode="x unified"
            )  

if __name__ == '__main__':
    import doctest
    doctest.testmod()