# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:21:08 2023

@author: luosz

数据库操作函数
"""
#%% definiton
# import
from datetime import date
import pandas as pd
from typing import List, Optional, Union, Mapping, Any

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.common import (make_sure_list, make_sure_datetime)

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
    def read_timed_task(
            cls, 
            *, 
            status:Optional[Union[str, List[str]]]=['start', 'pause'],
            success:Optional[Union[str, List[str]]]=None,
            func:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_timed_task_log()
        '''
        tbname = 'timed_task'
        eq_clause, in_clause = cls.get_in_or_eq_clause(success=success, func=func, status=status)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_timed_task_log(
            cls, 
            *, 
            success:Optional[Union[str, List[str]]]=None,
            func:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_timed_task_log()
        '''
        tbname = 'timed_task_log'
        eq_clause, in_clause = cls.get_in_or_eq_clause(success=success, func=func)
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
        >>> _ = RSDBInterface.read_turbine_variable_bound()
        '''
        tbname = 'turbine_variable_bound'
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id, var_name=var_name)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 

    @classmethod
    def read_windfarm_power_curve(
            cls, 
            *, 
            model_name:Optional[Union[str, List[str]]]=None,
            limit=None,
            )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_windfarm_power_curve()
        '''
        tbname = 'windfarm_power_curve'
        eq_clause, in_clause = cls.get_in_or_eq_clause(model_name=model_name)
        df = RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit) 
        return df.sort_values('mean_speed')

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
        >>> _ = RSDBInterface.read_app_server()
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
        >>> _ = RSDBInterface.read_app_configuration()
        '''
        tbname = 'app_configuration'
        eq_clause, in_clause = cls.get_in_or_eq_clause(key=key_)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, limit=limit)  

    @classmethod
    def read_windfarm_infomation(
            cls, 
            *, 
            limit:Optional[int]=1,
            )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_windfarm_infomation()
        '''
        tbname = 'windfarm_infomation'
        return RSDB.query(tbname, limit=limit)  

    @classmethod
    def read_model(
            cls, 
            *, 
            id_:(list or int or str)=None,
            set_id:Optional[List[str or int]]=None,
            turbine_id:(list or int or str)=None,
            uuid:(list or int or str)=None,
            name:(list or int or str)=None,
            create_time:Optional[Union[str, List[str]]]=None,
            columns:Optional[Union[List[str], str]]=None,
            limit:Optional[int]=None,
            func_dct:Mapping[str, List[str]]=None,
            groupby:Optional[Union[str, List[str]]]=None,
            orderby:Optional[Union[str, List[str]]]=None,
            )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_model()
        '''
        tbname = 'model'
        columns = make_sure_list(columns)
        create_time = make_sure_list(pd.to_datetime(create_time))
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, turbine_id=turbine_id, 
            uuid=uuid, name=name, create_time=create_time)
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, 
                          in_clause=in_clause, limit=limit, func_dct=func_dct, 
                          groupby=groupby, orderby=orderby)  

    @classmethod
    def read_windfarm_configuration(
            cls, 
            *, 
            set_id:Optional[List[str or int]]=None,
            turbine_id:Optional[List[str or int]]=None,
            map_id:Optional[List[str or int]]=None,
            columns:Optional[Union[List[str], str]]=None,
            )->pd.DataFrame:
        '''
        >>> len(RSDBInterface.read_windfarm_configuration())>0
        True
        '''
        tbname = 'windfarm_configuration'
        eq_clause, in_clause = cls.get_in_or_eq_clause(set_id=set_id, turbine_id=turbine_id, map_id=map_id)
        return RSDB.query(tbname, eq_clause=eq_clause, in_clause=in_clause, columns=columns)

    @classmethod    
    def read_turbine_model_point(
        cls, 
        *, 
        set_id:Optional[List[str or int]]=None, 
        stat_sample:Optional[int]=None,
        stat_operation:Optional[int]=None,
        select:Optional[int]=1,
        columns:Optional[Union[List[str], str]]=None,
        )->pd.DataFrame:
        '''
        >>> _ = RSDBInterface.read_turbine_model_point()
        '''
        tbname = 'turbine_model_points'
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            set_id=set_id, stat_sample=stat_sample, stat_operation=stat_operation,
            select=select
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause)

    @classmethod   
    def read_statistics_sample(
        cls,
        *,
        id_:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        start_time:Union[str, pd.Timestamp, date] = None,
        end_time:Union[str, pd.Timestamp, date] = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        unique:bool=False,
        random:bool=False,
        func_dct:Mapping[str, List[str]]=None,
        groupby:List[str]=None,
        drop_duplicate:bool=True
        )->pd.DataFrame:
        '''
        >>> pd.Series(['set_id', 'turbine_id', 'bin']).isin(RSDBInterface.read_statistics_sample().columns).all()
        True
        '''
        tbname = 'statistics_sample'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(id=id_, set_id=set_id, turbine_id=turbine_id)
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
        id_:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        model_uuid:List[str]=None,
        start_time:Union[str, pd.Timestamp, date] = None,
        end_time:Union[str, pd.Timestamp, date] = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> isinstance(RSDBInterface.read_model_anormaly(), (pd.DataFrame, pd.Series))
        True
        '''
        tbname = 'model_anormaly'
        start_time = make_sure_datetime(start_time)
        lge_clause = {} if start_time is None else {'bin':start_time}
        end_time = make_sure_datetime(end_time)  
        lt_clause = {} if end_time is None else {'bin':end_time}
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, turbine_id=turbine_id, model_uuid=model_uuid
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit, lge_clause=lge_clause, lt_clause=lt_clause)
    
    @classmethod  
    def read_model_label(
        cls,
        *,
        id_:(list or int or str)=None,
        username:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        sample_id:(list or int or str)=None,
        is_anormaly:int=None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> _ = RSDBInterface.read_model_label()
        >>> _ = RSDBInterface.read_model_label(id_=1, set_id='10050')
        '''
        tbname = 'model_label'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            id=id_, set_id=set_id, username=username, turbine_id=turbine_id, 
            sample_id=sample_id, is_anormaly=is_anormaly
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, in_clause=in_clause, 
                          limit=limit)

    @classmethod  
    def read_user(
        cls,
        *,
        username:(list or int or str)=None,
        privilege:list = None,
        columns:Optional[Union[List[str], str]]=None,
        limit:int=None,
        ):
        '''
        >>> len(RSDBInterface.read_user(username='admin'))==1
        True
        '''
        tbname = 'user'
        columns = make_sure_list(columns)
        eq_clause, in_clause = cls.get_in_or_eq_clause(
            privilege=privilege, username=username
            )
        return RSDB.query(tbname, columns=columns, eq_clause=eq_clause, 
                          in_clause=in_clause, limit=limit)  
    

#%% main        
if __name__ == "__main__":
    import doctest
    doctest.testmod()