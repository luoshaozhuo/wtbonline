# -*- coding: utf-8 -*-

#%% import 
import pandas as pd

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.common import make_sure_list
from wtbonline._logging import log_it
from wtbonline._process.model.anormlay import get_trainers, _LOGGER, OUTPATH

#%% function
def load_model(uuid, return_trainer=False):
    model_sr = RSDBInterface.read_model(uuid=uuid).squeeze()
    assert len(model_sr)>0, f'查无记录 uuid={uuid}'
    trainer = get_trainers()[model_sr['name']][0]
    pathname = OUTPATH/f'{uuid}.pkl'
    clf = trainer.load_model(pathname)
    if return_trainer==True:
        return clf, trainer
    else:
        return clf  

def predict(
        uuids, 
        set_id, 
        turbine_id, 
        start_time, 
        end_time, 
        size, 
        model_uuid=None,
        ):
    uuids = make_sure_list(uuids)
    data_df = RSDBInterface.read_statistics_sample(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time
        )
    anomaly_df=[]
    for uuid in uuids:
        clf, trainer = load_model(uuid, return_trainer=True)
        trainer.train(data_df, only_value=True, test_size=0)
        X = trainer.X_train
        scores = pd.Series(clf.score_samples(X), index=X.index)
        idxes = scores.sort_values().head(size).index
        anomaly_df.append(data_df.loc[idxes,['set_id', 'turbine_id', 'id', 'bin']])
    anomaly_df = pd.concat(anomaly_df, ignore_index=True)
    anomaly_df.rename(columns={'id':'sample_id'}, inplace=True)
    anomaly_df.drop_duplicates(['sample_id'], inplace=True)
    anomaly_df.sort_values('sample_id', inplace=True)
    anomaly_df['model_uuid'] = ','.join(uuids) if model_uuid is None else model_uuid 
    anomaly_df['create_time'] = pd.Timestamp.now()
    RSDBInterface.insert(anomaly_df, 'model_anormaly')

@log_it(_LOGGER, True)
def predict_all(*args, **kwargs):
    '''
    >>> predict_all(end_time='2023-11-01', delta=60)
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
        _LOGGER.info(f'异常值识别 {sid} {tid}')
        try:
            predict(
                uuids=grp['uuid'], 
                set_id=sid, 
                turbine_id=tid, 
                start_time=start_time, 
                end_time=end_time,
                size=kwargs.get('size', 20)
                )
        except Exception as e:
            _LOGGER.error(f'{sid} {tid} 异常点识别失败: {e}')


#%% main
if __name__ == "__main__":
    predict_all(end_time='2023-11-01', delta=60)
