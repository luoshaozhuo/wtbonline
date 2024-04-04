# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

用于模型训练的类
"""

# import 
import pandas as pd
from typing import List, Mapping, Any, Callable
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier

from wtbonline._common.utils import make_sure_dataframe

class BaseTrainer():
    '''
    >>> X = [-1, 1, 1, 1]
    >>> y = [ 0, 1, 1, 1]
    >>> trainer = BaseTrainer(test_size=0)
    >>> clf = DummyClassifier(strategy="most_frequent")
    >>> clf = trainer.fit(clf, X, y)
    >>> clf.predict(X)
    array([1, 1, 1, 1])
    '''
    def __init__(
            self, 
            train_test_split:Callable=None,
            minimum=0,
            test_size=0.3,
            ):
        self.train_test_split = self._train_test_split if train_test_split is None else train_test_split
        self.test_size = test_size
        self.minimum = minimum

    def _train_test_split(self, X, y, test_size, random_state=1, shuffle=False):
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

    def _fit(self, estimator, X_train, y_train, **kwargs):
        return estimator.fit(X_train, y_train)

    def fit(self, estimator, X, y=None, **kwargs):
        if len(X)<self.minimum:
            raise ValueError(f'at least {self.minimum} entities need for trainning, given {len(X)}')
        X_train, X_test, y_train, y_test = self.train_test_split(
            X, y, test_size=self.test_size, random_state=1, shuffle=False
            )
        return self._fit(estimator, X_train, y_train, **kwargs)

class GridCVTrainer(BaseTrainer):
    '''
    >>> X = [-1, 1, 1, 1]*5
    >>> y = [ 0, 1, 1, 1]*5
    >>> trainer = GridCVTrainer(test_size=0)
    >>> clf = DummyClassifier()
    >>> clf = trainer.fit(clf, X,y,param_grid={'strategy':['most_frequent', 'uniform']})
    >>> clf.predict([-1, 1, 1, 1])
    array([1, 1, 1, 1])
    '''     
    def _fit(self, estimator, X_train, y_train, **kwargs):
        param_grid=kwargs.get('param_grid', {})
        gscv = GridSearchCV(estimator, param_grid=param_grid, n_jobs=-1)
        _ = gscv.fit(X_train, y_train)
        return gscv.best_estimator_

def trainer_factory(type_='simple', **kwargs):
    '''
    >>> X = [-1, 1, 1, 1]*5
    >>> y = [ 0, 1, 1, 1]*5
    >>> trainer = trainer_factory(type_='gridcv', test_size=0)
    >>> clf = DummyClassifier()
    >>> clf = trainer.fit(clf, X,y,param_grid={'strategy':['most_frequent', 'uniform']})
    >>> clf.predict([-1, 1, 1, 1])
    array([1, 1, 1, 1])
    '''    
    dct = dict(
        simple=BaseTrainer(**kwargs),
        gridcv=GridCVTrainer(**kwargs),
        )
    rev = dct.get(type_, None)
    if rev is None:
        raise ValueError(f"不支持的trainer类型'{type_}', 必须为一下类型之一{list(dct.keys())}")
    return rev
    
# main
if __name__ == "__main__":
    import doctest
    doctest.testmod()