# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

建模基类，封装了数准备过程
"""

#%% import 
import pandas as pd
import numpy as np
from typing import List, Mapping, Any, Callable, Union
from sklearn.dummy import DummyClassifier
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

from wtbonline._common.utils import make_sure_dataframe, make_sure_list
from wtbonline._process.model.trainer import trainer_factory


#%% class
class Base():
    '''
    >>> X = [-1, 1, 1, 1]
    >>> y = [ 0, 1, 1, 1]
    >>> df = pd.DataFrame({'x':X,'y':y})
    >>> b = Base(minimum=0, test_size=0)
    >>> b.set_features(features='x', target='y')
    >>> b.fit(df)
    >>> b.predict({'x':X})
    array([1, 1, 1, 1])
    '''
    def __init__(self, estimator=DummyClassifier(), filter:List[Callable]=None, scaler=None, trainer:str='simple', **kwargs) -> None:
        self.filter = make_sure_list(filter)
        self.trainer = trainer_factory(trainer, **kwargs)
        self.scaler = scaler
        self.estimator = estimator
        
    def set_features(self, features:List[str], target:List[str]=None):
        self.features = make_sure_list(features)
        self.target = make_sure_list(target)
        self.columns = pd.Series(self.features + self.features).drop_duplicates()
    
    def _check(self, df:pd.DataFrame):
        cols = self.columns[~self.columns.isin(df.columns)]
        if len(cols)>0:
            raise ValueError(f'input data lack of columns : {cols}')
    
    def _filter(self, df:pd.DataFrame):
        df = make_sure_dataframe(df)
        cond = pd.Series([True]*len(df))
        for func in self.filter:
            cond = cond & func(df)
        df = df[cond]   
        if len(df)<0:
            raise ValueError('df is empty after filtering.')
        return df

    def _seperate(self, df):
        X = df[self.features]
        y = df[self.target] if len(self.target)>0 and pd.Series(self.target).isin(df.columns).all() else None    
        return X, y

    def _scale(self, X:pd.DataFrame):
        try:
            check_is_fitted(self.scaler)
        except NotFittedError as exc:
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)
        return X
            
    def fit(self, df:pd.DataFrame, **kwargs):
        self._check(df)
        df = self._filter(df)
        X, y = self._seperate(df)
        X = self._scale(X)
        self.estimator = self.trainer.fit(estimator=self.estimator, X=X, y=y, **kwargs)
    
    def predict(self, df:pd.DataFrame):
        # 不做filter，方便调用函数对dataframe进行赋值
        self._check(df)
        X, _ = self._seperate(df)
        X = self._scale(X)
        return self.estimator.predict(X)

    def score_samples(self, df:pd.DataFrame, **kwargs):
        # 不做filter，方便调用函数对dataframe进行赋值
        if not hasattr(self.estimator, 'score_samples'):
            raise AttributeError(f'estimator {self.estimator} do not have member function "score_samples"')
        self._check(df)
        X, _ = self._seperate(df)
        X = self._scale(X)
        return self.estimator.score_samples(X)

Classifier = Base

# main
if __name__ == "__main__":
    import doctest
    doctest.testmod()