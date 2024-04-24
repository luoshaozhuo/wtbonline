# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

#%% import
from numpy import isin
from numpy import random
import pandas as pd

from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text, func, delete, update, insert
from typing import Union, Optional, Mapping, List, Any
from functools import partial
from contextlib import contextmanager

from wtbonline._db.config import RSDB_URI, SESSION_TIMEOUT
from wtbonline._db.rsdb import model
from wtbonline._common.utils import (make_sure_list, make_sure_dict, make_sure_dataframe)
from wtbonline._db.rsdb.factory import ORMFactory
from wtbonline._db.rsdb.clause import Select, Where

#%% function
create_engine_ = partial(create_engine, url=RSDB_URI, pool_pre_ping=True, pool_timeout=1)

@contextmanager
def query_timeout(session, timeout):
    previous_timeout = session.execute(text('SELECT @@MAX_EXECUTION_TIME')).scalar()
    session.execute(text(f'SET SESSION MAX_EXECUTION_TIME={timeout}'))
    session.commit()
    try:
        yield
    finally:
        session.execute(text(f'SET SESSION MAX_EXECUTION_TIME={previous_timeout}'))
        session.commit()
        
#%% class
class RSDBDAO():
    def __init__(self, engine=None):
        self.factory = ORMFactory()
        self.engine = create_engine_() if engine is None else engine
        # self.Session = sessionmaker(self.engine, expire_on_commit=True)

    def get_session(self):
        '''
        返回类sessionmaker对象的调用
        用sessionmaker而不是Session，是为了省去每一次都绑定engine
        '''
        return sessionmaker(self.engine, expire_on_commit=True)

    def init_database(self, uri=RSDB_URI, timeout=SESSION_TIMEOUT):
        '''
        初始化时，自动检测数据库及数据表完整性，自动创建缺少部分
        >>> dao = RSDBDAO()
        >>> dao.init_database()
        '''
        # create database
        short_uri, dbname = uri.rsplit('/', 1)
        sql = f'''create database if not exists {dbname} DEFAULT CHARSET utf8mb4
            COLLATE utf8mb4_general_ci'''
        with Session(create_engine_(url=short_uri)) as session:
            with query_timeout(session, timeout):
                session.execute(text(sql))
        # create tables
        engine = create_engine(uri)
        model.db.metadata.create_all(engine)

    def read_sql(self, stmt:Union[str, Select], timeout=SESSION_TIMEOUT)->pd.DataFrame:
        ''' 通用sql查询，需要注意注入攻击
        >>> dao = RSDBDAO()
        >>> try:
        ...     dao.read_sql('select * from statistics_sample', timeout=1)
        ... except Exception as e:
        ...     print(e)
        (pymysql.err.OperationalError) (3024, 'Query execution was interrupted, maximum statement execution time exceeded')
        [SQL: select * from statistics_sample]
        (Background on this error at: https://sqlalche.me/e/20/e3q8)
        >>> stmt = Select()(model.User)
        >>> len(dao.read_sql(stmt)) > 0
        True
        '''
        with self.engine.connect() as conn:
            with query_timeout(conn, timeout):
                for i in range(2):
                    try:
                        if isinstance(stmt, str):
                            stmt = text(stmt)
                        rs = conn.execute(stmt)
                        break
                    except:
                        import time
                        time.sleep(0.5)
                else:
                    rs = conn.execute(stmt)
            df = pd.DataFrame(rs.all(), columns=rs.keys())
        return df
    
    def query(self, 
              tbname:str,
              *, 
              columns:Optional[List[Union[str, Mapping[str, List[str]]]]]=None,
              eq_clause:Optional[Mapping[str, str]]=None, 
              in_clause:Optional[Mapping[str, str]]=None, 
              lge_clause:Optional[Mapping[str, str]]=None, 
              lt_clause:Optional[Mapping[str, str]]=None, 
              limit:int=None,
              unique:bool=False,
              groupby:Optional[Union[str, List[str]]]=None,
              orderby:Optional[Union[str, List[str]]]=None,
              random:bool=False,
              timeout = SESSION_TIMEOUT
              )->pd.DataFrame:
        '''
        >>> dao = RSDBDAO()
        >>> tbname='statistics_sample'
        >>> columns = ['id','set_id','device_id']
        >>> eq_clause = {'id':300}
        >>> lge_clause = {'id':300, 'id':500}
        >>> lt_clause = {'id':600}
        >>> in_clause = {'id':['96', '94']}
        >>> func_dct = {'id':['max', 'min'], 'device_id':['count']}
        >>> dao.query(tbname, columns=columns).columns.tolist()==columns
        True
        >>> dao.query(tbname, columns=columns, eq_clause=eq_clause).shape
        (1, 3)
        >>> dao.query(tbname, columns=columns, lge_clause=lge_clause).shape[0]>0
        True
        >>> dao.query(tbname, lge_clause=lge_clause, lt_clause=lt_clause).shape[0]>0
        True
        >>> dao.query(tbname, in_clause=in_clause).shape[0]>0
        True
        >>> dao.query(tbname, limit=1).shape[0]==1
        True
        >>> dao.query(tbname, columns=func_dct).columns.tolist()
        ['id_max', 'id_min', 'device_id_count']
        >>> dao.query(tbname, columns=func_dct, groupby='set_id', orderby='set_id').columns.tolist()
        ['id_max', 'id_min', 'device_id_count', 'set_id']
        >>> dao.query(tbname, random=True, limit=100)['id'].max()>100
        True
        '''
        model_ = self.factory.get(tbname)
        groupby = make_sure_list(groupby)
        orderby = make_sure_list(orderby)
        assert model_ is not None, f'table {tbname} not defined in model.py'
        
        stmt = Select()(model_=model_, params=[columns, groupby])
        stmt = Where()(model_=model_, params={'eq':eq_clause,'lge':lge_clause,'lt':lt_clause,'in':in_clause}, stmt=stmt)        
        
        stmt = stmt if unique==False else stmt.distinct()
        if random:
            stmt = stmt.order_by(func.random())
        elif len(orderby)>0:
            stmt = stmt.order_by(*[getattr(model_, i) for i in orderby])
        stmt = stmt if len(groupby)==0 else stmt.group_by(*[getattr(model_, i) for i in groupby])
        stmt = stmt if limit is None else stmt.limit(limit)
        return self.read_sql(stmt, timeout)
    
    def execute(self, stmt, timeout=SESSION_TIMEOUT):
        with self.get_session()() as session:
            with query_timeout(session, timeout=timeout):
                session.execute(stmt)
                session.commit()
    
    def truncate(self, tbname, timeout=SESSION_TIMEOUT):
        '''
        # >>> dao = RSDBDAO()
        # >>> dao.truncate('windfarm_configuration')
        '''
        stmt = f'truncate {tbname}'
        self.execute(text(f'truncate {stmt}'), timeout=timeout)        
        # with self.engine.connect() as conn:
        #     with query_timeout(conn, timeout):
        #         conn.execute(text(f'truncate {tbname}')) 
        #         conn.commit() 
    
    def insert(self, df:Union[dict, pd.DataFrame], tbname:str, timeout=30000):
        '''
        >>> dao = RSDBDAO()
        >>> dao.truncate('statistics_fault')
        >>> set_id = ['20835']*10
        >>> device_id = ['s10001']*10
        >>> start_time = ['2023-01-01']*10
        >>> end_time = start_time
        >>> val=['111']*10
        >>> fault_id = ['12']*10
        >>> fault_type = ['a12']*10
        >>> timestamp = ['2023-02-02 11:11:11']*10
        >>> create_time = timestamp
        >>> dct = dict(set_id=set_id, device_id=device_id, fault_id=fault_id, value=val, fault_type=fault_type, start_time=start_time, end_time=end_time, create_time=create_time)
        >>> dao.insert(dct, 'statistics_fault')
        >>> dao.query('statistics_fault', columns={'id':'count'})['id_count'].squeeze()>=2
        True
        >>> dao.truncate('statistics_fault')
        >>> dao.insert(df, 'statistics_fault')
        >>> dao.query('statistics_fault', lt_clause={'id':11}, columns={'id':'count'})['id_count'].squeeze()==10
        True
        '''
        df = make_sure_dataframe(df)
        if len(df)<1:
            return
        cols = df.select_dtypes(bool).columns
        df[cols] = df[cols].astype(str)
        Model = ORMFactory().get(tbname)
        assert Model is not None, f'table {tbname} not defined in model.py'
        stmt = insert(Model).values(df.to_dict('records'))
        self.execute(stmt, timeout=timeout)          
        # with self.get_session()() as session:
        #     with query_timeout(session, timeout=timeout):
        #         session.execute(stmt)
        #         session.commit()   
        
    def update(self, 
               tbname:str,
               new_values:Mapping[str, Any],
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, str]]=None, 
               lge_clause:Optional[Mapping[str, str]]=None, 
               lt_clause:Optional[Mapping[str, str]]=None,
               timeout=30000
               ):
        ''' 
        >>> dao = RSDBDAO()
        >>> value = f'a{random.randint(10000)}'
        >>> dao.update('statistics_fault', lt_clause={'id':11}, new_values={'device_id':value})
        >>> dao.query('statistics_fault', eq_clause={'device_id':value}, lt_clause={'id':11}).shape[0]==10
        True
        '''
        new_values = make_sure_dict(new_values)
        if len(new_values)<1:
            return
        model_ = self.factory.get(tbname)
        stmt = update(model_)
        stmt = Where()(model_=model_, params={'eq':eq_clause,'lge':lge_clause,'lt':lt_clause,'in':in_clause}, stmt=stmt)         
        stmt = stmt.values({getattr(model_, key_):new_values[key_] for key_ in new_values})
        # with self.get_session()() as session:
        #     with query_timeout(session, timeout=timeout):
        #         session.execute(stmt)
        #         session.commit()'
        self.execute(stmt, timeout=timeout)  

    def delete(self, 
               tbname:str,
               *, 
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, List[str]]]=None, 
               lge_clause:Optional[Mapping[str, Any]]=None, 
               lt_clause:Optional[Mapping[str, Any]]=None,
               timeout = 30000
               ):
        ''' 删除数据
        >>> dao = RSDBDAO()
        >>> tbname =  'statistics_fault'
        >>> id_ = 5
        >>> len(dao.query(tbname, eq_clause={'id':id_}))==1
        True
        >>> dao.delete(tbname, eq_clause={'id':id_})
        >>> len(dao.query(tbname, eq_clause={'id':id_}))==0
        True
        >>> dao.truncate(tbname)
        '''
        model_ = self.factory.get(tbname)
        stmt = delete(model_)
        stmt = Where()(model_=model_, params={'eq':eq_clause,'lge':lge_clause,'lt':lt_clause,'in':in_clause}, stmt=stmt) 
        self.execute(stmt, timeout=timeout)
        # with self.get_session()() as session:
        #     with query_timeout(session, timeout=timeout):
        #         session.execute(stmt)
        #         session.commit()

RSDB = RSDBDAO()

if __name__ == "__main__":
    '''
    测试前需要提前对online库做以下处理:
    statistics_daily生成1万条样本数据，id系统自增（可通过navicat实现）
    '''
    import doctest
    doctest.testmod()
