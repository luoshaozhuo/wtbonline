# author luosz
# created on 10.23.2023


import plotly.graph_objects as go
from typing import List, Union, Optional
import pandas as pd

from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._process.tools.filter import normal_production
from wtbonline._db.postgres_facade import PGFacade

#%% constant
ANOMALY_MATRIX_PLOT_COLOR = {
    '非离群':'gray',
    '正常':'#2ca02c',
    '异常':'red',
    '离群，未标注':'blue',
    }

COLUMNS_AUG = [
    'set_id', 'device_id', 'pv_c', 'limitpowbool_mode', 'limitpowbool_nunique', 'workmode_mode', 
    'workmode_nunique', 'ongrid_mode', 'ongrid_nunique', 'totalfaultbool_mode', 'totalfaultbool_nunique', 'id', 'bin'
    ]

DEVICE_DF = PGFacade.read_model_device().set_index('device_id')

#%% class
class Anomaly(Base):
    '''
    >>> cls = Anomaly()
    >>> cls.init(var_names=['var_94','winspd', 'var_226'])
    >>> fig = cls.plot(set_id='20625', device_ids='d10003', start_time='2023-10-01 00:00:00', end_time='2024-10-01 00:30:00')
    >>> fig.show(renderer='png')
    '''    
    def init(self, var_names:Optional[Union[List[str], str]]=[]):
        '''
        var_names : 最少指定两个变量
        '''
        var_names = make_sure_list(var_names)
        for i,var in enumerate(var_names):
            if var.split('_')[-1] != 'mean':
                var_names[i] = var_names[i]+'_mean'
        columns = [
            'var_94_mean', 'winspd_mean', 'var_226_mean', 'var_101_mean',
            'var_382_mean', 'var_383_mean'
            ]
        self.var_names = columns if len(var_names)<1 else var_names
        if len(self.var_names)<3:
            raise ValueError('最少需要三个var_name')
        self.height = 800
        self.width = 800
        self.showlegend = False
    
    def get_title(self, set_id, device_ids, ytitles):
        return DEVICE_DF.loc[device_ids[0], 'device_name']
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]]):
        # 仅绘制单台机组
        device_id = make_sure_list(device_ids)[0]
        var_names = make_sure_list(var_names)
        col_all = make_sure_list(set(COLUMNS_AUG+var_names))
        col_sel = make_sure_list(set(var_names+['bin', 'id']))
        # filter会筛除大部分数据，所以用4倍sample_cnt来采样
        sample_df = RSDBFacade.read_statistics_sample(
            set_id=set_id,
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            limit=4*self.nsamples, 
            random=True,
            columns = col_all
            )
        sample_df = normal_production(sample_df).loc[:, col_sel]
        if len(sample_df)==0:
            raise ValueError('无数据')
        # 合异常数据
        idx = RSDBFacade.read_model_anormaly(
            set_id=set_id, 
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            ).drop_duplicates('sample_id')['sample_id']
        if len(idx)>0:
            df = RSDBFacade.read_statistics_sample(id_=idx, columns=col_sel)
            rev = pd.concat([df, sample_df], ignore_index=True)
        else:
            rev = sample_df
        rev = rev.drop_duplicates('id').set_index('id', drop=False)
        rev.insert(0, 'is_suspector', -1)
        rev.loc[idx, 'is_suspector'] = 1
        # 增加标签字段
        df = RSDBFacade.read_model_label(set_id=set_id, device_id=device_ids)
        df = df.sort_values('create_time').drop_duplicates('sample_id', keep='last')
        if len(df)>0:
            rev = pd.merge(
                df[['sample_id', 'is_anomaly']], 
                rev.reset_index(drop=True), 
                left_on='sample_id', 
                right_on='id', 
                how='right'
                ).drop(columns=['sample_id'])
            rev['is_anomaly'] = rev['is_anomaly'].fillna(0)
        else:     
            rev['is_anomaly'] = 0
        # 抽样，保留全部异常数据
        sub_anormal = rev[rev['is_anomaly']==1]
        count = self.nsamples - len(sub_anormal)
        sub_normal = rev[rev['is_anomaly']==0]
        sub_normal = sub_normal.sample(count) if sub_normal.shape[0]>count else sub_normal
        rev = pd.concat([sub_normal, sub_anormal], ignore_index=True)
        # 加入绘图所需中文标签
        idx_not_susptor= rev[rev['is_suspector']==-1].index
        idx_suspetor_without_label = rev[(rev['is_anomaly']==0) & (rev['is_suspector']==1)].index
        idx_anormaly = rev[rev['is_anomaly']==1].index
        idx_not_anormaly = rev[rev['is_anomaly']==-1].index
        rev.loc[idx_not_susptor, 'textd'] = '非离群'
        rev.loc[idx_suspetor_without_label, 'textd'] ='离群，未标注'
        rev.loc[idx_anormaly, 'textd'] = '异常'
        rev.loc[idx_not_anormaly, 'textd'] = '正常'
        rev.loc[idx_not_susptor, 'color'] = ANOMALY_MATRIX_PLOT_COLOR['非离群']
        rev.loc[idx_suspetor_without_label, 'color'] = ANOMALY_MATRIX_PLOT_COLOR['离群，未标注']
        rev.loc[idx_anormaly, 'color'] = ANOMALY_MATRIX_PLOT_COLOR['异常']
        rev.loc[idx_not_anormaly, 'color'] = ANOMALY_MATRIX_PLOT_COLOR['正常']
        rev.loc[idx_not_susptor, 'opacity'] = 0.1
        rev.loc[idx_suspetor_without_label, 'opacity'] = 1
        rev.loc[idx_anormaly, 'opacity'] = 1
        rev.loc[idx_not_anormaly, 'opacity'] = 1 
        return rev
    
    def build(self, data, ytitles):
        df = data
        customdata = df['id'].to_list()
        fig = go.Figure()
        dimensions = []
        for var_name in self.var_names:
            dimensions.append(dict(label=ytitles[var_name], values=df[var_name]))
        fig.add_trace(
            go.Splom(
                dimensions=dimensions,
                marker=dict(color=df['color'],
                            size=3,
                            line=dict(width=0),
                            opacity=df['opacity'],
                            ),
                text=df['textd'],
                showupperhalf=False,
                customdata=customdata,
                selected={'marker':{'color':'cyan', 'opacity':1, 'size':6}},
                diagonal=dict(visible=False),
                )
            )
        return fig
 
    def tight_layout(self, fig, title):
        super().tight_layout(fig, title)
        fig.update_layout(
            **{f'xaxis{(i+1)}':{'title':{'font':{'size':12}}} for i in range(len(self.var_names))},
            **{f'yaxis{(i+1)}':{'title':{'font':{'size':12}}} for i in range(len(self.var_names))},
            clickmode='event+select',
            hovermode='closest',
            )
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()