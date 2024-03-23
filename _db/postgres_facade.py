# -*- coding: utf-8 -*-
"""
Created on Fri March 8 2024

@author: luosz

远程postgres数据库操作函数
"""
#%% definiton
# import
import pandas as pd
from typing import List, Union
from sqlalchemy import create_engine, text

from wtbonline._common.utils import make_sure_datetime, make_sure_list
from wtbonline._db.config import POSTGRES_URI

#%% constant
_ENGINE = create_engine(POSTGRES_URI)

#%% class
class PGFacade():
    @classmethod  
    def read_model_point(cls, set_id:str=None, var_name:List[str]=[], point_name:List[str]=[]):
        '''
        >>> len(PGFacade.read_model_point(set_id='20835'))>0
        True
        >>> len(PGFacade.read_model_point(set_id='20835', var_name='var_101'))==1
        True
        >>> len(PGFacade.read_model_point(set_id='20835', var_name='var_101'))==1
        True
        >>> len(PGFacade.read_model_point(set_id='20835', point_name='有功功率'))==1
        True
        '''
        var_name = make_sure_list(var_name)
        point_name = make_sure_list(point_name)
        cols = ['set_id', 'var_name', 'point_name', 'datatype', 'unit']
        sql = f"select {','.join(cols)} from model_points where local_save=1"
        sql += f" and set_id='{set_id}'" if set_id is not None else ''
        df = pd.read_sql(text(sql), con=_ENGINE)
        df['var_name'] = df['var_name'].str.lower()
        if 'unit' in df.columns:
            df['unit'] = df['unit'].fillna('unknown')
        if len(var_name)>0:
            df = df[df['var_name'].isin(var_name)]
        if len(point_name)>0:
            df = df[df['point_name'].isin(point_name)]
        df['name'] = df['point_name'] + '_' + df['unit']
        return df

    @classmethod  
    def read_access_servers(cls, id_:Union[int, List[int]]=None):
        '''
        >>> len(PGFacade.read_access_servers())>0
        True
        '''
        id_ = make_sure_list(id_)
        cols = ['server_ip1', 'id']
        sql = text(f"select {','.join(cols)} from access_servers")
        df = pd.read_sql(sql, con=_ENGINE)
        if len(id_)>0:
            df = df[df['id'].isin(id_)]
        return df

    @classmethod  
    def read_model_device(cls, device_id:List[str]=None, device_name:List[str]=[], set_id:List[str]=None):
        '''
        >>> len(PGFacade.read_model_device())>0
        True
        '''
        device_id = make_sure_list(device_id)
        device_name = make_sure_list(device_name)
        set_id = make_sure_list(set_id)
        cols = ['point_set_id as set_id', 'device_id', 'device_type_id','device_name', 'id']
        sql = text(f"select {','.join(cols)} from model_device")
        df = pd.read_sql(sql, con=_ENGINE)
        if len(device_id)>0:
            df = df[df['device_id'].isin(device_id)]
        if len(device_name)>0:
            df = df[df['device_name'].isin(device_name)]
        if len(set_id)>0:
            df = df[df['set_id'].isin(set_id)]
        ip_df = cls.read_access_servers()
        rev = pd.merge(df, ip_df, how='left', on='id')
        return rev
    
    @classmethod  
    def read_model_factory(cls):
        '''
        >>> len(PGFacade.read_model_factory())>0
        True
        '''
        cols = ['factory_name', 'capacity', 'longtitude', 'latitude']
        sql = text(f"select {','.join(cols)} from model_factory")
        df = pd.read_sql(sql, con=_ENGINE)
        return df
    
    @classmethod  
    def read_model_code_descr(cls, set_id:str=None):
        '''
        >>> len(PGFacade.read_model_code_descr(set_id='20835'))>0
        True
        >>> len(PGFacade.read_model_code_descr())>0
        True
        '''
        cols = ['set_id', 'var_path', 'code', 'var_name']
        sql = f"select {','.join(cols)} from model_code_descr"
        if set_id is not None:
            sql += f" where set_id='{set_id}'"
        df = pd.read_sql(text(sql), con=_ENGINE)
        return df
    
    @classmethod  
    def read_data_fault(cls, device_id:Union[List[str], str]=None):
        '''
        >>> len(PGFacade.read_data_fault(device_id=['s10001','s10002']))>0
        True
        >>> len(PGFacade.read_data_fault(device_id='s10001'))>0
        True
        ''' 
        device_id = make_sure_list(device_id)
        cols = ['device_id', 'val', 'begin_tm', 'end_tm']
        sql = f"select {','.join(cols)} from data_fault"
        if len(device_id)==1:
            sql += f" where device_id='{device_id[0]}'"
        elif len(device_id)>1:
            sql += f''' where device_id in ('{"','".join(device_id)}')'''
        df = pd.read_sql(text(sql), con=_ENGINE)
        return df
    
    @classmethod  
    def read_model_powercurve_current(cls, set_id):
        '''
        >>> len(PGFacade.read_model_powercurve_current(set_id='20835'))>0
        True
        '''
        device_type_id = cls.read_model_device(set_id=set_id)['device_type_id'].iloc[0]
        sql = f'''
            select wind_spd as mean_wind_speed, power as mean_power 
            from model_powcurve_current 
            where device_type_id='{device_type_id}'
            '''
        df = pd.read_sql(text(sql), con=_ENGINE)
        return df
    
    @classmethod 
    def _read_anomaly_log(cls, tbname:str, device_id:str, val:list[str]=[], start_time=None, end_time=None):
        val = make_sure_list(val)
        sql = f'''
            select device_id, val, begin_tm, end_tm
            from {tbname}
            where device_id='{device_id}'
            '''
        if len(val)>0:
            val = [str(i) for i in val]
            sql += f''' and val in ('{"','".join(val)}')'''
        if start_time is not None:
            sql += f" and begin_tm>='{make_sure_datetime(start_time)}'"
        if end_time is not None:
            sql += f" and begin_tm<'{make_sure_datetime(end_time)}'"
        return pd.read_sql(text(sql), con=_ENGINE)        
    
     
    @classmethod  
    def read_data_alarm(cls, device_id:str, val:list[str]=[], start_time=None, end_time=None):
        '''
        >>> df = PGFacade.read_data_alarm('s10003', val=[28012, 20051], start_time='2022-12-12', end_time='2023-12-12')
        >>> df.shape[0]>0
        True
        '''
        return cls._read_anomaly_log(tbname='data_alarm', device_id=device_id, val=val, start_time=start_time, end_time=end_time)      
 
 
    @classmethod  
    def read_data_fault(cls, device_id:str, val:list[str]=[], start_time=None, end_time=None):
        '''
        >>> df = PGFacade.read_data_fault('s10003', val=[13010, 11017], start_time='2022-12-12', end_time='2023-12-12')
        >>> df.shape[0]>0
        True
        '''
        return cls._read_anomaly_log(tbname='data_fault', device_id=device_id, val=val, start_time=start_time, end_time=end_time)      

    @classmethod  
    def read_data_msg(cls, device_id:str, val:list[str]=[], start_time=None, end_time=None):
        '''
        >>> df = PGFacade.read_data_msg('s10003', val=[17037, 11114], start_time='2022-12-12', end_time='2023-12-12')
        >>> df.shape[0]>0
        True
        '''
        return cls._read_anomaly_log(tbname='data_msg', device_id=device_id, val=val, start_time=start_time, end_time=end_time)     
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
