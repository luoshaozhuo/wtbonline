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
from sqlalchemy import create_engine, text, func, select, delete, update, insert
import inspect
from typing import Union, Optional, Mapping, List, Any
from collections.abc import Iterable
from functools import partial
from contextlib import contextmanager

from wtbonline._db.config import RSDB_URI, SESSION_TIMEOUT
from wtbonline._db.rsdb import model
from wtbonline._db.common import (make_sure_list, make_sure_dict, make_sure_dataframe)

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
class ORMFactory:
    def __init__(self):
        self._tbl_mapping = self._get_table_mapping()

    @property
    def tbl_mapping(self):
        return self._tbl_mapping

    def _get_table_mapping(self):
        rev = {}
        for i,j in inspect.getmembers(model, inspect.isclass):
            if str(j).find('rsdb')>-1:
                rev.update({j.__tablename__:j})
        return rev

    def get(self, tbname):
        ''' 通过数据表名获取orm对象 '''
        return self._tbl_mapping.get(tbname)

class RSDBDAO():
    def __init__(self, engine=None):
        self.factory = ORMFactory()
        self.engine = create_engine_() if engine is None else engine
        self.Session = sessionmaker(self.engine, expire_on_commit=True)

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

    def select_(sel, model_, columns:List[str]=[], func_dct:Mapping[str, List[str]]={}):
        '''
        columns: list
            list of attibutes, aka, columns
        func_dct: dictionary
            column:functions pares like {'wndspd':['mean', 'max]}
        >>> dao = RSDBDAO()
        >>> model_ = dao.factory.get('user')
        >>> columns = ['username', 'privilege']
        >>> print(dao.select_(model_, columns))
        SELECT "user".username, "user".privilege 
        FROM "user"
        >>> func_dct = {'id':['abs', 'floor']}
        >>> print(dao.select_(model_, columns, func_dct))
        SELECT "user".username, "user".privilege, abs("user".id) AS id_abs, floor("user".id) AS id_floor 
        FROM "user"
        '''
        if len(columns)==0 and len(func_dct)==0:
            stmt = select(model_)
        else:
            columns = [getattr(model_, i) for i in columns]
            aug = []
            for key_ in func_dct:
                aug += [
                    eval(f'func.{f}')(getattr(model_, key_)).label(f'{key_}_{f}')
                    for f in func_dct[key_]
                    ]
            stmt = select(*(columns+aug))
        return stmt 
            
    def where_(
            self, 
            stmt, 
            model_, 
            eq_dct:Mapping[str, Union[str, int, float]] = {},
            lge_dct:Mapping[str, Union[str, int, float]] = {},
            lt_dct:Mapping[str, Union[str, int, float]] = {}, 
            in_dct:Mapping[str, Union[str, int, float]] = {}
            ):
        '''
        >>> dao = RSDBDAO()
        >>> model_ = dao.factory.get('user')
        >>> stmt = dao.select_(model_)
        >>> print(dao.where_(stmt, model_, eq_dct={'username':'admin', 'id':1}, lge_dct={'id':1}, lt_dct={'id':1}, in_dct={'id':[1,2,3]}))
        SELECT "user".id, "user".username, "user".password, "user".privilege 
        FROM "user" 
        WHERE "user".username = :username_1 AND "user".id = :id_1 AND "user".id >= :id_2 AND "user".id < :id_3 AND "user".id IN (__[POSTCOMPILE_id_4])
        '''
        aug = []
        for key_ in eq_dct:
            aug.append(getattr(model_, key_)==eq_dct[key_])
        for key_ in lge_dct:
            aug.append(getattr(model_, key_)>=lge_dct[key_])
        for key_ in lt_dct:
            aug.append(getattr(model_, key_)<lt_dct[key_])
        for key_ in in_dct:
            aug.append(getattr(model_, key_).in_(in_dct[key_]))
            
        if len(aug)>0:
            stmt = stmt.where(*aug)
        return stmt

    def read_sql(self, stmt:Union[str, Select], timeout=SESSION_TIMEOUT)->pd.DataFrame:
        ''' 通用sql查询，需要注意注入攻击
        >>> dao = RSDBDAO()
        >>> try:
        ...     dao.read_sql('select * from statistics_daily', timeout=1)
        ... except Exception as e:
        ...     print(e)
        (pymysql.err.OperationalError) (3024, 'Query execution was interrupted, maximum statement execution time exceeded')
        [SQL: select * from statistics_daily]
        (Background on this error at: https://sqlalche.me/e/20/e3q8)
        >>> stmt = dao.select_(model.User)
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
              columns:Optional[List[str]]=None,
              eq_clause:Optional[Mapping[str, str]]=None, 
              in_clause:Optional[Mapping[str, str]]=None, 
              lge_clause:Optional[Mapping[str, str]]=None, 
              lt_clause:Optional[Mapping[str, str]]=None, 
              limit:int=None,
              unique:bool=False,
              func_dct:Mapping[str, List[str]]=None,
              groupby:Optional[Union[str, List[str]]]=None,
              orderby:Optional[Union[str, List[str]]]=None,
              random:bool=False,
              timeout = SESSION_TIMEOUT
              )->pd.DataFrame:
        '''
        >>> dao = RSDBDAO()
        >>> columns = ['id','set_id','date']
        >>> eq_clause = {'id':300}
        >>> lge_clause = {'id':300, 'id':500}
        >>> lt_clause = {'id':600}
        >>> in_clause = {'fault_codes':['0']}
        >>> func_dct = {'id':['max', 'min'], 'turbine_id':['count']}
        >>> dao.query('statistics_daily', columns=columns).columns
        Index(['id', 'set_id', 'date'], dtype='object')
        >>> dao.query('statistics_daily', columns=columns, eq_clause=eq_clause).shape
        (1, 3)
        >>> dao.query('statistics_daily', columns=columns, lge_clause=lge_clause).shape[0]>0
        True
        >>> dao.query('statistics_daily', lge_clause=lge_clause, lt_clause=lt_clause).shape[0]>0
        True
        >>> dao.query('statistics_daily', in_clause=in_clause).shape[0]>0
        True
        >>> dao.query('statistics_daily', limit=1).shape[0]==1
        True
        >>> dao.query('statistics_daily', func_dct=func_dct).shape
        (1, 3)
        >>> dao.query('statistics_daily', func_dct=func_dct, groupby='fault_codes', orderby='fault_codes').shape[0]>1
        True
        >>> dao.query('statistics_daily', random=True, timeout=1)
        Traceback (most recent call last):
            ...
        sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (3024, 'Query execution was interrupted, maximum statement execution time exceeded')
        [SQL: SELECT statistics_daily.id, statistics_daily.set_id, statistics_daily.turbine_id, statistics_daily.date, statistics_daily.count_sample, statistics_daily.energy_output, statistics_daily.fault_codes, statistics_daily.create_time 
        FROM statistics_daily ORDER BY rand()]
        (Background on this error at: https://sqlalche.me/e/20/e3q8)
        >>> dao.query('statistics_daily', random=True, limit=100)['id'].max()>100
        True
        '''
        columns = make_sure_list(columns)
        eq_clause = make_sure_dict(eq_clause)
        in_clause = make_sure_dict(in_clause)
        lge_clause = make_sure_dict(lge_clause)
        lt_clause = make_sure_dict(lt_clause)
        func_dct = make_sure_dict(func_dct)
        for i in func_dct:
            func_dct[i] = make_sure_list(func_dct[i])
        model_ = self.factory.get(tbname)
        groupby = make_sure_list(groupby)
        orderby = make_sure_list(orderby)
        assert model_ is not None, f'table {tbname} not defined in model.py'
        columns = columns if len(groupby)<1 else groupby
        
        stmt = self.select_(model_=model_, columns=columns, func_dct=func_dct)
        stmt = self.where_(stmt, model_=model_, eq_dct=eq_clause, lge_dct=lge_clause, lt_dct=lt_clause, in_dct=in_clause)
        stmt = stmt if unique==False else stmt.distinct()
        if random:
            stmt = stmt.order_by(func.random())
        elif len(orderby)>0:
            stmt = stmt.order_by(*[getattr(model_, i) for i in orderby])
        stmt = stmt if len(groupby)==0 else stmt.group_by(*[getattr(model_, i) for i in groupby])
        stmt = stmt if limit is None else stmt.limit(limit)
        return self.read_sql(stmt, timeout)
    
    def truncate(self, tbname, timeout=SESSION_TIMEOUT):
        with self.engine.connect() as conn:
            with query_timeout(conn, timeout):
                conn.execute(text(f'truncate {tbname}')) 
                conn.commit() 
    
    def insert(self, df:Union[dict, pd.DataFrame], tbname:str, timeout=30000):
        '''
        >>> dao = RSDBDAO()
        >>> dao.truncate('statistics_fault')
        >>> set_id = ['20835']*10
        >>> turbine_id = ['s10001']*10
        >>> date = ['2023-01-01']*10
        >>> fault_id = ['a12']*10
        >>> timestamp = ['2023-02-02 11:11:11']*10
        >>> create_time = timestamp
        >>> dct = dict(set_id=set_id, turbine_id=turbine_id, date=date, fault_id=fault_id, timestamp=timestamp, create_time=create_time)
        >>> df = pd.DataFrame(dct)
        >>> dao.insert(df, 'statistics_fault')
        >>> dao.query('statistics_fault', func_dct={'id':'count'})['id_count'].squeeze()>=2
        True
        >>> dao.truncate('statistics_fault')
        >>> dao.insert(df, 'statistics_fault')
        >>> dao.query('statistics_fault', lt_clause={'id':11}, func_dct={'id':'count'})['id_count'].squeeze()==10
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
        with self.Session() as session:
            with query_timeout(session, timeout=timeout):
                session.execute(stmt)
                session.commit()   
        
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
        >>> dao.update('statistics_daily', lt_clause={'id':11}, new_values={'turbine_id':value})
        >>> dao.query('statistics_daily', eq_clause={'turbine_id':value}).shape[0]==10
        True
        '''
        new_values = make_sure_dict(new_values)
        if len(new_values)<1:
            return

        eq_clause = make_sure_dict(eq_clause)
        in_clause = make_sure_dict(in_clause)
        lge_clause = make_sure_dict(lge_clause)
        lt_clause = make_sure_dict(lt_clause)
        model_ = self.factory.get(tbname)
        stmt = update(model_)
        stmt = self.where_(stmt, model_, eq_dct=eq_clause, lge_dct=lge_clause, lt_dct=lt_clause, in_dct=in_clause)
        stmt = stmt.values({getattr(model_, key_):new_values[key_] for key_ in new_values})
        with self.Session() as session:
            with query_timeout(session, timeout=timeout):
                session.execute(stmt)
                session.commit()

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
        >>> len(dao.query('statistics_fault', eq_clause={'id':1}))==1
        True
        >>> dao.delete('statistics_fault', eq_clause={'id':1})
        >>> len(dao.query('statistics_fault', eq_clause={'id':1}))==0
        True
        >>> dao.delete('statistics_fault', lge_clause={'id':1})
        >>> len(dao.query('statistics_fault'))==0
        True
        '''
        eq_clause = make_sure_dict(eq_clause)
        in_clause = make_sure_dict(in_clause)
        lge_clause = make_sure_dict(lge_clause)
        lt_clause = make_sure_dict(lt_clause)
        model_ = self.factory.get(tbname)
        stmt = delete(model_)
        stmt = self.where_(stmt, model_, eq_dct=eq_clause, lge_dct=lge_clause, lt_dct=lt_clause, in_dct=in_clause)
        with self.Session() as session:
            with query_timeout(session, timeout=timeout):
                session.execute(stmt)
                session.commit()
      

RSDB = RSDBDAO()

if __name__ == "__main__":
    '''
    测试前需要提前对online库做以下处理:
    statistics_daily生成1万条样本数据（可通过navicat实现）
    生成规则如下：
    1、id, 不设置， 让系统自动填充
    2、count_sample，正则表达式, {1-9}{3,4}
    '''
    import doctest
    doctest.testmod()
