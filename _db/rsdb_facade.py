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
from wtbonline._common.utils import make_sure_list, make_sure_datetime
from wtbonline._db.rsdb import model

#%% class
class RSDBFacade():
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
    def read_turbine_fault_type(
            cls, 
            *, 
            columns:Optional[Union[List[str], str]]=None,
            cause:Optional[str]=None,
            name:Optional[str]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFacade.read_turbine_fault_type().columns.tolist()
        ['id', 'set_id', 'name', 'cause', 'type', 'index', 'value', 'var_names', 'time_span', 'graph']
        '''
        tbname = model.TurbineFaultType.__tablename__
        eq_clause, in_clause = cls.get_in_or_eq_clause(cause=cause, name=name)
        df = RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit, columns=columns) 
        df['index'] = df['index'].str.lower()
        df['var_names'] = df['var_names'].str.lower()
        return df

    @classmethod
    def read_statistics_fault(
            cls, 
            *, 
            id_:Optional[Union[list, int, str]]=None,
            set_id:Optional[Union[str, List[str]]]=None,
            device_id:Optional[Union[str, List[str]]]=None,
            fault_id:Optional[Union[int, List[int]]]=None,
            value:Optional[Union[int, List[int]]]=None,
            fault_type:Optional[Union[int, List[int]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            start_time:Union[str, pd.Timestamp, datetime.date] = None,
            end_time:Union[str, pd.Timestamp, datetime.date] = None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFacade.read_statistics_fault(
        ... set_id='20835',
        ... device_id='s10003',
        ... fault_id='a12',
        ... start_time='2023-01-01',
        ... end_time='2023-01-02').columns.tolist()
        ['id', 'set_id', 'device_id', 'fault_id', 'value', 'fault_type', 'start_time', 'end_time', 'create_time']
        '''
        tbname = model.StatisticsFault.__tablename__
        
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'start_time':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'start_time':end_time}
        
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, fault_id=fault_id, value=value, fault_type=fault_type)
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
        >>> RSDBFacade.read_timed_task(
        ... task_id='20835',
        ... status='s10003',
        ... func='a12').columns.tolist()
        ['id', 'task_id', 'status', 'func', 'type', 'start_time', 'function_parameter', 'task_parameter', 'username', 'update_time']
        '''
        tbname = model.TimedTask.__tablename__
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
        >>> RSDBFacade.read_timed_task_log(
        ... task_id='abcd',
        ... result='a12').columns.tolist()
        ['id', 'task_id', 'result', 'start_time', 'end_time', 'pid']
        '''
        tbname = model.TimedTaskLog.__tablename__
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
        >>> RSDBFacade.read_turbine_variable_bound(
        ... set_id='abcd',
        ... var_name='a12').columns.tolist()
        ['id', 'set_id', 'var_name', 'name', 'lower_bound', 'upper_bound']
        '''
        tbname = model.TurbineVariableBound.__tablename__
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
        >>> RSDBFacade.read_app_server(
        ... name='tdengine',
        ... remote=1,
        ... type='restapi').columns.tolist()
        ['id', 'name', 'host', 'version', 'remote', 'type', 'port', 'user', 'password', 'database']
        '''
        tbname = model.AppServer.__tablename__
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
        >>> RSDBFacade.read_app_configuration(key_='abc').columns.tolist()
        ['id', 'key', 'value', 'comment']
        '''
        tbname = model.AppConfiguration.__tablename__
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
        >>> RSDBFacade.read_model(
        ... id_='abc',
        ... set_id='abc',
        ... device_id='abc',
        ... uuid='abc',
        ... name='abc',
        ... create_time='2023-01-01',
        ... ).columns.tolist()
        ['id', 'farm_name', 'set_id', 'device_id', 'uuid', 'name', 'start_time', 'end_time', 'is_local', 'create_time']
        '''
        tbname = model.Model.__tablename__
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
        >>> RSDBFacade.read_windfarm_configuration(
        ... set_id='abc',
        ... ).columns.tolist()
        ['id', 'set_id', 'gearbox_ratio']
        '''
        tbname = model.WindfarmConfiguration.__tablename__
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
        >>> RSDBFacade.read_turbine_model_point(
        ... stat_sample=1,
        ... stat_operation=1,
        ... stat_accumulation=1,
        ... point_name='abc',
        ... var_name='abc',
        ... ).columns.tolist()
        ['id', 'stat_operation', 'stat_sample', 'stat_accumulation', 'point_name', 'var_name']
        '''
        tbname = model.TurbineModelPoint.__tablename__
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            stat_sample=stat_sample, stat_operation=stat_operation,
            point_name=point_name, var_name=var_name, stat_accumulation=stat_accumulation
            )
        rev = RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)
        if 'var_name' in rev.columns:
            rev['var_name'] = rev['var_name'].str.lower()
        return rev

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
        groupby:List[str]=None,
        drop_duplicate:bool=True
        )->pd.DataFrame:
        '''
        >>> RSDBFacade.read_statistics_sample(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... start_time='2023-02-01',
        ... end_time='2023-02-02',
        ... columns={'var_101_mean':['max', 'sum']},
        ... groupby='set_id',
        ... ).columns.tolist()
        ['var_101_mean_max', 'var_101_mean_sum']
        '''
        tbname = model.StatisticsSample.__tablename__
        eq_clause, in_clause = cls.get_in_or_eq_clause(id=id_, set_id=set_id, device_id=device_id)
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'bin':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'bin':end_time}
        df = RSDB.query(tbname, columns=columns, lge_clause=lge_clause, eq_clause=eq_clause,
                        lt_clause=lt_clause, in_clause=in_clause, limit=limit, unique=unique,
                        groupby=groupby, random=random)
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
        >>> RSDBFacade.read_model_anormaly(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... model_uuid='abc',
        ... start_time='2023-02-01',
        ... end_time='2023-02-02',
        ... ).columns.tolist()
        ['id', 'set_id', 'device_id', 'sample_id', 'bin', 'model_uuid', 'create_time']
        '''
        tbname = model.ModelAnomaly.__tablename__
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
        >>> RSDBFacade.read_model_label(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... username='abc',
        ... sample_id='12',
        ... is_anomaly=1,
        ... ).columns.tolist()
        ['id', 'username', 'set_id', 'device_id', 'sample_id', 'is_anomaly', 'create_time']
        '''
        tbname = model.ModelLabel.__tablename__
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
        ):
        '''
        >>> RSDBFacade.read_user(
        ... username='abc',
        ... privilege=1,
        ... ).columns.tolist()
        ['id', 'username', 'password', 'privilege']
        '''
        tbname = model.User.__tablename__
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            privilege=privilege, username=username
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)  

if __name__ == "__main__":
    '''
    测试前需要提前对online库做以下处理:
    statistics_daily生成1万条样本数据（可通过navicat实现）
    id，系统自增
    set_id， 正则表达式 2083[0-9]
    device_id, 正则表达式  s_100[0-5][1-9]
    '''
    import doctest
    doctest.testmod()