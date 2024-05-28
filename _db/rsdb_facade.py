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

from wtbonline._db.rsdb.dao import RSDBDAO
from wtbonline._common.utils import make_sure_list, make_sure_datetime
from wtbonline._db.rsdb import model
from wtbonline._db.postgres_facade import PGFacade

#%% class
class RSDBFacade():
    def __init__(self):
        self.RSDB = RSDBDAO()
    
    def insert(self, df:Union[dict, pd.DataFrame], tbname:str):
        self.RSDB.insert(df, tbname)

    
    def update(self,               
               tbname:str,
               new_values:Mapping[str, Any],
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, str]]=None, 
               lge_clause:Optional[Mapping[str, str]]=None, 
               lt_clause:Optional[Mapping[str, str]]=None):
        self.RSDB.update(tbname, new_values, eq_clause=eq_clause, in_clause=in_clause, lge_clause=lge_clause, lt_clause=lt_clause)

    
    def get_in_or_eq_clause(self, **kwargs):
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


    
    def read_apscheduler_jobs(self,)->pd.DataFrame:
        tbname = model.ApschedulerJob.__tablename__
        return self.RSDB.query(tbname) 

    
    def read_turbine_fault_type(
            self, 
            *, 
            is_offshore:Optional[int]=None,
            columns:Optional[Union[List[str], str]]=None,
            cause:Optional[str]=None,
            name:Optional[str]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_turbine_fault_type().columns.tolist()
        ['id', 'is_offshore', 'name', 'cause', 'value', 'type', 'var_names', 'index', 'time_span', 'graph']
        '''
        if is_offshore is None:
            set_id = PGFacade().read_model_device()['set_id'].iloc[0]
            is_offshore = self.read_windfarm_configuration(set_id=set_id)['is_offshore'].iloc[0]            
        tbname = model.TurbineFaultType.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(cause=cause, name=name, is_offshore=is_offshore)
        df = self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit, columns=columns) 
        df['index'] = df['index'].str.lower()
        df['var_names'] = df['var_names'].str.lower()
        return df

    
    def read_statistics_fault(
            self, 
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
        >>> RSDBFC.read_statistics_fault(
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
        
        eq_clause, in_clause = self.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, fault_id=fault_id, value=value, fault_type=fault_type)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit, 
                          lge_clause=lge_clause, lt_clause=lt_clause ,columns=columns) 

    
    def read_timed_task(
            self, 
            *, 
            task_id:Optional[str]=None,
            status:Optional[Union[str, List[str]]]=None,
            func:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_timed_task(
        ... task_id='20835',
        ... status='s10003',
        ... func='a12').columns.tolist()
        ['id', 'task_id', 'status', 'func', 'type', 'start_time', 'function_parameter', 'task_parameter', 'username', 'update_time']
        '''
        tbname = model.TimedTask.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(status=status, func=func, task_id=task_id)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    
    def read_timed_task_log(
            self, 
            *, 
            task_id:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_timed_task_log(task_id='abcd').columns.tolist()
        ['id', 'task_id', 'status', 'update_time']
        '''
        tbname = model.TimedTaskLog.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(task_id=task_id)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    
    def read_turbine_variable_bound(
            self, 
            *, 
            set_id:Optional[Union[str, List[str]]]=None,
            var_name:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_turbine_variable_bound(
        ... set_id='abcd',
        ... var_name='a12').columns.tolist()
        ['id', 'set_id', 'var_name', 'name', 'lower_bound', 'upper_bound']
        '''
        tbname = model.TurbineVariableBound.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(set_id=set_id, var_name=var_name)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    
    def read_app_server(
            self, 
            *, 
            name:Optional[str]=None,
            remote:Optional[int]=None,
            type:Optional[str]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_app_server(
        ... name='tdengine',
        ... remote=1,
        ... type='restapi').columns.tolist()
        ['id', 'name', 'host', 'version', 'remote', 'type', 'port', 'user', 'password', 'database']
        '''
        tbname = model.AppServer.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(name=name, remote=remote, type=type)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    
    def read_app_configuration(
            self, 
            *, 
            key_:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_app_configuration(key_='abc').columns.tolist()
        ['id', 'key', 'value', 'comment']
        '''
        tbname = model.AppConfiguration.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(key=key_)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit)  


    
    def read_model(
            self, 
            *, 
            id_:Optional[Union[list, int, str]]=None,
            set_id:Optional[Union[list, int, str]]=None,
            device_id:Optional[Union[list, int, str]]=None,
            uuid:Optional[Union[list, int, str]]=None,
            type_:Optional[Union[list, int, str]]=None,
            create_time:Optional[Union[str, List[str]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            limit:Optional[int]=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_model(
        ... id_='abc',
        ... set_id='abc',
        ... device_id='abc',
        ... uuid='abc',
        ... create_time='2023-01-01',
        ... ).columns.tolist()
        ['id', 'set_id', 'device_id', 'type', 'uuid', 'start_time', 'end_time', 'create_time']
        '''
        tbname = model.Model.__tablename__
        create_time = make_sure_list(pd.to_datetime(create_time))
        eq_clause, in_clause = self.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, 
            uuid=uuid, type=type_, create_time=create_time)
        return self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, limit=limit, orderby='create_time')  

    
    def read_windfarm_configuration(
            self, 
            *, 
            set_id:Optional[Union[list, int, str]]=None,
            )->pd.DataFrame:
        '''
        >>> RSDBFC.read_windfarm_configuration(
        ... set_id='abc',
        ... ).columns.tolist()
        ['id', 'set_id', 'gearbox_ratio', 'is_offshore']
        '''
        tbname = model.WindfarmConfiguration.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(set_id=set_id)
        return self.RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause)


        
    def read_turbine_model_point(
        self, 
        *, 
        point_name:Optional[Union[List[str], str]]=None,
        var_name:Optional[Union[List[str], str]]=None,    
        columns:Optional[Union[List[str], str]]=None,
        )->pd.DataFrame:
        '''
        >>> RSDBFC.read_turbine_model_point(
        ... point_name='abc',
        ... var_name='abc',
        ... ).columns.tolist()
        ['id', 'point_name', 'var_name', 'datatype']
        '''
        tbname = model.TurbineModelPoint.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(point_name=point_name, var_name=var_name)
        rev = self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)
        if 'var_name' in rev.columns:
            rev['var_name'] = rev['var_name'].str.lower()
        return rev

       
    def read_statistics_sample(
        self,
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
        >>> RSDBFC.read_statistics_sample(
        ... id_=1,
        ... set_id='acd',
        ... device_id='abc',
        ... start_time='2023-02-01',
        ... end_time='2023-02-02',
        ... columns={'var_101_mean':['max', 'sum']},
        ... groupby='set_id',
        ... ).columns.tolist()
        ['var_101_mean_max', 'var_101_mean_sum', 'set_id']
        '''
        tbname = model.StatisticsSample.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(id=id_, set_id=set_id, device_id=device_id)
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'bin':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'bin':end_time}
        df = self.RSDB.query(tbname, columns=columns, lge_clause=lge_clause, eq_clause=eq_clause,
                        lt_clause=lt_clause, in_clause=in_clause, limit=limit, unique=unique,
                        groupby=groupby, random=random)
        if drop_duplicate==True and 'creat_time' in df.columns:
            df.sort_values('create_time').drop_duplicates(keep='last', inplace=True)
        return df

      
    def read_model_anormaly(
        self,
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
        >>> RSDBFC.read_model_anormaly(
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
        eq_clause, in_clause = self.get_in_or_eq_clause(
            id=id_, set_id=set_id, device_id=device_id, model_uuid=model_uuid
            )
        return self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit, lge_clause=lge_clause, lt_clause=lt_clause)
    
      
    def read_model_label(
        self,
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
        >>> RSDBFC.read_model_label(
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
        eq_clause, in_clause = self.get_in_or_eq_clause(
            id=id_, set_id=set_id, username=username, device_id=device_id, 
            sample_id=sample_id, is_anomaly=is_anomaly
            )
        return self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit)

      
    def read_user(
        self,
        *,
        username:Optional[Union[list, int, str]]=None,
        privilege:list = None,
        columns:Optional[Union[List[str], str]]=None,
        ):
        '''
        >>> RSDBFC.read_user(
        ... username='abc',
        ... privilege=1,
        ... ).columns.tolist()
        ['id', 'username', 'password', 'privilege']
        '''
        tbname = model.User.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(
            privilege=privilege, username=username
            )
        return self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)  

      
    def read_turbine_outlier_monitor(
        self,
        *,
        id_:Union[str, List[str]]=None,
        system_:Union[str, List[str]]=None,
        type_:Union[str, List[str]]=None,
        columns:Optional[Union[List[str], str]]=None,
        ):
        '''
        >>> RSDBFC.read_turbine_outlier_monitor().columns.tolist()
        ['id', 'system', 'type', 'var_names', 'plot_varnames']
        '''
        tbname = model.TurbineOutlierMonitor.__tablename__
        eq_clause, in_clause = self.get_in_or_eq_clause(id=id_, system_=system_,type_=type_)
        return self.RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)  

RSDBFC = RSDBFacade()

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