# author luosz
# created on 10.23.2023

#%% import
from typing import Union, List
import pandas as pd
import numpy as np

from plotly.subplots import make_subplots
import plotly.express as px 
import plotly.graph_objects as go

from wtbonline._common.utils import make_sure_list, make_sure_dataframe, make_sure_datetime
# from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.postgres_facade import PGFacade
# from wtbonline._process.tools.common import concise, standard
from wtbonline._plot.functions import ts_plot_stack

#%% class
class Base():
    '''
    >>> df = {'set_id':'20835', 'device_id':'s10003', 'start_time':'2023-05-01', 'end_time':'2023-06-01'}
    >>> base = Base(target_df=df, var_names=['var_101', 'var_103'])
    >>> fig = base.plot()[0]
    >>> fig.show(renderer='png')
    '''
    def __init__(self, target_df:Union[pd.DataFrame, dict], var_names:List[str], nsamples:int=3600, samplling_rate:int=1, height=600, title=''):
        '''
        target_df -- 目标数据集
            必须包含set_id,device_id,start_time,end_time'，
        samples -- 最大绘图点数
        '''
        self.nsamples = nsamples
        self.samplling_rate = samplling_rate
        self.height = height
        self.target_df = self._check_target(target_df)
        self.var_names = make_sure_list(var_names)
        self.title = title
        self.init()
        
    def init(self):
        ''' 定制的初始化过程 '''
        pass
    
    def plot(self):
        rev = []
        for _,row in self.target_df.iterrows():
            df = self.read_data(row=row)
            ytitles = self.get_ytitles(row['set_id'], set(df.columns)-set(['ts', 'device']))
            fig = self.build(df, ytitles)
            self.tight_layout(fig)
            rev.append(fig)
        return rev

    def _check_target(self, target_df):
        ''' 检查字段，转换数据类型 '''
        ret = target_df.copy()
        ret = make_sure_dataframe(target_df)
        cols = pd.Series(['set_id', 'device_id', 'start_time', 'end_time'])
        if not cols.isin(target_df).all():
            raise ValueError(f'target_df必须包含如下字段：{cols}')
        ret['start_time'] = pd.to_datetime(ret['start_time'])
        ret['end_time'] = pd.to_datetime(ret['end_time'])
        return ret
    
    def read_data(self, row:dict):
        ''' 读取数据，默认从远程tsdb读取
        row : set_id, device_id, start_time, end_time
        '''
        columns = [f'max({i}) as {i}' for i in self.var_names]
        df = TDFC.read(
            set_id=row['set_id'],
            device_id=row['device_id'],
            start_time=row['start_time'],
            end_time=row['end_time'],
            columns=columns,
            sample=self.nsamples,
            remote=True,
            )
        return df
    
    def get_ytitles(self, set_id, columns):
        return TDFC._get_variable_info(set_id, columns)['name'].tolist()

    def build(self, df, ytitles):
        return ts_plot_stack(df, ycols=self.var_names, ytitles=ytitles, title=self.title)
        
    def tight_layout(self, fig):
        fig.update_layout(
            title=dict(text=self.title, font=dict(size=20), y=0.98, yref='container'),
            height=self.height,
            legend=dict(
                orientation="h",
                font=dict(
                        size=12,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1),
            margin=dict(l=50, r=50, t=70, b=50),
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()