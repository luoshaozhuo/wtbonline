# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:19:56 2023

@author: luosz

准备demo数据
"""

# =============================================================================
# import
# =============================================================================
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from pathlib import Path
import inspect
import time
import os

from _database import config as cfg
from _database import model
from _database import _tdengine as td
from _database import _mysql as msql

# =============================================================================
# constant
# =============================================================================
SQL_ENGINE = create_engine(cfg.URI)
SOURCE_PATH = './data/demo'

# =============================================================================
# function
# =============================================================================
def accumulate(set_id, conf_df):
    ''' 累计值 '''
    columns = conf_df['function'] + '(' + conf_df['var_name'] + ')'
    sql = f'''select {','.join(columns)},device from s_{set_id} group by device'''
    with td.TAOS_Connector(cfg.LOCAL_DRIVER) as scada:
        ret = scada.query(sql)
    ret.columns = conf_df['name'].tolist() + ['turbine_id']
    return ret

def get_statistic_function(conf_df):
    ''' 从数据库读取统计函数 '''
    aggrigation_dct = {}
    agg_df = conf_df[conf_df['var_name']!='-']
    for _,row in agg_df.iterrows():
        func = eval(row['function'])
        value = aggrigation_dct.get(row['var_name'], None)
        if value:
            if isinstance(value, list):
                value = value + [func]
            else:
                value = [value] + [func]
        else:
            value = eval(row['function'])
        aggrigation_dct.update({row['var_name']:value})


    app_df = conf_df[conf_df['var_name']=='-']    
    apply_lst = app_df['function'].tolist()
        
    return aggrigation_dct, agg_df['name'].tolist(), apply_lst, app_df['name'].tolist()

def statistics_of_sample(data_df, conf_df, window_length='10min'):
    ''' 计算统计值 '''
    agg_dct, agg_col, app_lst, app_col = get_statistic_function(conf_df)
    
    ret = []
    for tid, df in data_df.groupby('device'):
        df.set_index('ts', inplace=True)
        resmple = df.resample(window_length)
        temp = resmple.apply(agg_dct).reset_index()
        temp.insert(1, 'device', tid)
        ret.append(temp)   
    ret = pd.concat(ret, ignore_index=True)
    ret.columns = ['start_time', 'turbine_id'] + agg_col
    
    for i in range(len(app_lst)):
        ret[app_col[i]] = eval(app_lst[i].replace('df[', 'ret['))
    
    ret.drop(columns=conf_df[conf_df['keep']==0]['name'], inplace=True)
    return ret

def get_day_range(set_id):
    sql = f'''select first(ts), last(ts) from s_{set_id}'''
    with td.TAOS_Connector(cfg.LOCAL_DRIVER) as scada:
        bounds = scada.query(sql).squeeze().dt.date
    return pd.date_range(bounds[0], bounds[1], freq='1d').tolist()  

def insert_demo_data():
    tables = pd.DataFrame(inspect.getmembers(model, inspect.isclass),
                      columns=['name', 'class'])
    tables['name'] = tables['name'].str.lower()
    tables = tables.set_index('name').squeeze()
    for i in Path(SOURCE_PATH).glob('*.xlsx'):
        df = pd.read_excel(i)
        name = (i.name)[:-5].replace('_','')
        name = name[:-1] if name[-1]=='s' else name
        msql.insert(df, tables[name])

def insert_statistic_accumulation(set_id):
    msql.truncate_table(model.StatisticsAccumulation)
    conf_df = msql.read_statistics_configuration('statistic_accumulation')
    acc_df = accumulate(set_id, conf_df)
    acc_df['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    acc_df['set_id'] = set_id
    msql.insert(acc_df, model.StatisticsAccumulation, ['set_id','turbine_id'])    


def insert_statistic_sample(set_id):
    msql.truncate_table(model.StatisticsSample)
    date_range = get_day_range(set_id)
    para = msql.read_statistics_parameter('statistic_sample')['parameter'].squeeze()
    para = eval(para)
    if len(date_range)<1:
        return
    # 按天循环计算统计值并插入到表
    conf_df = msql.read_statistics_configuration('statistic_sample')
    conf_df['var_name'] = conf_df['var_name'].str.lower()
    columns = pd.Series(['ts','device'] + conf_df['var_name'].tolist())
    columns = columns[columns!='-'].drop_duplicates()
    for start in date_range:
        print(start)
        end = start + pd.Timedelta('1d')
        sql = f'''
            select {','.join(columns)} from s_{set_id}
            where ts>="{start}" and ts<"{end}"
        '''
        with td.TAOS_Connector(cfg.LOCAL_DRIVER) as scada:
            df = scada.query(sql)
        if df.shape[0]>100:
            stat_df = statistics_of_sample(df, conf_df, para['window_length'])
            stat_df['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                    time.localtime())
            if stat_df.isna().any().any():
                print('包含nan值。跳过。')
                continue
            stat_df['set_id'] = set_id
            msql.insert(stat_df, model.StatisticsSample)
                
def insert_model_anormaly(set_id):
    msql.truncate_table(model.ModelAnormaly)
    df = msql.read_statistics_sample(set_id=set_id, limit=100)
    df.rename(columns={'id':'sample_id'}, inplace=True)
    df['model_id'] = 1
    df['set_id'] = set_id
    df['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    cols = ['set_id', 'model_id', 'sample_id', 'turbine_id', 'create_time']
    msql.insert(df[cols], model.ModelAnormaly)

def restore_scada_data(database, set_id, turbine_id, src_path, dest_path=None):
    ''' 从csv文件导入数据到tdengine '''
    kwargs = cfg.SOURCE_DRIVER.copy()
    kwargs['database'] = None
    sql = td.statement_creat_database(database=database)
    print('create databases', td.execute(sql,kwargs ))  
    
    sql_dct = {'create_super_table':
               td.statement_creat_super_table(set_id=set_id, database=database)}
    sql_dct.update({i.split(' ')[-1]:i for i in 
                    td.statement_creat_sub_table(set_id=set_id, database=database)})
    for i in sql_dct:
        print(i, td.execute(sql_dct[i], cfg.SOURCE_DRIVER))
        
    sql_lst = td.statement_insert_from_csv(
        src_path=src_path, 
        database=database, 
        set_id=set_id, 
        turbine_id=turbine_id)
    if dest_path is not None:
        sql_lst = [i.replace(src_path, dest_path) for i in sql_lst]
    print(''.join(sql_lst))

# =============================================================================
# main
# =============================================================================
if __name__ == '__main__':
    # 创建数据库
    # msql.drop_database()
    # msql.create_database()
    # msql.create_table()
    # insert_demo_data()
    df = msql.read_windfarm_configuration()
    for set_id in df['set_id'].unique():
        insert_statistic_accumulation(set_id)
        insert_statistic_sample(set_id)
        insert_model_anormaly(set_id)
