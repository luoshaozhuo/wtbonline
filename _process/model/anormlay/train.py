# -*- coding: utf-8 -*-

#%% import 
import pandas as pd
from typing import Union, List, Optional
 
from wtbonline._db.rsdb.dao import RSDB
from _db.rsdb_facade import RSDBFacade
from wtbonline._common.utils import make_sure_list
from wtbonline._logging import log_it
from wtbonline._process.model.anormlay import get_trainers, _LOGGER

#%% function
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
    ''' 从statistic_sample中读取数据训练模型 '''
    trainer_dct = get_trainers()
    uuids_ = make_sure_list(uuids_)
    df = RSDBFacade.read_statistics_sample(
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
    >>> train_all(end_time='2023-09-01', delta=120)
    '''
    if kwargs['end_time'] is not None and kwargs['end_time']!='':
        end_time = pd.to_datetime(kwargs['end_time'])
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    
    conf_df = RSDBFacade.read_windfarm_configuration()[['set_id', 'turbine_id']]
    farm_name = RSDBFacade.read_windfarm_infomation()['farm_name'].iloc[0]
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


#%% main
if __name__ == "__main__":
    train_all(end_time='2023-09-01', delta=120)