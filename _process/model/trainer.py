# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

机器学习建模
"""

# import 
import pandas as pd
from typing import List, Mapping, Any, Callable
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator
import pickle
import uuid
import os
from pathlib import Path

from wtbonline._db.common import make_sure_dataframe, make_sure_dict

class BaseTrainer():
    def __init__(
            self, 
            estimator:BaseEstimator, 
            *,
            data_filter:Callable=None,
            get_XY:Callable=None,
            train_test_split:Callable=None,
            test_size=0.3,
            outpath=None
            ):
        self.estimator = estimator
        if outpath==None:
            self.outpath = os.path.dirname(os.path.abspath(__file__))+'/model'
        else:
            self.outpath = outpath
        self.data_filter = self._data_filter if data_filter is None else data_filter
        self.get_XY = self._get_XY if get_XY is None else get_XY
        self.train_test_split = self._train_test_split if train_test_split is None else train_test_split
        self.test_size = test_size
        self.reset()

    def reset(self):
        self.pathname = None
        self.finished = False
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None  
    
    def _data_filter(self,df:pd.DataFrame)->pd.DataFrame:
        ''' 过滤用于训练模型的数据 '''
        return df
    
    def _get_XY(self,df:pd.DataFrame)->List[pd.DataFrame]:
        ''' 构造X，y数据集 
        X,y = self.filter(df)
        '''
        columns = df.columns[df.columns != 'target']
        return df[columns], df[['target']]

    def save_model(self, *, _model=None, pathname=None):
        '''
        >>> from sklearn.dummy import DummyRegressor
        >>> from sklearn.preprocessing import MaxAbsScaler
        >>> clf = DummyRegressor()
        >>> trainer = BaseTrainer(clf)
        >>> setattr(clf, 'description', {'uuid':'test'})
        >>> pathname = trainer.save_model(_model=clf, pathname='/tmp/test.pkl')
        >>> Path(pathname).unlink()
        '''
        model = self.estimator if _model is None else _model
        if model is None:
            return
        
        filename = model.description['uuid']
        pathname = f'{self.outpath }/{filename}.pkl' if pathname is None else pathname
        Path(pathname).unlink(missing_ok=True)
        with open(pathname, 'wb') as fd:
            pickle.dump(model, fd)

        if model is not None:
            self.pathname = pathname
        return pathname
    
    def load_model(self, pathname:str=None):
        with open(pathname, 'rb') as fd:
            model = pickle.load(fd)
        return model

    @classmethod
    def _train_test_split(clf, X, y, test_size=0.3, random_state=1, shuffle=False):
        X = make_sure_dataframe(X)
        y = make_sure_dataframe(y)
        if test_size>0:
            if len(y)>0:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state, shuffle=shuffle
                    )
            else:
                X_train, X_test = train_test_split(
                    X, test_size=test_size, random_state=random_state, shuffle=shuffle
                    )
                y_train = y_test = None
        else:
            X_train = X
            y_train = y
            X_test = pd.DataFrame(columns=X_train.columns)
            y_test = pd.DataFrame(columns=y_train.columns)
        return X_train, X_test, y_train, y_test

    def _fit(self, kwargs):
        raise NotImplementedError()

    def train(
        self,
        df:pd.DataFrame,
        *,
        kwargs:Mapping[str,Any]={},
        uuid_:str=None,
        description:Mapping[str, str]={},
        minimum:int=8000,
        target:str=None,
        only_value=False,
        test_size=None,
        logger=None
        ):
        if len(df)<minimum and only_value==False:
            if logger is not None:
                logger.warn(f'at least {minimum} entities need for trainning after filtering')
            return
        df = df.copy()
        df = self.data_filter(df)
        if len(df)<minimum and only_value==False:
            if logger is not None:
                logger.warn(f'at least {minimum} entities need for trainning after filtering')
            return
        test_size = self.test_size if test_size is None else test_size
        X, y = self.get_XY(df)
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test_split(
            X, y, test_size=test_size, random_state=1, shuffle=False
            )
        if only_value==True:
            return

        self._fit(kwargs)
        y = make_sure_dataframe(y)
        if target is None:
            if len(y)==0:
                target = ''
            else:
                target = y.columns.tolist()
        description = make_sure_dict(description).copy()
        description.update({
            'feature':X.columns.tolist(),
            'target':target,
            'uuid':uuid_ if uuid_ is not None else f'{uuid.uuid1()}',
            'train_time':pd.Timestamp.now(),
            'test_size':self.test_size,
            })
        setattr(self.estimator, 'description', description)
        self.finished = True

class SimpleTrainer(BaseTrainer):
    def __init__(
            self, 
            estimator:BaseEstimator, 
            *,
            data_filter:Callable=None,
            get_XY:Callable=None,
            train_test_split:Callable=None,
            outpath=None,
            test_size=0.3
            ):
        super().__init__(
            estimator, data_filter=data_filter, get_XY=get_XY,
            train_test_split=train_test_split, outpath=outpath, test_size=test_size)
        
    def _fit(self, kwargs={}):
        '''
        >>> from sklearn.tree import DecisionTreeRegressor
        >>> from sklearn.datasets import load_diabetes
        >>> dset = load_diabetes()
        >>> df = pd.DataFrame(dset['data'], columns=dset['feature_names'])
        >>> df['target'] = dset['target']
        >>> trainer = SimpleTrainer(DecisionTreeRegressor())
        >>> kwargs = {
        ...     'param_grid':{
        ...         'max_depth':[None,3,6,9],
        ...         'min_samples_split':[2,4,6],
        ...         'max_features':['sqrt', 'log2', None], 
        ...         }
        ...    }
        >>> trainer.train(df, kwargs=kwargs, uuid_='test', minimun=10)
        >>> pathname = trainer.save_model()
        >>> Path(trainer.pathname).unlink()
        '''
        y_train = make_sure_dataframe(self.y_train)
        if len(y_train)>0:
            gscv = GridSearchCV(self.estimator, n_jobs=-1, **kwargs)
            gscv.fit(self.X_train, self.y_train.squeeze())
            self.estimator = gscv.best_estimator_
        else:
            self.estimator.fit(self.X_train, **kwargs)
        
# from autosklearn.regression import AutoSklearnRegressor
# class SMBOTrainer(BaseTrainer):
#     def __init__(
#             self, 
#             estimator:BaseEstimator, 
#             *,
#             data_filter:Callable=None,
#             get_XY:Callable=None,
#             train_test_split:Callable=None,
#             outpath=None,
#             test_size=0.3,
#             ):
#         super().__init__(
#             estimator, data_filter=data_filter, get_XY=get_XY,
#             train_test_split=train_test_split, outpath=outpath, test_size=test_size)

#     def _fit(self, kwargs):
#         '''
#         >>> from sklearn.datasets import load_diabetes
#         >>> dset = load_diabetes()
#         >>> df = pd.DataFrame(dset['data'], columns=dset['feature_names'])
#         >>> df['target'] = dset['target']
#         >>> kwargs={'time_left_for_this_task':30}
#         >>> trainer = SMBOTrainer(AutoSklearnRegressor(**kwargs))
#         >>> trainer.train(df, uuid_='test', minimun=10)
#         >>> pathname = trainer.save_model()
#         >>> Path(trainer.pathname).unlink()
#         '''
#         self.estimator.fit(
#             self.X_train, 
#             self.y_train, 
#             self.X_test, 
#             self.y_test,
#             **kwargs
#             )

# main
if __name__ == "__main__":
    import doctest
    doctest.testmod()