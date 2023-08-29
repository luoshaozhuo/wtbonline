# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:21:08 2023

@author: luosz

数据库操作函数
"""
# =============================================================================
# import
# =============================================================================
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, text
import inspect
import pandas as pd
import numpy as np
from collections.abc import Iterable

try:
    from . import config as cfg
    from . import model
except:
    import config as cfg
    import model

# =============================================================================
# constant
# =============================================================================
ENGINE_MYSQL = create_engine(cfg.URI)

# =============================================================================
# funcion
# =============================================================================
def get_column_name(df):
    '''
    中文名加单位，如“电网有功功率(kW)”
    df : pd.DataFrame，如下
                  point_name  unit
    var_name
    var_246           电网有功功率    kW
    var_101         1#叶片实际角度     °
    var_102         2#叶片实际角度     °
    var_103         3#叶片实际角度     °
    '''
    ld = lambda x:x['point_name'] if x['unit'] is None else (f"{x['point_name']}_({x['unit']})")
    return [ld(r) for i,r in df.iterrows()]

def _to_list(x):
    if x is None:
        x = []
    elif isinstance(x, str) or (not isinstance(x, Iterable)):
        x = [x]
    else:
        x = list(x)
    return x

def select_clause(table, columns='*'):
    columns = _to_list(columns)
    sql = f'''select `{'`,`'.join(columns)}` from {table.__tablename__}'''
    sql = sql.replace('`*`','*').replace('`;`','')
    return sql

def where_clause(name, val, sql, params, conj='and', comp='='):
    params = params.copy()
    if val is None:
        return sql, params
    if sql.find('where')<0:
        sql += ' where'
        conj = ''
    if not isinstance(val, (list, tuple, pd.Series, np.ndarray)):
        params.append(val)
        sql += f'''{conj} `{name}`{comp}%s '''
    elif len(val)<1:
        return sql, params
    else:
        params += list(val)
        sql += f'''{conj} `{name}` in ({','.join(['%s']*len(val))}) '''
    return sql, params

def limit_clause(sql, limit):
    if isinstance(limit, int):
        sql += f' order By Rand() limit {limit}'
    return sql

def read_sql(sql, params=[]):
    return pd.read_sql(sql, ENGINE_MYSQL, params=tuple(params))


# =============================================================================
# mysql hanlder
# =============================================================================
def truncate_table(table):
    with sessionmaker(create_engine(cfg.URI))() as session:
        session.execute(text(f'truncate table {table.__tablename__}'))

def drop_database(dbname='online'):
    with sessionmaker(create_engine(cfg.URI_WITHOUT_DB))() as session:
        session.execute(text(f'drop database if exists {dbname}'))

def create_database(dbname='online'):
    sql = f'''create database if not exists {dbname} DEFAULT CHARSET utf8mb4
              COLLATE utf8mb4_general_ci'''
    with sessionmaker(create_engine(cfg.URI_WITHOUT_DB))() as session:
        session.execute(text(sql))

def drop_table(table=None):
    if table is None:
        for i,j in inspect.getmembers(model, inspect.isclass):
            if i=='Base' or i=='SQLAlchemy' or not hasattr(j, 'metadata'):
                continue
            j.metadata.drop_all(ENGINE_MYSQL)
    else:
        table.metadata.drop_all(ENGINE_MYSQL)

def create_table(table=None):
    ''' 创建model模块里面的所有表 '''
    for i,j in inspect.getmembers(model, inspect.isclass):
        if i=='Base' or i=='SQLAlchemy' or not hasattr(j, 'metadata'):
            continue
        j.metadata.create_all(ENGINE_MYSQL)

def update_one(sr, key_, table):
    ''' 更新数据
    若给定keys，则先删除原有数据记录再插入
    '''
    with sessionmaker(ENGINE_MYSQL)() as session:
        query = session.query(table).filter(table.__dict__[key_]==sr[key_])
        sr.pop(key_)
        query.update(sr.to_dict())
        session.commit()

def insert(df, table, keys=None):
    ''' 插入数据
    若给定keys，则先删除原有数据记录再插入
    '''
    keys = _to_list(keys)
    if len(keys)>0:
        delete(df[keys], table)

    entries = []
    for _,row in df.iterrows():
        row = row.where(row.notnull(), None)
        entries.append(table(**row.to_dict()))

    with sessionmaker(ENGINE_MYSQL)() as session:
        session.add_all(entries)
        session.commit()

def delete(df, table):
    ''' 删除记录
    df : pd.DataFrame
        过滤条件，df中所有字段以and的逻辑筛选数据。如需删除整表所有数据，传入None
    table : flask_sqlalchemy.model.DefaultMeta
        数据表类
    '''
    if isinstance(df, pd.DataFrame) and df.shape[0]>0:
        cond = and_(*[table.__dict__[col].in_(df[col]) for col in df.columns])
    elif df is None:
        cond = True
    else:
        return
    with sessionmaker(ENGINE_MYSQL)() as session:
        query = session.query(table).filter(cond)
        query.delete()
        session.commit()


def read_model_point(
        set_id:(list or int or str)=None,
        point_id:(list or int or str)=None,
        point_name:(list or int or str)=None,
        var_name:(list or int or str)=None,
        unit:(list or int or str)=None,
        datatype:(list or int or str)=None,
        select:int=None,
        statistics:int=None,
        columns:list = ['set_id', 'point_id', 'point_name', 'var_name', 'unit',
                        'datatype' ,'select', 'stat_opeartion', 'stat_sample',
                        'stat_accumlation'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.TurbineModelPoint, columns)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('point_id', point_id, sql, params)
    sql,params = where_clause('point_name', point_name, sql, params)
    sql,params = where_clause('var_name', var_name, sql, params)
    sql,params = where_clause('unit', unit, sql, params)
    sql,params = where_clause('datatype', datatype, sql, params)
    sql,params = where_clause('select', select, sql, params)
    sql,params = where_clause('statistics', statistics, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_statistics_sample(
        _id:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        start_time = None,
        end_time = None,
        columns:list = ['*'],
        limit:int=None,
        ):
    if (end_time==start_time) and (start_time is not None):
        end_time = pd.to_datetime(start_time) + pd.Timedelta('1d')
    params = list()
    sql = select_clause(model.StatisticsSample, columns)
    if _id is not None:
        sql,params = where_clause('id', _id, sql, params)
    else:
        sql,params = where_clause('set_id', set_id, sql, params)
        sql,params = where_clause('turbine_id', turbine_id, sql, params)
        sql,params = where_clause('start_time', start_time, sql, params, comp='>=')
        sql,params = where_clause('start_time', end_time, sql, params, comp='<')
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_statistics_accumulattion(
        _id:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.StatisticsAccumulation, columns)
    if _id is not None:
        sql,params = where_clause('id', _id, sql, params)
    else:
        sql,params = where_clause('set_id', set_id, sql, params)
        sql,params = where_clause('turbine_id', turbine_id, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_model_anormaly(
        model_id:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        sample_id:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.ModelAnormaly, columns)
    sql,params = where_clause('model_id', model_id, sql, params)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('turbine_id', turbine_id, sql, params)
    sql,params = where_clause('sample_id', sample_id, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_model_label(
        username:(list or int or str)=None,
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        sample_id:(list or int or str)=None,
        is_anormaly:int=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.ModelLabel, columns)
    sql,params = where_clause('username', username, sql, params)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('turbine_id', turbine_id, sql, params)
    sql,params = where_clause('sample_id', sample_id, sql, params)
    sql,params = where_clause('is_anormaly', is_anormaly, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_windfarm_configuration(
        set_id:(list or int or str)=None,
        turbine_id:(list or int or str)=None,
        map_id:(list or int or str)=None,
        on_grid_date:str=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.WindfarmConfiguration, columns)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('turbine_id', turbine_id, sql, params)
    sql,params = where_clause('map_id', map_id, sql, params)
    sql,params = where_clause('on_grid_date', on_grid_date, sql, params, comp='>=')
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)


def read_statistics_configuration(
        table_name:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.StatisticsConfiguration, columns)
    sql,params = where_clause('table_name', table_name, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_statistics_parameter(
        table_name:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.StatisticsParameter, columns)
    sql,params = where_clause('table_name', table_name, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_page_setting(
        page:(list or int or str)=None,
        card:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.PageSetting, columns)
    sql,params = where_clause('page', page, sql, params)
    sql,params = where_clause('card', card, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_report_configuration(
        set_id:(list or int or str)=None,
        chapter:(list or int or str)=None,
        section:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.ReportConfiguration, columns)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('chapter', chapter, sql, params)
    sql,params = where_clause('section', section, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_report_scheme(
        set_id:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.ReportScheme, columns)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)


def read_turbine_charateristic_frequency(
        set_id:(list or int or str)=None,
        point_name:(list or int or str)=None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.TurbineCharacteristicFrequency, columns)
    sql,params = where_clause('set_id', set_id, sql, params)
    sql,params = where_clause('point_name', point_name, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_user(
        username:(list or int or str)=None,
        privilege:list = None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.User, columns=columns)
    sql,params = where_clause('username', username, sql, params)
    sql,params = where_clause('privilege', privilege, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)

def read_timed_task(
        name:(list or int or str)=None,
        status:(list or int or str)=None,
        _type:(list or int or str)=None,
        period:(list or int or str)=None,
        window:(list or int or str) = None,
        columns:list = ['*'],
        limit:int=None,
        ):
    params = list()
    sql = select_clause(model.TimedTask, columns=columns)
    sql,params = where_clause('name', name, sql, params)
    sql,params = where_clause('status', status, sql, params)
    sql,params = where_clause('type', _type, sql, params)
    sql,params = where_clause('period', period, sql, params)
    sql,params = where_clause('window', window, sql, params)
    sql = limit_clause(sql, limit)
    return read_sql(sql, params)


def get_available_set_id():
    sql = f'''
          select distinct(set_id) from {model.StatisticsSample.__tablename__}
          '''
    return read_sql(sql)['set_id']

def get_available_map_id(set_id):
    sql = f'''
            select map_id from {model.WindfarmConfiguration.__tablename__} a
            inner join
            (select distinct(turbine_id) from {model.StatisticsSample.__tablename__} b
             where set_id=%s) b
            on a.turbine_id=b.turbine_id
            where set_id=%s
          '''
    return read_sql(sql, params=[set_id]*2)['map_id']

def map_id_to_turbine_id(set_id, map_id):
    df = read_windfarm_configuration(set_id=set_id,
                                     map_id=map_id,
                                     columns=['turbine_id'])
    return df['turbine_id']

def get_available_date(set_id, turbine_id):
    sql = f'''
          select distinct(date(start_time)) as date
          from {model.StatisticsSample.__tablename__}
          where set_id=%s and turbine_id=%s
          '''
    df = read_sql(sql, params=[set_id, turbine_id])
    df['date'] = pd.to_datetime(df['date'])
    return df['date']