# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

建模与异常值识别
"""

#%% import 
from pathlib import Path
import pandas as pd
from typing import Union, List, Optional
from functools import partial
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from functools import partial
from datetime import date
import plotly.graph_objects as go
 
from wtbonline._db.config import get_temp_dir
from wtbonline._process.model.trainer import SimpleTrainer
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.common import make_sure_list
from wtbonline._process.tools.plot import scatter_anormaly, scatter_regressor
from wtbonline._logging import get_logger, log_it

#%% constant
_LOGGER = get_logger('modelling')

OUTPATH = RSDBInterface.read_app_configuration(key_='model_path')['value'].squeeze()
OUTPATH = Path(OUTPATH)
OUTPATH.mkdir(exist_ok=True)

#%% function
def data_filter(df, return_exclude=False, return_count=False):
    ''' 剔除不能用于训练模型的数据 '''
    cnt_dct = {}
    conds = True

    condtion = df['pv_c']<0.001
    cnt_dct.update({'非平稳':df[~condtion].shape[0]})
    conds = conds & condtion

    condtion = (df['limitpowbool_mode']=='False') & (df['limitpowbool_nunique']==1)
    cnt_dct.update({'限电':df[~condtion].shape[0]})
    conds = conds & condtion

    condtion = (df['workmode_mode']=='32') & (df['workmode_nunique']==1)
    cnt_dct.update({'非发电':df[~condtion].shape[0]})
    conds = conds & condtion
    
    condtion = (df['ongrid_mode']=='True') & (df['ongrid_nunique']==1)
    cnt_dct.update({'非并网':df[~condtion].shape[0]})
    conds = conds & condtion

    condtion = (df['totalfaultbool_mode']=='False') & (df['totalfaultbool_nunique']==1)
    cnt_dct.update({'有故障':df[~condtion].shape[0]})
    conds = conds & condtion

    condtion = df['validation']==0
    cnt_dct.update({'没通过传感器校验':df[~condtion].shape[0]})
    conds = conds & condtion

    rev = df[conds] if return_exclude==False else [df[conds], df[~conds]]
    rev = rev if return_count==False else make_sure_list(rev) + [pd.Series(cnt_dct)]
    return rev

def get_XY(df, xcols:List[str], ycols:Union[List[str], str]):
    '''
    xcols : 特征前缀。通过给定前缀，选出相关特征。特征以下划线加统计量命名，如xxx_mean, xxx_std。
    ycols : 应变量特征名，全称，非前缀。
    >>> set_id='20835'
    >>> turbine_id='s10001'
    >>> start_time='2023-05-01'
    >>> end_time='2023-06-01'
    >>> df = RSDBInterface.read_statistics_sample(
    ...     set_id=set_id, 
    ...     turbine_id=turbine_id, 
    ...     start_time=start_time, 
    ...     end_time=end_time
    ...     )
    >>> x, y = get_XY(df, ['var_226', 'var_101'], 'var_355_mean')
    >>> len(x)>0
    True
    >>> y.squeeze().name=='var_355_mean'
    True
    >>> x, y = get_XY(df, ['var_101_mean', 'var_226_mean'], None)
    >>> x.columns.tolist() == ['var_101_mean', 'var_226_mean']
    True
    >>> y is None
    True
    '''
    xcols = make_sure_list(xcols)
    ycols = make_sure_list(ycols)
    xcols = '|'.join(xcols)
    X = df.filter(regex=f'^({xcols}).*', axis=1)
    y = None if len(ycols)==0 else df[ycols]
    return X, y 

def get_trainers():
    '''
    >>> type(get_trainers())
    <class 'dict'>
    '''
    trainer_dct={}

    xcols = ['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean']
    ycols = None
    clf = LocalOutlierFactor(
        novelty=True,
        contamination=0.01, 
        n_neighbors=200
        )
    pl = Pipeline([('scaler', MinMaxScaler()),('clf', clf)])
    trainer = SimpleTrainer(estimator=pl,
        data_filter=data_filter, 
        get_XY=partial(get_XY, xcols=xcols, ycols=ycols),
        test_size=0,
        train_test_split=None,
        outpath=OUTPATH,
        )
    kwargs = {}
    trainer_dct.update({'lof_ctrl':(trainer, kwargs)})
    
    xcols = ['var_382_mean', 'var_383_mean']
    ycols = None
    clf = LocalOutlierFactor(
        novelty=True,
        contamination=0.01, 
        n_neighbors=200
        )
    trainer =  SimpleTrainer(
        estimator=clf,
        data_filter=data_filter, 
        get_XY=partial(get_XY, xcols=xcols, ycols=ycols),
        test_size=0,
        train_test_split=None,
        outpath=OUTPATH,
        )
    kwargs = {}
    trainer_dct.update({'lof_vibr':(trainer, kwargs)})
    
    xcols = ['var_226','var_101', 'var_102', 'var_103', 'var_94', 'var_2709', 'evntemp']
    ycols= ['var_355_mean']
    trainer = SimpleTrainer(
        estimator=RandomForestRegressor(),
        data_filter=data_filter, 
        get_XY=partial(get_XY, xcols=xcols, ycols=ycols),
        train_test_split=None,
        outpath=OUTPATH,
        )
    kwargs = {
        'param_grid':{
            'max_depth':[None,3,6,9],
            'min_samples_split':[2,4,6],
            'max_features':['sqrt', 'log2', None], 
            }
        }
    trainer_dct.update({'rf':(trainer, kwargs)})

    return trainer_dct


def train(
    farm_name:str,
    set_id:str,
    turbine_id:Union[str, List[str]],
    start_time:Optional[Union[str, pd.Timedelta]]=None,
    end_time:Optional[Union[str, pd.Timedelta]]=None, 
    uuids_:List[str]=None,
    selects=['lof_ctrl', 'lof_vibr'],
    minimum:int=8000,
    logger=None,
    ):
    ''' 从statistic_sample中读取数据训练模型
    start_time : bin开始时间
    end_time : bin结束时间
    >>> set_id='20835'
    >>> turbine_id='s10001'
    >>> start_time='2023-01-01'
    >>> end_time='2024-01-01'
    >>> farm_name='bozhong'
    >>> uuids_=['lof_ctrl','lof_vibr']
    >>> train(
    ...     farm_name=farm_name, 
    ...     set_id=set_id, 
    ...     turbine_id=turbine_id,
    ...     start_time=start_time, 
    ...     end_time=end_time,
    ...     uuids_=uuids_,
    ...     minimum=3000
    ...     )
    >>> len(RSDBInterface.read_model(uuid='lof_ctrl'))>0
    True
    >>> len(RSDBInterface.read_model(uuid='lof_vibr'))>0
    True
    >>> RSDB.delete('model', in_clause={'uuid':['lof_ctrl', 'lof_vibr']})
    >>> (OUTPATH/'lof_ctrl.pkl').unlink()
    >>> (OUTPATH/'lof_vibr.pkl').unlink()
    '''
    trainer_dct = get_trainers()
    uuids_ = make_sure_list(uuids_)
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, 
        turbine_id=turbine_id, 
        start_time=start_time, 
        end_time=end_time
        )
    entity = {
        'farm_name':farm_name,
        'set_id':set_id,
        'turbine_id':turbine_id,
        'start_time':start_time,
        'end_time':end_time,
        }
    for i, key_ in enumerate(selects):
        uuid_ = None if len(uuids_)==0 else uuids_[i] 
        trainer, kwargs = trainer_dct[key_]
        trainer.train(
            df, 
            kwargs=kwargs, 
            description=entity, 
            uuid_=uuid_,
            minimum=minimum,
            logger=logger
            )
        if trainer.finished:
            trainer.save_model()
            this_entity = entity.copy()
            this_entity.update({
                'name':key_, 
                'create_time':pd.Timestamp.now(),
                'uuid':trainer.estimator.description['uuid']
                })
            RSDB.delete('model', eq_clause={'uuid':trainer.estimator.description['uuid']})
            RSDB.insert(this_entity, 'model')
        else:
            logger.warn(f'模型训练失败: {set_id} {turbine_id} {start_time} {end_time} {selects} {minimum}')

@log_it(_LOGGER,True)
def train_all(*args, **kwargs):
    '''
    train_all(start_time='2023-01-01', end_time='2024-04-01')
    '''
    if kwargs['end_time'] is not None and kwargs['end_time']!='':
        end_time = pd.to_datetime(kwargs['end_time'])
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    
    conf_df = RSDBInterface.read_windfarm_configuration()[['set_id', 'turbine_id']]
    farm_name = RSDBInterface.read_windfarm_infomation()['farm_name'].iloc[0]
    for _, row in conf_df.iterrows():
        _LOGGER.info(f"train {row['set_id']} {row['turbine_id']}")
        train(
            farm_name=farm_name,
            set_id=row['set_id'],
            turbine_id=row['turbine_id'],
            start_time=start_time,
            end_time=end_time,
            minimum=kwargs.get('minimum', 3000),
            logger=_LOGGER
            )

def predict(
        uuids, 
        set_id, 
        turbine_id, 
        start_time, 
        end_time, 
        size, 
        model_uuid=None,
        ):
    '''
    >>> set_id='20835'
    >>> turbine_id='s10001'
    >>> start_time='2023-01-01'
    >>> end_time='2024-01-01'
    >>> farm_name='bozhong'
    >>> uuids_=['lof_ctrl','lof_vibr']
    >>> model_uuid='test'
    >>> size=20
    >>> train(
    ...     farm_name=farm_name, 
    ...     set_id=set_id, 
    ...     turbine_id=turbine_id,
    ...     start_time=start_time, 
    ...     end_time=end_time,
    ...     uuids_=uuids_,
    ...     minimum=3000
    ...     )
    >>> predict(uuids_, set_id, turbine_id, start_time, end_time, size, model_uuid)
    >>> len(RSDBInterface.read_model_anormaly(model_uuid='test'))>0
    True
    >>> RSDB.delete('model_anormaly', eq_clause={'model_uuid':'test'})
    '''
    uuids = make_sure_list(uuids)
    data_df = RSDBInterface.read_statistics_sample(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time
        )
    anomaly_df=[]
    for uuid in uuids:
        model_sr = RSDBInterface.read_model(uuid=uuid).squeeze()
        assert len(model_sr)>0, f'查无记录 uuid={uuid}'
        trainer = get_trainers()[model_sr['name']][0]
        pathname = OUTPATH/f'{uuid}.pkl'
        clf = trainer.load_model(pathname)
        trainer.train(data_df, only_value=True, test_size=0)
        X = trainer.X_train
        scores = pd.Series(clf.score_samples(X), index=X.index)
        idxes = scores.sort_values().head(size).index
        anomaly_df.append(data_df.loc[idxes,['set_id', 'turbine_id', 'id', 'bin']])
    anomaly_df = pd.concat(anomaly_df, ignore_index=True)
    anomaly_df.rename(columns={'id':'sample_id'}, inplace=True)
    anomaly_df.drop_duplicates(['sample_id'], inplace=True)
    anomaly_df['model_uuid'] = ','.join(uuids) if model_uuid is None else model_uuid 
    anomaly_df['create_time'] = pd.Timestamp.now()
    RSDBInterface.insert(anomaly_df, 'model_anormaly')

@log_it(_LOGGER, True)
def predict_all(*args, **kwargs):
    '''
    predict_all(start_time='2022-01-01', end_time='2023-04-01')
    '''
    if kwargs['end_time'] is not None and kwargs['end_time']!='':
        end_time = pd.to_datetime(kwargs['end_time']) 
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    
    model_df = RSDBInterface.read_model(
        name=['lof_ctrl', 'lof_vibr'],
        func_dct={'create_time':['max']},
        groupby=['set_id', 'turbine_id', 'name'],
        ).rename(columns={'create_time_max':'create_time'})
    model_df = RSDBInterface.read_model(
        **{i:model_df[i].unique().tolist() for i in model_df}
        )
    for (sid,tid),grp in model_df.groupby(['set_id', 'turbine_id']):
        predict(
            uuids=grp['uuid'], 
            set_id=sid, 
            turbine_id=tid, 
            start_time=start_time, 
            end_time=end_time,
            size=kwargs.get('size', 20)
            )

def test_train(uuids_, start_time, end_time):
    '''
    uuid : 模型的uuid
    用于检查检查train生成的模型
    uuids_=['lof_ctrl','lof_vibr']
    start_time='2023-01-01'
    end_time='2023-12-01' 
    test_train(uuids_, start_time, end_time)
    '''
    farm_name = 'test'
    minimun=3000
    conf_sr = RSDBInterface.read_windfarm_configuration().iloc[0]
    set_id=conf_sr['set_id']
    turbine_id=conf_sr['turbine_id']
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, turbine_id=turbine_id, start_time=start_time, end_time=end_time, 
        )
    train_df, test_df = df, df
    # manual
    for uu in uuids_:
        trainer, kwargs = get_trainers()[uu]
        trainer.train(
            train_df, 
            kwargs=kwargs, 
            uuid_='test',
            minimun=minimun,
            )
        pathname = get_temp_dir()/f'manual_{uu}.pkl'
        trainer.save_model(pathname=pathname)
        plot(trainer, test_df, pathname, f'manual_{uu}')

    # auto
    train(
         farm_name=farm_name, 
         set_id=set_id, 
         turbine_id=turbine_id,
         start_time=start_time, 
         end_time=end_time,
         uuids_=uuids_,
         minimun=minimun
         )   
    p = RSDBInterface.read_app_configuration(key_='model_path')['value'].squeeze()
    p = Path(p) 
    for uu in uuids_:
        trainer, kwargs = get_trainers()[uu]
        pathname = p/f'{uu}.pkl'
        plot(trainer, test_df, pathname, f'auto_{uu}')
        pathname.unlink()
    RSDB.delete('model', in_clause={'uuid':uuids_})

def test_predict(uuids_, start_time, end_time):
    '''
    model_uuid : 模型的uuid或组合, 形式：','.joind(uuids)
    用于检查检查train生成的模型
    uuids_=['lof_ctrl','lof_vibr']
    start_time='2023-01-01'
    end_time='2023-12-01' 
    test_predict(uuids_, start_time, end_time)
    '''
    size=20
    farm_name = 'test'
    minimun=3000
    conf_sr = RSDBInterface.read_windfarm_configuration().iloc[0]
    set_id=conf_sr['set_id']
    turbine_id=conf_sr['turbine_id']
    model_uuid = ','.join(uuids_)
    train(
         farm_name=farm_name, 
         set_id=set_id, 
         turbine_id=turbine_id,
         start_time=start_time, 
         end_time=end_time,
         uuids_=uuids_,
         minimun=minimun
         ) 
    predict(uuids_, set_id, turbine_id, start_time, end_time, size)
    
    all_df = RSDBInterface.read_statistics_sample(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        ).set_index('id')
    anormaly_df = RSDBInterface.read_model_anormaly(
        model_uuid=model_uuid,
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        )
    all_df = data_filter(all_df)
    all_df['is_anormaly'] = False
    all_df.loc[anormaly_df['sample_id'], 'is_anormaly'] = True
    a = all_df[all_df['is_anormaly']==False]
    a = a if len(a)<4001 else a.sample(4000)
    b = all_df[all_df['is_anormaly']==True]
    sub_df = all_df.loc[a.index.tolist() + b.index.tolist()]
    fig = scater_matrix_anormaly(sub_df)
    fig.write_html(get_temp_dir()/'test_predict.html')

def plot(trainer, test_df, pathname, filename):
    test_df = test_df.copy()
    trainer.train(
        test_df, 
        kwargs={}, 
        uuid_='test',
        only_value=True,
        test_size=0
        )
    X = trainer.X_train
    clf = trainer.load_model(pathname)
    X['score'] = clf.score_samples(X)
    X['is_anormaly'] = 1
    X.loc[X.sort_values('score').head(20).index, 'is_anormaly']=-1
    a = X[X['is_anormaly']==1]
    a = a if len(a)<4001 else a.sample(4000)
    b = X[X['is_anormaly']==-1]
    sub_df = test_df.loc[a.index.tolist() + b.index.tolist()].copy()
    sub_df['is_anormaly'] = False
    sub_df.loc[b.index, 'is_anormaly'] = True
    fig = scater_matrix_anormaly(sub_df)
    fig.write_html(get_temp_dir()/f'{filename}.html')

def scater_matrix_anormaly(df):
    # 绘图
    # df['is_anormaly'] 为布尔量
    size = df['is_anormaly'].astype('category').cat.codes
    size = size.replace(0, 1)
    size = size.replace(1, 3)
    color = df['is_anormaly'].astype('category').cat.codes
    color = color.replace(0, 'blue')
    color = color.replace(1, 'red')
    opacity = df['is_anormaly'].astype('category').cat.codes
    opacity = opacity.replace(0, 0.2)
    fig = go.Figure(
        data=go.Splom(
            dimensions=[dict(label='风速',
                                values=df['var_355_mean']),
                        dict(label='湍流度',
                                values=df['var_355_std']/df['var_355_mean']),
                        dict(label='叶轮转速',
                                values=df['var_94_mean']),
                        dict(label='发电机扭矩',
                                values=df['var_226_mean']),
                        dict(label='1#叶片桨距角',
                                values=df['var_101_mean']),
                        dict(label='风向角',
                                values=df['var_2709_mean']),
                        dict(label='电网有功功率',
                                values=df['var_246_mean']),
                        dict(label='机舱x方向振动',
                                values=df['var_382_mean']),
                        dict(label='机舱y方向振动',
                                values=df['var_383_mean']),
                        ],
            showupperhalf=False, # remove plots on diagonal
            text=df['is_anormaly'],
            marker=dict(color=color,
                        showscale=False, # colors encode categorical variables
                        line_color='white', 
                        line_width=0.1,
                        size=size,
                        opacity=opacity)
            )
        )
    return fig


# #%% main
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()