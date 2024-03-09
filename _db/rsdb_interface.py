# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:21:08 2023

@author: luosz

数据库操作函数
"""
#%% definiton
# import
import datetime
import pandas as pd
from typing import List, Optional, Union, Mapping, Any

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.common import (make_sure_list, make_sure_datetime)
from wtbonline._db.rsdb import model
from wtbonline._db.config import POSTGRES_URI

#%% class
class RSDBInterface():
    @classmethod
    def insert(cls, df:Union[dict, pd.DataFrame], tbname:str):
        RSDB.insert(df, tbname)

    @classmethod
    def update(cls,               
               tbname:str,
               new_values:Mapping[str, Any],
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, str]]=None, 
               lge_clause:Optional[Mapping[str, str]]=None, 
               lt_clause:Optional[Mapping[str, str]]=None):
        RSDB.update(tbname, new_values, eq_clause=eq_clause, in_clause=in_clause, lge_clause=lge_clause, lt_clause=lt_clause)

    @classmethod
    def get_in_or_eq_clause(cls, **kwargs):
        eq_clause = {}
        in_clause = {}
        for key_ in kwargs:
            values = make_sure_list(kwargs[key_])
            n = len(values)
            if n==0:
                continue
            elif n==1:
                eq_clause.update({key_:values})
            else:
                in_clause.update({key_:values})
        return eq_clause, in_clause


    @classmethod
    def read_apscheduler_jobs(cls,)->pd.DataFrame:
        tbname = model.ApschedulerJob.__tablename__
        return RSDB.query(tbname) 

    @classmethod
    def read_statistics_daily(
            cls, 
            *, 
            set_id:Optional[Union[str, List[str]]]=None,
            device_id:Optional[Union[str, List[str]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> df = RSDBInterface.read_statistics_daily(set_id='20835', device_id='s10003')
        >>> df.shape[0]>1
        True
        >>> df.shape[1]==8
        True
        >>> RSDBInterface.read_statistics_daily(columns=df.columns[:3]).shape[1]==3
        True
        '''
        tbname = model.StatisticsDaily.__tablename__
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id, device_id=device_id)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit, columns=columns) 

    @classmethod
    def read_turbine_fault_type(
            cls, 
            *, 
            columns:Optional[Union[List[str], str]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> df = RSDBInterface.read_turbine_fault_type()
        >>> df.shape[0]>1
        True
        >>> df.shape[1]==2
        True
        >>> RSDBInterface.read_turbine_fault_type(columns=df.columns[:1]).shape[1]==1
        True
        '''
        tbname = model.TurbineFaultType.__tablename__
        return RSDB.query(tbname, limit=limit, columns=columns) 

    @classmethod
    def read_statistics_fault(
            cls, 
            *, 
            set_id:Optional[Union[str, List[str]]]=None,
            device_id:Optional[Union[str, List[str]]]=None,
            fault_id:Optional[Union[int, List[int]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            date:datetime.date=None,
            start_time:Union[str, pd.Timestamp, datetime.date] = None,
            end_time:Union[str, pd.Timestamp, datetime.date] = None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_statistics_fault(
        ... set_id='20835',
        ... device_id='s10003',
        ... fault_id='a12',
        ... date='2023-01-01',
        ... start_time='2023-01-01',
        ... end_time='2023-01-02').columns.tolist()
        ['id', 'set_id', 'device_id', 'date', 'fault_id', 'timestamp', 'create_time']
        '''
        tbname = model.StatisticsFault.__tablename__
        
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'timestamp':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'timestamp':end_time}
        date = make_sure_datetime(date)
        
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id, device_id=device_id, fault_id=fault_id, date=date)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit, 
                          lge_clause=lge_clause, lt_clause=lt_clause ,columns=columns) 

    @classmethod
    def read_timed_task(
            cls, 
            *, 
            task_id:Optional[str]=None,
            status:Optional[Union[str, List[str]]]=None,
            func:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_timed_task(
        ... task_id='20835',
        ... status='s10003',
        ... func='a12').columns.tolist()
        ['id', 'task_id', 'status', 'func', 'type', 'start_time', 'function_parameter', 'task_parameter', 'username', 'update_time']
        '''
        tbname = 'timed_task'
        eq_clause, in_clause = cls.get_in_or_eq_clause(status=status, func=func, task_id=task_id)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_timed_task_log(
            cls, 
            *, 
            task_id:Optional[Union[str, List[str]]]=None,
            result:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_timed_task_log(
        ... task_id='abcd',
        ... result='a12').columns.tolist()
        ['id', 'task_id', 'result', 'start_time', 'end_time', 'pid']
        '''
        tbname = 'timed_task_log'
        eq_clause, in_clause = cls.get_in_or_eq_clause(task_id=task_id, result=result)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_turbine_variable_bound(
            cls, 
            *, 
            set_id:Optional[Union[str, List[str]]]=None,
            var_name:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_turbine_variable_bound(
        ... set_id='abcd',
        ... var_name='a12').columns.tolist()
        ['id', 'set_id', 'var_name', 'name', 'lower_bound', 'upper_bound']
        '''
        tbname = 'turbine_variable_bound'
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id, var_name=var_name)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_app_server(
            cls, 
            *, 
            name:Optional[str]=None,
            remote:Optional[int]=None,
            type:Optional[str]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_app_server(
        ... name='tdengine',
        ... remote=1,
        ... type='restapi').columns.tolist()
        ['id', 'name', 'host', 'remote', 'type', 'port', 'user', 'password', 'database']
        '''
        tbname = 'app_server'
        eq_clause, in_clause = cls.get_in_or_eq_clause(name=name, remote=remote, type=type)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_app_configuration(
            cls, 
            *, 
            key_:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_app_configuration(key_='abc').columns.tolist()
        ['id', 'key', 'value', 'comment']
        '''
        tbname = 'app_configuration'
        eq_clause, in_clause = cls.get_in_or_eq_clause(key=key_)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit)  


    @classmethod
    def read_model(
            cls, 
            *, 
            id_:Optional[Union[list, int, str]]=None,
            set_id:Optional[Union[list, int, str]]=None,
            device_id:Optional[Union[list, int, str]]=None,
            uuid:Optional[Union[list, int, str]]=None,
            name:Optional[Union[list, int, str]]=None,
            create_time:Optional[Union[str, List[str]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            limit:Optional[int]=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_model(
        ... id_='abc',
        ... set_id='abc',
        ... device_id='abc',
        ... uuid='abc',
        ... name='abc',
        ... create_time='2023-01-01',
        ... ).columns.tolist()
        ['id', 'farm_name', 'set_id', 'device_id', 'uuid', 'name', 'start_time', 'end_time', 'is_local', 'create_time']
        '''
        tbname = 'model'
        columns = make_sure_list(columns)
        create_time = make_sure_list(pd.to_datetime(create_time))
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, 
            uuid=uuid, name=name, create_time=create_time)
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, limit=limit)  

    @classmethod
    def read_windfarm_configuration(
            cls, 
            *, 
            set_id:Optional[Union[list, int, str]]=None,
            )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_windfarm_configuration(
        ... set_id='abc',
        ... ).columns.tolist()
        ['id', 'set_id', 'gearbox_ratio']
        '''
        tbname = 'windfarm_configuration'
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause)


    @classmethod    
    def read_turbine_model_point(
        cls, 
        *, 
        stat_sample:Optional[int]=None,
        stat_operation:Optional[int]=None,
        stat_accumulation:Optional[int]=None,
        point_name:Optional[Union[List[str], str]]=None,
        var_name:Optional[Union[List[str], str]]=None,    
        columns:Optional[Union[List[str], str]]=None,
        )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_turbine_model_point(
        ... stat_sample=1,
        ... stat_operation=1,
        ... stat_accumulation=1,
        ... point_name='abc',
        ... var_name='abc',
        ... ).columns.tolist()
        ['id', 'stat_operation', 'stat_sample', 'stat_accumulation', 'point_name', 'var_name', 'ref_name']
        '''
        tbname = 'turbine_model_points'
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            stat_sample=stat_sample, stat_operation=stat_operation,
            point_name=point_name, var_name=var_name, stat_accumulation=stat_accumulation
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)

    @classmethod   
    def read_statistics_sample(
        cls,
        *,
        id_:Optional[Union[list, int]]=None,
        set_id:Optional[Union[list, int, str]]=None,
        device_id:Optional[Union[list, int, str]]=None,
        start_time:Union[str, pd.Timestamp, datetime.date] = None,
        end_time:Union[str, pd.Timestamp, datetime.date] = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        unique:bool=False,
        random:bool=False,
        func_dct:Mapping[str, List[str]]=None,
        groupby:List[str]=None,
        drop_duplicate:bool=True
        )->pd.DataFrame:
        '''
        >>> RSDBInterface.read_statistics_sample(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... start_time='2023-02-01',
        ... end_time='2023-02-02',
        ... func_dct={'var_101_mean':['AVG', 'sum']},
        ... groupby='set_id',
        ... ).shape[1]>1
        True
        '''
        tbname = 'statistics_sample'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(id=id_, set_id=set_id, device_id=device_id)
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'bin':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'bin':end_time}
        df = RSDB.query(tbname, columns=columns, lge_clause=lge_clause, eq_clause=eq_clause,
                        lt_clause=lt_clause, in_clause=in_clause, limit=limit, unique=unique,
                        func_dct=func_dct, groupby=groupby, random=random)
        if drop_duplicate==True and 'creat_time' in df.columns:
            df.sort_values('create_time').drop_duplicates(keep='last', inplace=True)
        return df

    @classmethod  
    def read_model_anormaly(
        cls,
        *,
        id_:Optional[Union[list, int, str]]=None,
        set_id:Optional[Union[list, int, str]]=None,
        device_id:Optional[Union[list, int, str]]=None,
        model_uuid:List[str]=None,
        start_time:Union[str, pd.Timestamp, datetime.date] = None,
        end_time:Union[str, pd.Timestamp, datetime.date] = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> RSDBInterface.read_model_anormaly(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... model_uuid='abc',
        ... start_time='2023-02-01',
        ... end_time='2023-02-02',
        ... ).columns.tolist()
        ['id', 'set_id', 'device_id', 'sample_id', 'bin', 'model_uuid', 'create_time']
        '''
        tbname = 'model_anomaly'
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'bin':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'bin':end_time}
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, model_uuid=model_uuid
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit, lge_clause=lge_clause, lt_clause=lt_clause)
    
    @classmethod  
    def read_model_label(
        cls,
        *,
        id_:Optional[Union[list, int, str]]=None,
        set_id:Optional[Union[list, int, str]]=None,
        device_id:Optional[Union[list, int, str]]=None,
        username:Optional[Union[list, int, str]]=None,
        sample_id:Optional[Union[list, int, str]]=None,
        is_anomaly:int=None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> RSDBInterface.read_model_label(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... username='abc',
        ... sample_id='12',
        ... is_anomaly=1,
        ... ).columns.tolist()
        ['id', 'username', 'set_id', 'device_id', 'sample_id', 'is_anomaly', 'create_time']
        '''
        tbname = 'model_label'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, username=username, device_id=device_id, 
            sample_id=sample_id, is_anomaly=is_anomaly
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit)

    @classmethod  
    def read_user(
        cls,
        *,
        username:Optional[Union[list, int, str]]=None,
        privilege:list = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> RSDBInterface.read_user(
        ... username='abc',
        ... privilege=1,
        ... ).columns.tolist()
        ['id', 'username', 'password', 'privilege']
        '''
        tbname = 'user'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            privilege=privilege, username=username
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, 
                          in_clause=in_clause, limit=limit)  

if __name__ == "__main__":
    import doctest
    doctest.testmod()