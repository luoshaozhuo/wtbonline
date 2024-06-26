# -*- coding: utf-8 -*-
"""
Created on Thur July 27 16:03:00 2023

@author: luosz

机器学习建模
"""

#%% import 
import pandas as pd
import uuid
import numpy as np
from pathlib import Path
import pickle
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import MinMaxScaler, Normalizer, MaxAbsScaler

from wtbonline._process.model.base import Classifier
from wtbonline._process.tools.filter import stationary,not_limit_power,in_power_generating_mode,no_fault,on_grid
from wtbonline._common.utils import make_sure_dataframe

#%% class
class Anomaly():
    '''
    >>> from wtbonline._db.tsdb_facade import TDFC
    >>> from wtbonline._db.rsdb_facade import RSDBFacade
    >>> estimater = Anomaly()
    >>> df = RSDBFacade.read_statistics_sample(
    ...    set_id='20625',
    ...    device_id='d10003',
    ...    start_time='2023-01-01',
    ...    end_time='2024-04-01',
    ...    columns=estimater.columns
    ...    )
    >>> estimater.fit(df)
    >>> _ = estimater.save_model('/tmp/')
    '''
    def __init__(self, contamination=0.01, minimum=0, test_size=0.3):
        self.filter = [stationary, not_limit_power, in_power_generating_mode, no_fault, on_grid]
        
        vars_ctrl = ['var_94_mean', 'winspd_mean', 'var_226_mean', 'var_101_mean']
        estimator = IsolationForest(
            contamination=contamination, 
            n_estimators=200,
            max_samples=1.0
            )
        self.lof_ctrl = Classifier(
            estimator=estimator, 
            filter=self.filter, 
            scaler=MinMaxScaler(), 
            minimum=minimum, 
            test_size=test_size, 
            trainer='simple'
            )
        self.lof_ctrl.set_features(features=vars_ctrl)
        
        vars_vibr = ['var_382_mean', 'var_383_mean']
        estimator = LocalOutlierFactor(
            contamination=contamination, 
            n_neighbors=20,
            novelty=True,
            )
        self.lof_vibr = Classifier(
            estimator=estimator, 
            filter=self.filter, 
            scaler=MinMaxScaler(),
            minimum=minimum, 
            test_size=test_size,
            trainer='simple'
            )
        self.lof_vibr.set_features(features=vars_vibr)
        
        self.uuid = None
        self.features = vars_ctrl + vars_vibr
        self.target = []
        cols_aug = [
            'pv_c', 
            'limitpowbool_mode', 
            'limitpowbool_nunique', 
            'workmode_mode', 
            'workmode_nunique', 
            'totalfaultbool_mode', 
            'totalfaultbool_nunique', 
            'ongrid_mode', 
            'ongrid_nunique'
            ]
        self.columns = self.features + cols_aug # 本模型需要用到的所有字段
        
    def fit(self, df:pd.DataFrame):
        self.lof_ctrl.fit(df)
        self.lof_vibr.fit(df)
        self.uuid = uuid.uuid1()
    
    def predict(self, df:pd.DataFrame):
        y1 = self.lof_ctrl.predict(df)
        y2 = self.lof_vibr.predict(df)
        return y1 | y2
    
    def _filter(self, df:pd.DataFrame):
        return self.lof_vibr._filter(df) # 两个模型的filter及scaler的_filter一致
    
    def score_samples(self, df:pd.DataFrame):
        y1 = self.lof_ctrl.score_samples(df)
        y2 = self.lof_vibr.score_samples(df)
        return y1 + 1.5*y2
    
    def save_model(self, outpath=None):
        pathname = f'{outpath}/{self.uuid}.pkl'
        Path(pathname).unlink(missing_ok=True)
        with open(pathname, 'wb') as fd:
            pickle.dump(self, fd)
        return pathname

#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()