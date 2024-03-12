# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

机器学习建模
"""
# %% import 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Optional, Tuple, Union
from sklearn.base import BaseEstimator
from itertools import combinations_with_replacement, product
import numpy as np

from _db.rsdb_facade import RSDBInterface
from wtbonline._db.common import make_sure_list, make_sure_dataframe, make_sure_series

# %% function
def readable_label(cols:Union[pd.Series, list, str, tuple], set_id:str, reverse:bool=False):
    '''
    >>> readable_label('var_94', '10050')
    ['风轮转速_RPM']
    >>> readable_label('风轮转速_RPM', '10050', True)
    ['var_94']
    '''
    cols = make_sure_list(cols)
    model_point = RSDBInterface.read_turbine_model_point(
        set_id=set_id, columns=['var_name', 'point_name', 'unit']
        )
    model_point['name'] = model_point['point_name'] + '_' + model_point['unit'] 
    x, y = 'var_name', 'name'
    if reverse:
        x, y = y, x
    repl = {row[x]:row[y] for i,row in model_point.iterrows()}
    return pd.Series(cols).replace(repl).tolist()
    
def scatter_anormaly(
        X:pd.DataFrame, 
        clf:BaseEstimator, 
        *,
        features:Optional[List[str]]=[],
        additional:Optional[List[str]]=[], 
        pathname:str=None):
    '''
    >>> from sklearn.neighbors import LocalOutlierFactor
    >>> from wtbonline._process.modelling import data_filter, get_XY
    >>> from sklearn.preprocessing import MinMaxScaler
    >>> features = ['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean']
    >>> additional = ['var_382_mean', 'var_383_mean','var_2709_mean']
    >>> kwargs = dict(
    ...     set_id='10050',
    ...     turbine_id='s10001',
    ...     start_time='2022-01-01',
    ...     end_time='2023-04-01',
    ...     )
    >>> raw_df = RSDBInterface.read_statistics_sample(**kwargs)
    >>> data_df = data_filter(raw_df)[features+additional]
    >>> scaler = MinMaxScaler().fit(data_df)
    >>> data_df = pd.DataFrame(
    ...     scaler.transform(data_df), 
    ...     columns=data_df.columns, 
    ...     index=data_df.index)
    >>> clf = LocalOutlierFactor(novelty=True, contamination=0.01, n_neighbors=200)
    >>> _ = clf.fit(data_df[features])
    >>> scatter_anormaly(data_df, clf, features=features, additional=additional, pathname='/home/luo/ctrl_anormaly.html')
    >>> features = ['var_382_mean', 'var_383_mean']
    >>> additional = ['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean', 'var_2709_mean']
    >>> data_df = data_filter(raw_df)[features+additional]
    >>> _ = clf.fit(data_df[features])
    >>> scatter_anormaly(data_df, clf, features=features, additional=additional, pathname='/home/luo/vrb_anormaly.html')
    '''
    X = make_sure_dataframe(X)
    features = make_sure_list(features)
    features = X.columns.to_list() if features is None else features
    columns = features + make_sure_list(additional)
    if len(X)<1:
        return
    
    comb_df = pd.DataFrame(
        list(combinations_with_replacement(columns, 2)), 
        columns=['x', 'y']
        )
    comb_df = comb_df[~(comb_df['x']==comb_df['y'])].reset_index(drop=True)
    is_abnormal = clf.predict(X[features])
    normal_df = X[is_abnormal==1]
    normal_index = normal_df.index if len(normal_df)<2000 else normal_df.sample(2000).index
    abnormal_index = X[is_abnormal==-1].index

    nrow = int(np.ceil(len(comb_df)/3))
    fig = make_subplots(nrow, 3)
    rc = [{'row':i[0], 'col':i[1]} for i in 
          list(product(np.arange(1,nrow+1),[1,2,3]))]
    for i, row in comb_df.iterrows():
        x,y = row.tolist()
        color = 'red' if x in features and y in features else 'blue'
        fig.add_trace(
            go.Scatter(
                x=X.loc[normal_index, x], 
                y=X.loc[normal_index, y], 
                marker=dict(color='gray', size=2, opacity=0.5),
                mode='markers'), 
            **rc[i]
            )
        fig.add_trace(
            go.Scatter(
                x=X.loc[abnormal_index, x], 
                y=X.loc[abnormal_index, y],
                mode='markers', 
                marker=dict(color=color, size=3, opacity=0.5)), 
                **rc[i]
                )
        fig.update_xaxes(title=x, **rc[i])
        fig.update_yaxes(title=y, **rc[i])
        i += 1
    fig.update_layout(
        width=1200, 
        height=200*nrow, 
        title=f'建模变量：{features}', 
        margin=dict(l=80, r=80, t=80, b=80), 
        showlegend=False
        )

    if pathname is not None:
        fig.write_html(pathname)
    else:
        fig.show()

def stats_from_trees(X:pd.DataFrame, model:BaseEstimator):
    ''' 计算样本记录对应的所有子树预测结果的均值及标准差 '''
    def func(x):
        sr = pd.Series([m.tree_.value[i].squeeze() for m,i in zip(model.estimators_, x)])
        return pd.Series([sr.mean(), sr.std()], index=['mean', 'std'])
    return pd.DataFrame(model.apply(X)).apply(func, axis=1)

def bin_axis(x, n):
    ''' 将坐标轴切分成恰当的区间 '''
    step = float(f'{(x.max() - x.min())/5/(n-1):.2g}')*5
    step = float(f'{step:.2g}')
    min_ = np.floor(x.min()/step) * step
    min_ = min_ if x.min()>min_ else min_- step
    max_ = np.ceil(x.max()/step) * step
    max_ = max_ if x.max()>max_ else max_+step
    bins = pd.cut(x, np.arange(min_, max_, step))
    return bins.apply(lambda x:float(f'{x.mid:.3g}'))

def is_outlier(y, mean, std, r):
    return (y > mean + r*std) | (y < mean - r*std)

def scatter_regressor(
        X:pd.DataFrame, 
        y:Union[pd.Series, list], 
        regr:BaseEstimator, 
        *,
        n:int=50, 
        additional:Optional[List[Tuple[str, str]]]=[], 
        pathname:str=None):
    '''  
    regr : ensemble tree base model
    n : 离群值数
    >>> xcols = ['var_226','var_101', 'var_102', 'var_103', 'var_94', 'var_2709', 'evntemp', 'var_382', 'var_383']
    >>> ycol = ['var_355_mean']
    >>> from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
    >>> from sklearn.tree import DecisionTreeRegressor
    >>> from sklearn.neighbors import LocalOutlierFactor
    >>> from wtbonline._process.modelling import data_filter, get_XY
    >>> from sklearn.preprocessing import MinMaxScaler
    >>> from sklearn.model_selection import GridSearchCV
    >>> from wtbonline._process.model.trainer import BaseTrainer
    >>> kwargs = dict(
    ...     set_id='10050',
    ...     turbine_id='s10001',
    ...     start_time='2022-01-01',
    ...     end_time='2023-04-01',
    ...     )
    >>> raw_df = RSDBInterface.read_statistics_sample(**kwargs)
    >>> inc_df, exclude_df, count_sr = data_filter(raw_df, True, True)
    >>> xcols = '|'.join(xcols)
    >>> X = inc_df.filter(regex=f'^({xcols})_.*', axis=1)
    >>> y = inc_df[ycol]
    >>> X_train, X_test, y_train, y_test = BaseTrainer._train_test_split(X, y)
    >>> grid = {
    ...    'max_depth':[None,3,6,9],
    ...    'min_samples_split':[2,4,6],
    ...    'max_features':['sqrt', 'log2', None], 
    ...    }
    >>> gscv = GridSearchCV(
    ...     RandomForestRegressor(random_state=1), 
    ...     grid, 
    ...     n_jobs=-1
    ...     )
    >>> gscv = gscv.fit(X_train, y_train.squeeze())
    >>> model = gscv.best_estimator_
    >>> X_test = X_test.reset_index(drop=True)
    >>> y_test = y_test.reset_index(drop=True)
    >>> scatter_regressor(X_test, y_test, model, pathname='/home/luo/comp_anormaly.html')
    '''
    X = make_sure_dataframe(X).reset_index(drop=True)
    y = make_sure_series(y).reset_index(drop=True)
    additional = make_sure_list(additional)
    if len(X)<1 and len(y)!=len(X):
        return
    
    if hasattr(regr, 'estimators_'):
        ms_df = stats_from_trees(X, regr)
        ms_df['y'] = y
        ms_df['bin_mean'] = bin_axis(ms_df['mean'], 10)
        ms_df['bin_std'] = bin_axis(ms_df['std'], 10)
        ms_df['diff_abs'] = (ms_df['mean'] - ms_df['y']).abs()
        count_outlier = pd.DataFrame(
            {'count':np.NaN, 'r':np.round(np.arange(0.1,4,0.1),1)}
            )
        count_outlier['count'] = count_outlier['r'].apply(
            lambda x:y[is_outlier(y, ms_df['mean'], ms_df['std'], x)].count()
            )
        count_outlier.set_index('r', drop=False, inplace=True)
        r = count_outlier[count_outlier['count']<=n].index[0]
        outlier_index = y[is_outlier(y, ms_df['mean'], ms_df['std'], r)].index
        
        cols = X.columns[X.columns.str.endswith('_mean')]
        ypred = ms_df['mean']
        nrow = 2 + int(np.ceil((len(cols)+len(additional))/2)) 
    else:
        ypred = pd.Series(regr.predict(X), index=y.index)
        nrow = 1
    target = y.name

    fig = make_subplots(nrow, 2)
    rc = [{'row':i[0], 'col':i[1]} for i in list(product(np.arange(1,nrow+1),[1,2]))]
    i = 0

    fig.add_trace(go.Histogram(x=ypred-y, histnorm='probability'), **rc[i])
    fig.update_xaxes(title='误差 m/s', **rc[i])
    fig.update_yaxes(title='频度', **rc[i])
    i += 1

    fig.add_trace(go.Scatter(x=ypred, y=y, mode='markers',  marker=dict(opacity=0.2)), **rc[i])
    fig.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()] , mode='lines'), **rc[i])
    fig.update_xaxes(title='预测值', **rc[i])
    fig.update_yaxes(title='实际值', **rc[i])
    i += 1

    if hasattr(regr, 'estimators_'):
        fig.add_trace(
            go.Scatter(
            x=count_outlier['r'],
            y=count_outlier['count'], 
            mode='markers+lines', 
            marker=dict(opacity=0.5)), **rc[i]
            )
        fig.add_annotation(
                x=2,
                y=count_outlier.loc[2.0,'count'],
                ayref="y",
                ay=-100,
                text=f"{count_outlier.loc[2.0,'count']}, {count_outlier.loc[2.0,'count']/len(y):.3f}",
                showarrow=True,
                arrowhead=2,
                **rc[i]
                )
        fig.add_annotation(
                x=3,
                y=count_outlier.loc[3.0,'count'],
                text=f"{count_outlier.loc[3.0,'count']}, {count_outlier.loc[3.0,'count']/len(y):.3f}",
                showarrow=True,
                arrowhead=2,
                **rc[i]
                )
        fig.update_xaxes(title='标准差倍数', **rc[i])
        fig.update_yaxes(title='离群值计数', **rc[i])
        i += 1

        fig.add_trace(
            go.Heatmap(
                x=ms_df['bin_mean'].unique().sort_values(),
                y=ms_df['bin_std'].unique().sort_values(),
                z=pd.pivot_table(ms_df, values='mean', index=['bin_mean'], columns='bin_std', aggfunc=len),
                showscale=False
                ),
            **rc[i]
            )
        fig.update_xaxes(title='预测值', **rc[i])
        fig.update_yaxes(title='预测值方差', **rc[i])
        i += 1

        for col in cols:
            fig.add_trace(
                go.Scatter(
                    x=X[col], 
                    y=y,
                    marker=dict(color='gray', size=2, opacity=0.2), 
                    mode='markers'), 
                **rc[i]
                )
            fig.add_trace(
                go.Scatter(
                    x=X.loc[outlier_index, col], 
                    y=y.loc[outlier_index], 
                    mode='markers', 
                    marker={'color':'red', 'size':3}
                    ), 
                **rc[i]
                )
            fig.update_xaxes(title=col, **rc[i])
            fig.update_yaxes(title=target, **rc[i])
            i += 1

        for xcol, ycol in additional:
            fig.add_trace(
                go.Scatter(
                    x=X[xcol], 
                    y=X[ycol],
                    marker=dict(color='gray', size=2, opacity=0.2), 
                    mode='markers'), 
                **rc[i]
                )
            fig.add_trace(
                go.Scatter(
                    x=X.loc[outlier_index, xcol], 
                    y=X.loc[outlier_index, ycol], 
                    mode='markers', 
                    marker={'color':'red', 'size':3}
                    ), 
                **rc[i]
                )
            fig.update_xaxes(title=xcol, **rc[i])
            fig.update_yaxes(title=ycol, **rc[i])
            i += 1        

    fig.update_layout(
        width=1000, 
        height=max(200*nrow, 500), 
        title=f'预测变量及得分：{target} - {regr.score(X, y):.2g}', 
        margin=dict(l=80, r=80, t=80, b=80), 
        showlegend=False
        )
    if pathname is not None:
        fig.write_html(pathname)
    else:
        fig.show()

# %% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()