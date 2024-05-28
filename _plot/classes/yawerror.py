# author luosz
# created on 10.23.2023

from typing import List, Union
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px 
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

from wtbonline._plot.classes.base import Base
from wtbonline._common.utils import make_sure_list
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._process.tools.filter import normal_production

#%% constant
COL_AUG = ['totalfaultbool_mode', 'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique', 'pv_c',
           'workmode_mode', 'workmode_nunique', 'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean', 'bin']
DEVICE_DF = PGFacade().read_model_device().set_index('device_id')

#%% class
class YawError(Base):
    '''
    >>> ye = YawError()
    >>> fig = ye.plot(set_id='20080', device_ids=['s10005'], start_time='2023-04-01 00:00:00', end_time='2024-04-01 00:00:00')
    >>> fig.show(renderer='png')
    '''  
    def init(self, var_names=[]):
        ''' 定制的初始化过程 '''
        self.height = 900
        # 有功功率, 瞬时风向, 风轮转速, 瞬时风速
        self.var_names = ['device_id', 'powact_mean', 'var_363_mean', 'var_94_mean', 'winspd_mean', 'winspd_std', 'var_101_iqr', 'var_101_mean']
    
    def get_title(self, set_id, device_ids, ytitles):
        sr = pd.Series(device_ids).sort_values()
        return DEVICE_DF['device_name'].loc[sr[0]]
    
    def read_data(self, set_id:str, device_ids:List[str], start_time:str, end_time:str, var_names:Union[str, List[str]]):
        sr = pd.Series(device_ids).sort_values()
        var_names = make_sure_list(var_names)
        df = self.RSDBFC.read_statistics_sample(
            set_id=set_id,
            device_id=sr[0],
            start_time=start_time,
            end_time=end_time,
            columns = list(set(COL_AUG+var_names)),
            )
        # 正常发电数据
        df = normal_production(df)
        if len(device_ids)!=len(df['device_id'].unique()):
            raise ValueError(f'部分机组查无数据，实际：{df["device_id"].unique().tolist()}，需求：{device_ids}')
        # 15°空气密度
        df['winspd_mean'] = df['winspd_mean']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
        # 无变桨
        df = df[(df['var_101_mean']<1) & (df['var_101_iqr']<0.1)]
        # 拆分区间
        span = 0.6
        bins_mid = np.arange(4,10)
        bins = [pd.Interval(left=i-span/2, right=i+span/2)  for i in bins_mid]
        df['wspd_bin'] = pd.cut(df['winspd_mean'],  bins=bins)
        df = df.dropna(how='any')
        df['wspd_mid'] = df['wspd_bin'].apply(lambda x:int(x.mid)).astype(float)
        # 湍流度控制
        df = df[df['winspd_std'].between(0, df['winspd_std'].quantile(0.8))]
        df = df[df['var_94_mean'].between(*df['var_94_mean'].quantile([0.05, 0.95]))]
        # 功率修正
        df['powact_mean'] = df['powact_mean']*(df['wspd_mid']/df['winspd_mean']).pow(3)
        return df.drop(columns=COL_AUG)
    
    def build(self, data, ytitles):
        df = data
        rows = int(np.ceil(len(df['wspd_bin'].dtype.categories)/2))
        subplot_titles = [f'风速区间 {i} m/s' for i in df['wspd_bin'].dtype.categories]
        fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)
        colors = px.colors.qualitative.Dark2
        for device_id in pd.Series(df['device_id'].unique()).sort_values():
            i = 0
            grp = df[df['device_id']==device_id]
            for interval in grp['wspd_bin'].dtype.categories:
                sub_df = grp[grp['wspd_bin']==interval].reset_index()
                row=int(i/2)+1
                col=i%2+1
                x=sub_df['var_363_mean']
                y=sub_df['powact_mean']
                # 散点图
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode='markers',
                        showlegend=False,
                        marker={'opacity':0.2, 'color':colors[2]},
                        ),
                        row=row,
                        col=col,
                    )   
                # 拟合曲线
                if len(x)<3:
                    continue
                X = pd.DataFrame({'x':x, 'x^2':x.pow(2), 'x^3':x.pow(3)})
                reg = LinearRegression(fit_intercept=True)
                reg.fit(X,y)
                x_ = pd.Series(np.arange(int(x.min()), int(x.max()), 0.1))
                X_ = pd.DataFrame({'x':x_, 'x^2':x_.pow(2), 'x^3':x_.pow(3)})
                y_ = pd.Series(reg.predict(X_))
                fig.add_trace(
                    go.Scatter(
                        x=x_,
                        y=y_,
                        mode='lines',
                        line={'color':colors[1]},
                        showlegend=False,
                        ),
                        row=row,
                        col=col,
                    ) 
                index = [y_.idxmax()]
                fig.add_trace(
                    go.Scatter(
                        x=x_.loc[index],
                        y=y_.loc[index],
                        mode='markers',
                        marker={'size':15, 'color':colors[1], 'symbol':'cross-dot'},
                        showlegend=False,
                        ),
                        row=row,
                        col=col,
                    )                
                fig.update_xaxes({'title': '10分钟平均有功功率 kW'}, row=row, col=col)
                fig.update_yaxes({'title': '10分钟平均风向 °', 'range':[0, sub_df['powact_mean'].max()]}, row=row, col=col)
                i = i+1
        return fig
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()