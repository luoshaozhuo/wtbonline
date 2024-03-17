# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

特定项目的数据库访问函数
"""
#%%
# =============================================================================
# import
# =============================================================================
from os import remove
import pandas as pd
from typing import List, Optional, Union, Any, Mapping
import uuid
from pathlib import Path
import numpy as np

from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._common.utils import make_sure_list, make_sure_datetime, make_sure_dataframe, make_sure_dict
from wtbonline._db.tsdb.tdengine import TDEngine_RestAPI, TDEngine_Connector
from wtbonline._db.config import get_temp_dir
from wtbonline._db.config import get_td_local_connector, get_td_remote_restapi

# =============================================================================
# constant
# =============================================================================
DATA_TYPE = {'F':'float32', 'I':'category', 'B':'bool'}

# =============================================================================
# funcion
# =============================================================================
class TDEngine_FACADE():
    def _get_variable_info(self, set_id:str, columns:List[str]):
        '''
        >>> TDFC._get_variable_info(set_id='20835', columns=['var_101','var_101_max','ts'])
                column var_name set_id point_name datatype unit        name
        0      var_101  var_101  20835   1#叶片实际角度        F    °  1#叶片实际角度_°
        1  var_101_max  var_101  20835   1#叶片实际角度        F    °  1#叶片实际角度_°
        '''
        columns = make_sure_list(columns)
        col_df = pd.DataFrame(columns, columns=['column'])
        col_df['var_name'] = pd.Series(['_'.join(i[:2]) for i in pd.Series(columns).str.split('_')])
        point_df = PGFacade.read_model_point(set_id=set_id, var_name=col_df['var_name'])
        rev = pd.merge(col_df, point_df, on='var_name', how='inner')
        return rev
    
    def _conver_dtype(self, set_id:str, df:pd.DataFrame)->pd.DataFrame:
        ''' 根据model_point表，将tsdb中读取到的数据字段转为指定类型 
        >>> df = pd.DataFrame({'var_101_max':[1.0,2.0], 'var_101':[3.0,4.0], 'totalfaultbool':[3,4], 'ts':['2020-02-02','2020-02-03']})
        >>> point_df = pd.DataFrame({
        ...     'var_name':['var_int', 'var_float', 'var_bool'], 
        ...     'datatype':['I','F', 'B'], 
        ...     })
        >>> TDFC._conver_dtype(set_id='20835', df=df).dtypes
        var_101_max                             float32
        var_101                                 float32
        totalfaultbool                             bool
        ts                datetime64[ns, Asia/Shanghai]
        dtype: object
        '''
        if df.shape[0]==0:
            return df
        # null数据会导致类型转换报错
        df.dropna(how='any', inplace=True)
        var_info = self._get_variable_info(set_id=set_id, columns=df.columns)
        # 类型转换
        for _,row in var_info.iterrows():
            # 从tdengine读取Int数据，偶尔会出现float值，先强制做一次int转换
            if row['datatype']=='I':
                df[row['column']] = df[row['column']].astype(int)
            df[row['column']] = df[row['column']].astype(DATA_TYPE[row['datatype']])
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
            try:
                df['ts'] = df['ts'].dt.tz_convert(tz='Asia/Shanghai')
            except:
                df['ts'] = df['ts'].dt.tz_localize(tz='Asia/Shanghai')
        return df

    def _normalize(self, sql):
        return pd.Series(sql).str.replace('\n +', ' ', regex=True).str.strip().squeeze()

    def _statement_create_database(self, dbname:str):
        ''' 在本地tdengine建立数据库 
        >>> TDFC._statement_create_database('test')
        "CREATE DATABASE IF NOT EXISTS test REPLICA 1 DURATION 10 KEEP 36500 BUFFER 96 MINROWS 100 MAXROWS 4096 WAL_FSYNC_PERIOD 3000 CACHEMODEL 'last_row' COMP 2 PRECISION 'ms';"
        '''
        sql = f'''
                CREATE DATABASE IF NOT EXISTS {dbname} REPLICA 1 DURATION 10 KEEP 36500
                BUFFER 96 MINROWS 100 MAXROWS 4096 WAL_FSYNC_PERIOD 3000 CACHEMODEL
                'last_row' COMP 2 PRECISION 'ms';
              '''
        return self._normalize(sql) 

    def _statement_create_super_table(self, database:str, set_id:str):
        ''' 创建超级表语句 
        >>> _ = TDFC._statement_create_super_table('test', '20835')
        '''
        point_sel = RSDBFacade.read_turbine_model_point()
        point_all = PGFacade.read_model_point(set_id=set_id, var_name=point_sel['var_name'])
        point_df = pd.merge(point_sel, point_all[['var_name', 'datatype']], how='inner')
        point_df['datatype'] = point_df['datatype'].replace({'F':'Float', 'I':'INT', 'B':'BOOL'})
        columns = point_df['var_name']+' '+point_df['datatype']
        sql = f'''
                CREATE STABLE IF NOT EXISTS {database}.s_{set_id}
                (ts TIMESTAMP, {','.join(columns)})
                TAGS (device NCHAR(20));
             '''
        return self._normalize(sql)

    def _statement_create_sub_table(self, database, set_id):
        ''' 创建子表语句 
        >>> set_id = PGFacade.read_model_device()['set_id'].unique()[0]
        >>> TDFC._statement_create_sub_table('test', set_id)[0]
        'CREATE TABLE IF NOT EXISTS test.d_s10001 USING test.s_20835 TAGS ("s10001");'
        '''
        device_ids = PGFacade.read_model_device(set_id=set_id)['device_id']
        sql_lst=[]
        for tid in device_ids.squeeze():
            temp = (f'''
                    CREATE TABLE IF NOT EXISTS {database}.d_{tid}
                    USING {database}.s_{set_id} TAGS ("{tid}");
                    ''')
            sql_lst.append(self._normalize(temp))
        return sql_lst

    def query(
            self, 
            sql, 
            *, 
            remote:bool=False, 
            driver_kwargs:Mapping[str, Union[str,int]]=None
            )->pd.DataFrame:
        ''' 通用sql执行函数 '''
        connector = TDEngine_RestAPI if remote==True else TDEngine_Connector
        kwargs = driver_kwargs
        if kwargs==None:
            kwargs = get_td_remote_restapi() if remote==True else get_td_local_connector()
        df = connector(**kwargs).query(sql)
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
        return df

    def init_database(self, dbname:Optional[str]=None, set_id:Optional[str]=None):
        ''' 创建数据库及超级表,默认情况下根据config文件配置库、超级表、子表
        >>> TDFC.init_database(dbname='test')        
        >>> dbs = TDFC.query('show databases').squeeze()
        >>> (dbs=='test').any()
        True
        >>> _ = TDFC.query(sql='drop database test')
        >>> dbs = TDFC.query('show databases').squeeze()
        >>> (dbs=='test').any()
        False
        '''
        kwargs = get_td_local_connector()
        dbname = kwargs['database'] if dbname==None else dbname
        kwargs['database'] = None
        set_ids = ( PGFacade.read_model_device()['set_id'].unique()
                   if set_id ==None 
                   else make_sure_list(set_id)) 
        
        conn = TDEngine_Connector(**kwargs)
        conn.query(self._statement_create_database(dbname)) 
        for i in set_ids:
            conn.query(self._statement_create_super_table(dbname, i))
            for j in self._statement_create_sub_table(dbname, i):
                conn.query(j)

    def _variable(
            self,
            *,
            columns:Union[str, List[str], Mapping[str,List[str]]]=None,
            groupby:Optional[List[str]]=None,
            interval:Optional[str]=None,
            sample:int=-1,
            remote:bool=False,
            ):
        # 不指定point_name或var_name或func_dct，返回全部字段，次数point_df与df可能不匹配
        '''
        >>> var_name = 'var_355'
        >>> groupby = ['var_101']
        >>> func_dct = {'var_28000':['max', 'min'], 'var_28001':['mean']}
        >>> TDFC._variable(columns=var_name)
        ['ts', 'var_355']
        >>> TDFC._variable(columns=var_name, interval='2s', remote=True)
        ['var_355']
        >>> TDFC._variable(columns=func_dct, groupby=groupby)
        ['max(var_28000) as `var_28000_max`', 'min(var_28000) as `var_28000_min`', 'mean(var_28001) as `var_28001_mean`', 'var_101']
        >>> TDFC._variable(columns=func_dct, groupby=groupby, remote=True)
        ['max(var_28000) as "var_28000_max"', 'min(var_28000) as "var_28000_min"', 'mean(var_28001) as "var_28001_mean"']
        '''
        groupby = make_sure_list(groupby)
        assert isinstance(columns, dict) if len(groupby)>0 else True, '给定groupby后，需要指定聚合函数'
        version = int(RSDBFacade.read_app_server(name='tdengine', remote=remote)['version'].loc[0].split('.')[0])
        if columns is None:
            rev = ['*']
        if isinstance(columns, (list, tuple, str, pd.Series, set)):
            if isinstance(columns, str):
                columns = [columns]
            columns = list(columns)
            rev = list(set(columns) - set(['ts', 'device']))
            if version<3:
                rev = ['ts'] + rev if sample is None else rev
            else:
                rev = ['ts']+rev if sample<1 else [f'sample(ts, {sample}) as ts']+rev
        elif isinstance(columns, dict):
            for key_ in columns:
                columns[key_] = make_sure_list(columns[key_])
            rev = ['_wstart as `ts`'] if version>2 and interval not in (None, '') else []
            for key_ in columns:
                # 旧版本别名用双引号""，新版本用``
                if version<3:
                    rev += [f'{f}({key_}) as "{key_}_{f}"' for f in columns[key_]]
                else:
                    rev += [f'{f}({key_}) as `{key_}_{f}`' for f in columns[key_]]
            # 3.x版本要手动添加group字段
            if len(groupby)>0 and version>2:
                rev += groupby
        else:
            raise ValueError(f'不支持的数据类型{type(columns)}')
        return rev

    def get_statement(
            self,
            *,
            set_id:str,
            device_id:str, 
            start_time:Union[str, pd.Timestamp]=None, 
            end_time:Union[str, pd.Timestamp]=None, 
            columns:Optional[Union[List[str], Mapping[str, List[str]]]]=None,
            limit:Optional[int]=None,
            groupby:Optional[List[str]]=None,
            orderby:Optional[List[str]]=None,
            interval:Optional[str]=None,
            sliding:Optional[str]=None,
            remote:bool=False,
            sample:int=-1,
            ):
        # 选定查询变量
        variables = self._variable(columns=columns, groupby=groupby, sample=sample, remote=remote)
        # 查询
        ## 防止查询列过多
        limit = 10 if len(variables)>100 and limit==None else limit
        ## 防止忘记限制查询行数
        limit = 1_000_000 if limit is None else limit
        dbname =get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
        tbname = f's_{set_id}' if device_id is None else f'd_{device_id}'
        sql = f'''
            select {', '.join(variables)} from {dbname}.{tbname}
            where
            ts>"{start_time}" and
            ts<="{end_time}"
            '''
        sql = (sql+' group by '+','.join(groupby)) if len(groupby)>0 else sql
        sql = (sql+f' INTERVAL({interval})') if interval is not None else sql
        sql = (sql+f' SLIDING({sliding})') if sliding is not None and interval is not None else sql 
        sql = (sql+f' order by {orderby}') if len(orderby)>0 else sql
        sql = (sql+f' limit {limit}') if limit is not None else sql 
        sql = pd.Series(sql).str.replace('\n *', ' ', regex=True).squeeze().strip()
        return sql

    def get_interval(self, start_time, end_time, sample, samplling_rate=1):
        '''
        >>> TDFC.get_interval('2023-05-01', '2023-05-01 03:00:00', 100)
        '108s'
        '''
        start_time = make_sure_datetime(start_time)
        end_time = make_sure_datetime(end_time)
        k = 1.0*(end_time - start_time).total_seconds()*samplling_rate/sample
        interval = None if k<1.5 else f'{int(np.ceil(k))}s'
        return interval

    def read(
            self,
            *,
            set_id:str,
            device_id:str, 
            start_time:Union[str, pd.Timestamp]=None, 
            end_time:Union[str, pd.Timestamp]=None, 
            columns:Optional[Union[List[str], Mapping[str, List[str]]]]=None,
            limit:Optional[int]=None,
            groupby:Optional[List[str]]=None,
            orderby:Optional[List[str]]=None,
            interval:Optional[str]=None,
            sliding:Optional[str]=None,
            remote:bool=False,
            sample:int=-1,
            samplling_rate=1,
            ):
        ''' 从tsdb读取数据，同时返回相应的字段说明 
        >>> device_df = PGFacade.read_model_device()
        >>> set_id = device_df['set_id'].iloc[0]
        >>> device_id = 's10003'
        >>> start_time='2023-01-01'
        >>> end_time='2023-01-02'
        >>> var_name = ['totalfaultbool', 'var_101']
        >>> groupby = ['device']
        >>> func_dct = {'var_355':['max', 'min'], 'var_101':['max']}
        >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=var_name)
        >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=var_name, remote=True)
        >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=func_dct)
        >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=var_name, interval='10s', sample=10)
        >>> TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=func_dct, sample=100, remote=True)
                                   ts  var_355_max  var_355_min  var_101_max
        0   2022-12-31 23:50:24+08:00      4.36121      2.36095     0.000000
        1   2023-01-01 00:04:48+08:00      5.36256      3.02394     0.010000
        2   2023-01-01 00:19:12+08:00      4.79507      3.21097     0.010000
        3   2023-01-01 00:33:36+08:00      4.66829      2.88396     0.010000
        4   2023-01-01 00:48:00+08:00      4.66829      2.95148     0.010000
        ..                        ...          ...          ...          ...
        96  2023-01-01 22:52:48+08:00      2.08171      0.80911    90.019997
        97  2023-01-01 23:07:12+08:00      1.56558      0.80911    90.019997
        98  2023-01-01 23:21:36+08:00      1.86198      0.66148    90.019997
        99  2023-01-01 23:36:00+08:00      1.86198      0.80911    90.019997
        100 2023-01-01 23:50:24+08:00      1.71893      0.96475    90.019997
        <BLANKLINE>
        [101 rows x 4 columns]
        '''
        start_time = pd.to_datetime('2020-01-01 00:00:00') if start_time is None else start_time
        end_time = pd.Timestamp.now() if end_time is None else end_time
        start_time, end_time = make_sure_datetime([start_time, end_time])
        # 不可用组合
        orderby = make_sure_list(orderby)
        groupby = make_sure_list(groupby)
        assert len(groupby)==0  if interval is not None else True, '不能同时指定interval及groupby'
        assert interval is None if len(groupby)>0 else True, '不能同时指定interval及groupby'
        
        if remote==False:
            sql = self.get_statement(
                set_id=set_id,
                device_id=device_id, 
                start_time=start_time, 
                end_time=end_time, 
                columns=columns,
                limit=limit,
                groupby=groupby,
                orderby=orderby,
                interval=interval,
                sliding=sliding,
                remote=remote,
                sample=sample
                )
            df = self.query(sql, remote=remote)
        else:
            df = []
            if sample is not None and sample>0 and interval is None:
                interval = self.get_interval(start_time, end_time, sample, samplling_rate=samplling_rate)
            while True:
                sql = self.get_statement(
                    set_id=set_id,
                    device_id=device_id, 
                    start_time=start_time, 
                    end_time=end_time, 
                    columns=columns,
                    limit=limit,
                    groupby=groupby,
                    orderby=orderby,
                    interval=interval,
                    sliding=sliding,
                    remote=remote,
                    )
                temp = self.query(sql, remote=remote)
                # version2的restapi 限制每次获取记录10240条
                if len(temp)<10240:
                    break
                df.append(temp)
                start_time = temp['ts'].max()
            df = pd.concat(df, ignore_index=True) if len(df)>0 else temp
        if 'ts' in df.columns:
            df = df.drop_duplicates('ts').sort_values('ts')
        df.rename(columns={'device':'device_id'}, inplace=True)
        df = self._conver_dtype(set_id=set_id, df=df)
        return df
    
    def write(
            self, 
            df:pd.DataFrame, 
            *, 
            set_id:str, 
            device_id:str, 
            dbname:Optional[str]=None
            ):
        ''' 将数据写入csv文件再导入数据库 
        >>> import os
        >>> set_id = '20835'
        >>> var_name = RSDBFacade.read_turbine_model_point()['var_name']
        >>> var_name = var_name.str.lower()
        >>> dbname, device_id = 'test', 's10003'
        >>> TDFC.init_database(dbname, set_id)
        >>> start_time, end_time = '2023-5-01', '2023-5-02'
        >>> df = TDFC.read(set_id=set_id, device_id=device_id, start_time=start_time, end_time=end_time, columns=var_name, remote=True, limit=1) 
        >>> TDFC.write(df=df.head(1), set_id=set_id, device_id=device_id, dbname=dbname)
        >>> _ = TDFC.query(sql='drop database test')
        '''
        df = make_sure_dataframe(df.copy())
        if len(df)<1:
            return
        # 获取字段名称
        fields = self.get_filed(set_id=set_id, remote=False)
        fieles = fields[fields!='device']
        df = df[fieles] # 貌似必须字段按顺序写入，且必须包含全部字段
        df['ts'] = df['ts'].dt.tz_localize(None)
        if 'device' in df.columns:
            df.drop(columns='device', inplace=True)
        columns = df.select_dtypes(['datetimetz', 'datetime', 'datetime64']).columns
        for col in columns:
            df[col] = "'" + df[col].dt.strftime('%Y-%m-%d %H:%M:%S') + "'"

        # 数据类型转换
        # bool转换为int，否则报错
        # 对于tdengine而言，1为true，0为false
        point_df = PGFacade.read_model_point(set_id=set_id)
        for datatype, type_ in [['B', 'int8'], ['I', 'int32']]:
            cols = point_df[point_df['datatype']==datatype]['var_name']
            cols = df.columns[df.columns.isin(cols)]
            for col in cols:
                df[col] = df[col].astype(type_)
     
        kwargs = get_td_local_connector()
        if dbname != None:
            kwargs['database'] = dbname
        pathname = Path(get_temp_dir())/f'tmp_{uuid.uuid4().hex}.csv'
        df.to_csv(pathname, index=False)
        sql = f"insert into {kwargs['database']}.d_{device_id} file '{pathname.as_posix()}';"
        _ = self.query(sql, driver_kwargs=kwargs)
        pathname.unlink()

    def get_filed(self, set_id, remote=False):
        '''
        >>> _ = TDFC.get_filed(set_id='20835')
        >>> _ = TDFC.get_filed(set_id='20835', remote=True)
        '''
        sql = f'describe s_{set_id}'
        rev = self.query(sql, remote=remote)
        rev.columns = rev.columns.str.lower()
        return rev['field']
    
    def get_deviceID(self, set_id, remote=False):
        '''
        >>> _ = TDFC.get_deviceID(set_id='20835')
        >>> _ = TDFC.get_deviceID(set_id='20835', remote=True)
        '''
        version = int(RSDBFacade.read_app_server(name='tdengine', remote=remote)['version'].loc[0].split('.')[0])
        if version>2:
            sql = f'SHOW TABLE TAGS FROM s_{set_id}'
            rev = self.query(sql, remote=remote)['device'].tolist()
        else:
            sql = f'show tables'
            rev = self.query(sql, remote=remote)
            rev = rev[rev['stable_name']==f's_{set_id}']['table_name'].tolist()
        return rev

TDFC = TDEngine_FACADE()

# %%
if __name__ == "__main__":
    import doctest
    doctest.testmod()