# -*- coding: utf-8 -*-

#%% import 
import pandas as pd
from typing import Union, List, Optional
from pathlib import Path
import pickle
 
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._common.utils import make_sure_datetime, make_sure_list
from wtbonline._logging import log_it
from wtbonline._process.model import _LOGGER, model_factory
from wtbonline._db.postgres_facade import PGFacade

#%% constant
PATH = Path(RSDBFacade.read_app_configuration(key_='model_path')['value'].iloc[0])
PATH.mkdir(exist_ok=True)

#%% function
def record(set_id, device_id, uuid, type_, start_time, end_time):
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

@log_it(_LOGGER,True)
def train_all(end_time, delta:int, type_:str='anomaly', **kwargs):
    end_time = make_sure_datetime(end_time)
    start_time = end_time - pd.Timedelta(f"{delta}d") 
    device_df = PGFacade.read_model_device()[['set_id', 'device_id']]
    clf = model_factory(type_)
    err_msg = []
    for _, row in device_df.iterrows():
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
            record(row['set_id'], row['device_id'], clf.uuid, type_, start_time, end_time)
            _LOGGER.info(f"train {type_} {row['set_id']} {row['device_id']}")
        except Exception as e:
            err_msg.append(f"train {type_} {row['set_id']} {row['device_id']} {e}")
    if len(err_msg):
        raise ValueError('\n'.join(err_msg))

def load_latest_model(set_id, device_id, type_):
    '''
    >>> load_latest_model('20625', 'd10001', type_='anomaly')
    '''
    uuid = RSDBFacade.read_model(set_id=set_id, device_id=device_id)['uuid'].iloc[-1]
    with open(PATH/f'{uuid}.pkl', 'rb') as fd:
        estimator = pickle.load(fd)
    if uuid!=str(estimator.uuid):
        raise ValueError(f'文件uuid不匹配, 给定{uuid}，实际{estimator.uuid}')
    return estimator

# def predict(
#         uuids, 
#         set_id, 
#         turbine_id, 
#         start_time, 
#         end_time, 
#         size, 
#         model_uuid=None,
#         ):
#     uuids = make_sure_list(uuids)
#     data_df = RSDBFacade.read_statistics_sample(
#         set_id=set_id,
#         turbine_id=turbine_id,
#         start_time=start_time,
#         end_time=end_time
#         )
#     anomaly_df=[]
#     for uuid in uuids:
#         clf, trainer = load_model(uuid, return_trainer=True)
#         trainer.train(data_df, only_value=True, test_size=0)
#         X = trainer.X_train
#         scores = pd.Series(clf.score_samples(X), index=X.index)
#         idxes = scores.sort_values().head(size).index
#         anomaly_df.append(data_df.loc[idxes,['set_id', 'turbine_id', 'id', 'bin']])
#     anomaly_df = pd.concat(anomaly_df, ignore_index=True)
#     anomaly_df.rename(columns={'id':'sample_id'}, inplace=True)
#     anomaly_df.drop_duplicates(['sample_id'], inplace=True)
#     anomaly_df.sort_values('sample_id', inplace=True)
#     anomaly_df['model_uuid'] = ','.join(uuids) if model_uuid is None else model_uuid 
#     anomaly_df['create_time'] = pd.Timestamp.now()
#     RSDBFacade.insert(anomaly_df, 'model_anormaly')

# @log_it(_LOGGER, True)
# def predict_all(*args, **kwargs):
#     '''
#     >>> predict_all(end_time='2023-11-01', delta=60)
#     '''
#     if kwargs['end_time'] is not None and kwargs['end_time']!='':
#         end_time = pd.to_datetime(kwargs['end_time']) 
#     else:
#         end_time = pd.Timestamp.now().date()
#     start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    
#     model_df = RSDBFacade.read_model(
#         name=['lof_ctrl', 'lof_vibr'],
#         func_dct={'create_time':['max']},
#         groupby=['set_id', 'turbine_id', 'name'],
#         ).rename(columns={'create_time_max':'create_time'})
#     model_df = RSDBFacade.read_model(
#         **{i:model_df[i].unique().tolist() for i in model_df}
#         )
#     for (sid,tid),grp in model_df.groupby(['set_id', 'turbine_id']):
#         _LOGGER.info(f'异常值识别 {sid} {tid}')
#         try:
#             predict(
#                 uuids=grp['uuid'], 
#                 set_id=sid, 
#                 turbine_id=tid, 
#                 start_time=start_time, 
#                 end_time=end_time,
#                 size=kwargs.get('size', 20)
#                 )
#         except Exception as e:
#             _LOGGER.error(f'{sid} {tid} 异常点识别失败: {e}')

#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    # train_all(end_time='2024-03-01', delta=120, minimum=200)