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
    def __init__(self, estimator=DummyClassifier(), filter:List[Callable]=None, scalar=None, trainer:str='simple', **kwargs) -> None:
        self.filter = make_sure_list(filter)
        self.scalar = scalar
        self.trainer = trainer_factory(trainer, **kwargs)
        self.estimator = estimator
        
    def set_features(self, features:List[str], target:List[str]=None):
        self.features = make_sure_list(features)
        self.target = make_sure_list(target)
    
    def _filter(self, df:pd.DataFrame):
        df = make_sure_dataframe(df)
        cond = pd.Series([True]*len(df))
        for func in self.filter:
            cond = cond & func(df)
        df = df[cond]   
        if len(df)<0:
            raise ValueError('df is empty after translation.')
        X = df[self.features]
        y = df[self.target] if len(self.target)>0 and pd.Series(self.target).isin(df.columns).all() else None
        return X, y
            
    def fit(self, df:pd.DataFrame, **kwargs):
        X, y = self._filter(df)
        if self.scalar is not None:
            X = self.scalar.fit_transform(X)
        self.estimator = self.trainer.fit(estimator=self.estimator, X=X, y=y, **kwargs)
    
    def predict(self, df:pd.DataFrame):
        X, _ = self._filter(df)
        if self.scalar is not None:
            X = self.scalar.transform(X)
        return self.estimator.predict(X)

Classifier = Base

# main
if __name__ == "__main__":
    import doctest
    doctest.testmod()