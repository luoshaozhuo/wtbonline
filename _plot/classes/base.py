# author luosz
# created on 10.23.2023

from typing import Union, List
import pandas as pd
import numpy as np

from plotly.subplots import make_subplots
import plotly.express as px 
import plotly.graph_objects as go
from wtbonline._db.common import make_sure_list

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.common import concise, standard

class BaseFigure():
    '''
    >>> df = {'set_id':'20835', 'turbine_id':'s10002', 'start_time':'2023-05-01', 'end_time':'2023-06-01'}
    >>> figure = BaseFigure(df, var_names=['var_101', 'var_102'])
    >>> figure.plot()
    '''  
    def __init__(self, target_df:Union[pd.DataFrame, dict], samples:int=3600, var_names:List[str]=[], height=600, title=''):
        '''
        target_df -- 目标数据集
            需要包含set_id,start_time,end_time，必须包含turbine_id', 'map_id', 'device'中的一个，
            字段名可以是中文，对应关系是：
                '机型编号':'set_id',
                '风机编号':'device'或'turbine_id',
                '地图编号':'map_id',
                '开始日期':'start_time',
                '结束日期':'end_time',
                '图例号':'name'
        samples -- 最大绘图点数
        '''
        self.figs = []
        self.samples = samples
        self.height = height
        self.target_df = self._check_target(target_df)
        self.var_names = make_sure_list(var_names)
        self.title = title
        self._init()
        self._initialize()
    
    def _init(self):
        ''' 定制的初始化过程 '''
        pass
    
    def _concise(self, sql):
        return concise(sql)
    
    def _amplitude_spectrum(self, y_t, sample_spacing=1):
        ''' 计算幅度谱 '''
        N = len(y_t)
        x_fft = np.fft.fftfreq(N, sample_spacing)
        y_fft = np.abs(np.fft.fft(y_t))*2.0/N # 单边幅度谱    
        return x_fft, y_fft
    
    def _standard(self, set_id, df):
        ''' 按需增加turbine_id、测点名称、设备编号 '''
        return standard(set_id, df)
    
    def _check_target(self, target_df):
        ''' 增加必要的的字段，转换数据类型 '''
        if not isinstance(target_df, (pd.DataFrame, dict)) :
            raise ValueError('target_df必须是DataFrame或dict')
        if isinstance(target_df, dict):
            try:
                target_df = pd.DataFrame(target_df)
            except:
                target_df = pd.DataFrame(target_df, index=[0])
        target_df = target_df.rename(columns={
            '机型编号':'set_id',
            '风机编号':'map_id',
            '开始日期':'start_time',
            '结束日期':'end_time',
            'deive':'turbine_id',
            '图例号':'name'
            })
        cols_compulsory = pd.Series(['set_id', 'start_time', 'end_time'])
        cols_optional = pd.Series(['turbine_id', 'map_id'])
        if not cols_compulsory.isin(target_df).all():
            raise ValueError(f'target_df必须包含如下字段：{cols_compulsory}')
        if not cols_optional.isin(target_df).any():
            raise ValueError(f'target_df必须包含如下字段中的一个：{cols_optional}')
        
        ret = []
        for set_id,grp in target_df.groupby('set_id'):
            ret.append(self._standard(set_id, grp))
        ret = pd.concat(ret, ignore_index=True)
        if ret.shape[0]<1:
            raise ValueError('target_df经过标准化处理后为空')
        
        if 'name' not in ret.columns:
            ret.insert(0, 'name', ret['map_id'])
        ret['start_time'] = pd.to_datetime(ret['start_time'])
        ret['end_time'] = pd.to_datetime(ret['end_time'])
        
        return ret
    
    def _read_data(self, turbine_id, start_time, end_time, var_names, remote=True):
        ''' 读取tsdb数据 '''
        var_names = var_names.copy()
        if 'ts' not in var_names:
            var_names.append('ts')
        var_names = set(var_names)
        df = []
        for i in range(20):
            sql = f'''
                select 
                    {','.join(var_names)}
                from
                    d_{turbine_id}
                where
                    ts >= '{start_time}'
                    and ts < '{end_time}'
                '''
            sql = self._concise(sql)
            temp = TDFC.query(sql, remote=remote)
            if temp.shape[0]==0:
                break
            start_time = temp['ts'].max()
            df.append(temp)
        df = pd.concat(df, ignore_index=True)
        df = df.sample(self.samples) if df.shape[0]>self.samples else df
        df = df.sort_values('ts').reset_index(drop=True)
        assert df.shape[0]>0, f'查无数据:{sql}'
        return df
    
    def _read_model_point(self, set_id, var_names):
        ''' 读取model_point表格 '''
        var_names = make_sure_list(var_names)
        assert len(var_names)>0, '未指定var_names'
        point_df = RSDBInterface.read_turbine_model_point(
            set_id=set_id, 
            var_name=var_names,
            columns=['var_name', 'point_name', 'unit', 'datatype'],
            select=None
            )
        assert point_df.shape[0]>0, f'turbine_model_point中找不到指定的var_names，{var_names}'
        point_df['var_name'] = point_df['var_name'].str.lower()
        point_df.set_index('var_name', drop=False, inplace=True)
        point_df['name'] = point_df['point_name']+'_'+point_df['unit']
        return point_df
    
    def _initialize(self, xasix='ts', mode='lines', opacity=0.5):
        ''' 构造figures，并赋予self.figs，默认绘制曲线图。同一个set的数据放在一张图内，每条曲线单独绘制。 '''
        N = len(self.var_names)
        for set_id,grp in self.target_df.groupby('set_id'):
            point_df = self._read_model_point(set_id, self.var_names)
            for _,row in  grp.iterrows():
                df = self._read_data(row['turbine_id'], row['start_time'], row['end_time'], self.var_names)
                if df.shape[0]<1:
                    continue
                fig = make_subplots(N, 1, shared_xaxes=True, vertical_spacing=0.05)
                for i, col in enumerate(self.var_names):
                    color = px.colors.qualitative.Plotly[i]
                    fig.add_trace(
                        go.Scatter(
                            x=df[xasix],
                            y=df[col],
                            mode=mode,
                            showlegend=False,
                            line=dict(color=color),
                            marker=dict(opacity=opacity, color=color),
                            ),
                        row=(i+1),
                        col=1,
                        )
                    fig.update_yaxes(title_text=point_df.loc[col,'name'], row=(i+1), col=1) 
                fig.update_xaxes(title_text='时间', row=N, col=1)
                self._tight_layout(fig)
                self.figs.append(fig) 
    
    def plot(self, renderer=None):
        for fig in self.figs:
            fig.show(renderer=renderer)
        
    def _tight_layout(self, fig):
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
            margin=dict(l=50, r=50, t=70, b=50)
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()