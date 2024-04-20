# -*- coding: utf-8 -*-

#%% import 
import pandas as pd
from typing import Union, List, Optional
from pathlib import Path
import pickle
 
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._common.utils import make_sure_datetime, make_sure_list
from wtbonline._process.model import _LOGGER, model_factory
from wtbonline._db.postgres_facade import PGFacade

#%% constant
PATH = Path(RSDBFacade.read_app_configuration(key_='model_path')['value'].iloc[0])
PATH.mkdir(exist_ok=True)

#%% function
def record_train(set_id, device_id, uuid, type_, start_time, end_time):
    create_time = pd.Timestamp.now()
    dct = dict(
        set_id=set_id,
        device_id=device_id,
        uuid=uuid,
        type=type_,
        start_time=start_time,
        end_time=end_time,
        create_time=create_time,
        )
    RSDB.insert(dct, 'model')

def train_all(end_time, delta:int, type_:str='anomaly', **kwargs):
    minimum=kwargs.get('minimum', 5000)
    test_size=kwargs.get('test_size', 0)
    end_time = make_sure_datetime(end_time)
    start_time = end_time - pd.Timedelta(f"{delta}d") 
    device_df = PGFacade.read_model_device()[['set_id', 'device_id']]
    err_msg = []
    for _, row in device_df.iterrows():
        clf = model_factory(type_, minimum=minimum, test_size=test_size)  
        df = RSDBFacade.read_statistics_sample(
            set_id=row['set_id'], 
            device_id=row['device_id'], 
            start_time=start_time, 
            end_time=end_time,
            columns=clf.columns,
            )
        if len(df)<1:
            continue
        try:     
            clf.fit(df)
            clf.save_model(PATH)
            record_train(row['set_id'], row['device_id'], clf.uuid, type_, start_time, end_time)
            _LOGGER.info(f"train {type_} {row['set_id']} {row['device_id']}")
        except Exception as e:
            err_msg.append(f"train {type_} {row['set_id']} {row['device_id']} {e}")
    if len(err_msg):
        raise ValueError('\n'.join(err_msg))

def load_latest_model(set_id, device_id, type_='anomaly'):
    '''
    >>> load_latest_model('20625', 'd10001', type_='anomaly')
    '''
    df = RSDBFacade.read_model(set_id=set_id, device_id=device_id, type_=type_)
    if len(df)>0:
        uuid = df['uuid'].iloc[-1]
    else:
        return None
    with open(PATH/f'{uuid}.pkl', 'rb') as fd:
        estimator = pickle.load(fd)
    if uuid!=str(estimator.uuid):
        raise ValueError(f'文件uuid不匹配, 给定{uuid}，实际{estimator.uuid}')
    return estimator

def record_predict(df, set_id, device_id, uuid):
    columns = ['set_id', 'device_id', 'sample_id', 'bin', 'model_uuid', 'create_time']
    df = df.rename(columns={'id':'sample_id'})
    df['model_uuid'] = uuid
    df['create_time'] = pd.Timestamp.now()
    df['set_id'] = set_id
    df['device_id'] = device_id
    RSDB.insert(df[columns], 'model_anomaly')
    
def predict_all(end_time, delta:int, type_:str='anomaly', **kwargs):
    nsample = kwargs.get('nsample', 30)
    end_time = make_sure_datetime(end_time)
    start_time = end_time - pd.Timedelta(f"{delta}d") 
    device_df = PGFacade.read_model_device()[['set_id', 'device_id']]
    clf = model_factory(type_)
    columns = clf.columns + ['bin', 'id']
    err_msg = []
    for _, row in device_df.iterrows():
        _LOGGER.info(f"predict {row['set_id']} {row['device_id']}")
        df = RSDBFacade.read_statistics_sample(
            set_id=row['set_id'], 
            device_id=row['device_id'], 
            start_time=start_time, 
            end_time=end_time,
            columns=columns,
            )
        clf = load_latest_model(row['set_id'], row['device_id'], type_)
        if clf is None:
            continue
        df = clf._filter(df)
        # 选出异常点，再按scores选出规定个数的样本
        sub_df = df[clf.predict(df)==-1].reset_index(drop=True)
        sub_df['score'] = clf.score_samples(sub_df)
        sub_df = sub_df.sort_values('score', ascending=True).head(nsample)
        try:
            record_predict(sub_df, row['set_id'], row['device_id'], clf.uuid)
        except Exception as e:
            err_msg.append(f"predict {type_} {row['set_id']} {row['device_id']} {e}")
    if len(err_msg):
        raise ValueError('\n'.join(err_msg))

#%% main
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    train_all(end_time='2024-01-01', delta=300, minimum=200)
    predict_all(end_time='2024-04-01', delta=120, nsample=30)