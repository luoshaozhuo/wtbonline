from pathlib import Path
from typing import Union, List
from functools import partial
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from functools import partial

from wtbonline._process.model.trainer import SimpleTrainer
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.common import make_sure_list
from wtbonline._process.tools.filter import filter_for_modeling
from wtbonline._logging import get_logger

#%% constant
_LOGGER = get_logger('modelling')

OUTPATH = RSDBInterface.read_app_configuration(key_='model_path')['value'].squeeze()
OUTPATH = Path(OUTPATH)
OUTPATH.mkdir(exist_ok=True)


#%% function

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
        data_filter=filter_for_modeling, 
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
        data_filter=filter_for_modeling, 
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
        data_filter=filter_for_modeling, 
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