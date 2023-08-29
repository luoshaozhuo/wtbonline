# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

# import
import pandas as pd

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text, func
import inspect
from typing import Union, Optional, Mapping, List, Any
from collections.abc import Iterable
from functools import partial

from wtbonline._db.config import RSDB_URI
from wtbonline._db.rsdb import model
from wtbonline._db.common import (make_sure_list, make_sure_dict, make_sure_dataframe)

# class
create_engine_ = partial(create_engine, url=RSDB_URI)

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
    def __init__(self):
        self.factory = ORMFactory()

    def get_session(self):
        '''
        返回类sessionmaker对象的调用
        '''
        return sessionmaker(create_engine_())()

    def init_database(self, uri=RSDB_URI):
        '''
        初始化时，自动检测数据库及数据表完整性，自动创建缺少部分
        >>> dao = RSDBDAO()
        >>> dao.init_database()
        '''
        # create database
        short_uri, dbname = uri.rsplit('/', 1)
        sql = f'''create database if not exists {dbname} DEFAULT CHARSET utf8mb4
            COLLATE utf8mb4_general_ci'''
        with sessionmaker(create_engine(short_uri))() as session:
            session.execute(text(sql))
        # create tables
        engine = create_engine(uri)
        tbl_mapping= self.factory.tbl_mapping
        for i in tbl_mapping:
            tbl_mapping[i].metadata.create_all(engine)

    def read_sql(self, sql:str)->pd.DataFrame:
        ''' 通用sql查询，需要注意注入攻击
        >>> dao = RSDBDAO()
        >>> len(dao.read_sql('show databases'))>0
        True
        '''
        with self.get_session() as session:
            df = pd.read_sql(sql=text(sql), con=session.bind) 
        return df   

    def sel_(sel, session, columns, Model, unique, func_dct:Mapping[str, List[str]]={}):
        '''
        >>> dao = RSDBDAO()
        >>> len(dao.query('user'))>0
        True
        >>> dao.query('user', columns='id').columns.tolist() == ['id']
        True
        >>> dao.query('user', columns=['id', 'username']).columns.tolist() == ['id', 'username']
        True
        '''
        if len(columns)==0 and len(func_dct)==0:
            query = session.query(Model)
        else:
            attributes = [getattr(Model, i) for i in columns]
            for key_ in func_dct:
                attributes += [
                    eval(f'func.{f}')(getattr(Model, key_)).label(f'{key_}_{f}')
                    for f in func_dct[key_]
                    ]
            query = session.query().with_entities(*attributes)
            if unique:
                query = query.distinct(*attributes)
        return query  

    def eq_(self, query, eq_clause):
        '''
        >>> dao = RSDBDAO()
        >>> len(dao.query('user', eq_clause={'username':'admin','privilege':1}))==1
        True
        '''
        query = query if len(eq_clause)==0 else query.filter_by(**eq_clause)
        return query

    def in_(self, query, in_clause, model):
        '''
        >>> dao = RSDBDAO()
        >>> len(dao.query('user', in_clause={'username':['admin', 'senior']}))==1
        True
        >>> len(dao.query('user', in_clause={'username':'admin'}))==1
        True
        >>> len(dao.query('user', in_clause={'username':'admin', 'id':[1,2]}))==1
        True
        '''
        for key_ in in_clause:
            values = make_sure_list(in_clause[key_])
            if len(values)>0:
                query = query.filter(getattr(model, key_).in_(values))
        return query
    
    def lge_(self, query, lge_clause, model):
        '''
        >>> dao = RSDBDAO()
        >>> len(dao.query('user', lge_clause={'privilege':2}))==0
        True
        >>> len(dao.query('user', lge_clause={'privilege':1, 'id':2}))==0
        True
        '''
        for key_ in lge_clause:
            query = query.filter(getattr(model, key_)>=lge_clause[key_])
        return query
    
    def lt_(self, query, lt_clause, model):
        '''
        >>> dao = RSDBDAO()
        >>> len(dao.query('user', lt_clause={'privilege':2}))==1
        True
        >>> len(dao.query('user', lt_clause={'privilege':1, 'id':2}))==0
        True
        '''
        for key_ in lt_clause:
            query = query.filter(getattr(model, key_)<lt_clause[key_])
        return query 

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
              _delete:bool=False,
              _update:bool=False,
              _new_values:Mapping[str, Any]=None
              )->pd.DataFrame:
        columns = make_sure_list(columns)
        eq_clause = make_sure_dict(eq_clause)
        in_clause = make_sure_dict(in_clause)
        lge_clause = make_sure_dict(lge_clause)
        lt_clause = make_sure_dict(lt_clause)
        func_dct = make_sure_dict(func_dct)
        Model = self.factory.get(tbname)
        groupby = make_sure_list(groupby)
        orderby = make_sure_list(orderby)
        assert Model is not None, f'table {tbname} not defined in model.py'
        columns = columns if len(groupby)<1 else groupby
        assert pd.Series(orderby).isin(groupby) if len(groupby)>0 and len(orderby)>0 else True
        with self.get_session() as session:
            query = self.sel_(session, columns, Model, unique, func_dct)
            query = self.eq_(query, eq_clause)
            query = self.in_(query, in_clause, Model)
            query = self.lge_(query, lge_clause, Model)
            query = self.lt_(query, lt_clause, Model)
            if len(orderby)>0:
                query = query.order_by(*[getattr(Model, i) for i in orderby])
            if len(groupby)>0:
                query = query.group_by(*[getattr(Model, i) for i in groupby])
            if limit is not None:
                query = query.limit(limit)
            if _delete:
                query.delete()
                session.commit()
                rev = None
            elif _update:
                query.update(_new_values)
                session.commit()       
                rev = None        
            else:
                try:
                    rev = pd.read_sql(sql=query.statement, con=session.bind) 
                except Exception as e:
                    raise ValueError(f'查询失败{query.statement} {e}')
        return rev
    
    def insert(self, df:Union[dict, pd.DataFrame], tbname:str):
        df = make_sure_dataframe(df)
        if len(df)<1:
            return
        cols = df.select_dtypes(bool).columns
        df[cols] = df[cols].astype(str)
        Model = ORMFactory().get(tbname)
        assert Model is not None, f'table {tbname} not defined in model.py'
        with self.get_session() as session:
            for _,row in df.iterrows():
                session.add(Model(**row.to_dict())) # 备选session.merge
            session.commit()

    def delete(self, 
               tbname:str,
               *, 
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, List[str]]]=None, 
               lge_clause:Optional[Mapping[str, Any]]=None, 
               lt_clause:Optional[Mapping[str, Any]]=None):
        ''' 删除数据
        >>> dao = RSDBDAO()
        >>> dao.insert({'username':'a', 'privilege':3, 'password':'abc'}, 'user')
        >>> len(dao.query('user', eq_clause={'username':'a'}))>0
        True
        >>> dao.delete('user', eq_clause={'username':'a'})
        >>> len(dao.query('user', eq_clause={'username':'a'}))==0
        True
        '''
        _ = self.query(tbname, eq_clause=eq_clause, in_clause=in_clause, 
                       lge_clause=lge_clause, lt_clause=lt_clause, _delete=True)

    def update(self, 
               tbname:str,
               new_values:Mapping[str, Any],
               eq_clause:Optional[Mapping[str, str]]=None, 
               in_clause:Optional[Mapping[str, str]]=None, 
               lge_clause:Optional[Mapping[str, str]]=None, 
               lt_clause:Optional[Mapping[str, str]]=None
               ):
        ''' 删除数据
        >>> dao = RSDBDAO()
        >>> len(dao.query('user', eq_clause={'privilege':1}))==1
        True
        >>> dao.update('user', eq_clause={'privilege':1}, new_values={'privilege':2})
        >>> len(dao.query('user', eq_clause={'privilege':2}))==1
        True
        >>> dao.update('user', eq_clause={'username':'admin'}, new_values={'privilege':1})
        >>> len(dao.query('user', eq_clause={'privilege':1}))==1
        True
        '''
        new_values = make_sure_dict(new_values)
        if len(new_values)<1:
            return
        _ = self.query(tbname, eq_clause=eq_clause, in_clause=in_clause, 
                       lge_clause=lge_clause, lt_clause=lt_clause, _update=True,
                       _new_values=new_values)

RSDB = RSDBDAO()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
