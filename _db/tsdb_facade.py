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
import pandas as pd
from typing import List, Optional, Union, Any, Mapping
import uuid
from pathlib import Path

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.common import make_sure_list, make_sure_datetime
from wtbonline._db.common import make_sure_dataframe, make_sure_dict
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
    def _conver_dtype(self,
                      df:pd.DataFrame, 
                      point_df:pd.DataFrame)->pd.DataFrame:
        ''' 根据model_point表，将tsdb中读取到的数据字段转为指定类型 
        >>> df = pd.DataFrame({'var_000_max':[1,2], 'var_123_max':[1,2], 'var_456':[3,4], 'var_789':[1, 0], 'ts':['2020-02-02','2020-02-03']})
        >>> point_df = pd.DataFrame({
        ...     'var_name':['var_123', 'var_456', 'var_789'], 
        ...     'datatype':['F','I', 'B'], 
        ...     })
        >>> TDFC._conver_dtype(df, point_df).dtypes
        var_000_max                            int64
        var_123_max                          float32
        var_456                             category
        var_789                                 bool
        ts             datetime64[ns, Asia/Shanghai]
        dtype: object
        '''
        if df.shape[0]==0:
            return df
        # null数据会导致类型转换报错
        df.dropna(how='any', inplace=True)
        # 类型转换
        for i in DATA_TYPE:
            cols = point_df[point_df['datatype']==i]['var_name']
            cols = cols[cols.isin(df.columns)]
            # 从tdengine读取Int数据，偶尔会出现float值，先强制做一次int转换
            if DATA_TYPE[i]=='category':
                df[cols] = df[cols].astype(int)
            df[cols] = df[cols].astype(DATA_TYPE[i])
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
            try:
                df['ts'] = df['ts'].dt.tz_convert(tz='Asia/Shanghai')
            except:
                df['ts'] = df['ts'].dt.tz_localize(tz='Asia/Shanghai')
        return df

    def _normalize(self, sql):
        return pd.Series(sql).str.replace('\n +', ' ', regex=True).str.strip().squeeze()

    def _statement_creat_database(self, dbname:str):
        ''' 在本地tdengine建立数据库 
        >>> stm = TDFC._statement_creat_database('test')
        '''
        sql = f'''
                CREATE DATABASE IF NOT EXISTS {dbname} REPLICA 1 DURATION 10 KEEP 36500
                BUFFER 96 MINROWS 100 MAXROWS 4096 WAL_FSYNC_PERIOD 3000 CACHEMODEL
                'last_row' COMP 2 PRECISION 'ms';
              '''
        return self._normalize(sql) 

    def _statement_creat_super_table(self, database:str, set_id:str):
        ''' 创建超级表语句 
        >>> stm = TDFC._statement_creat_super_table('test', '10050')
        '''
        point_df = RSDBInterface.read_turbine_model_point(set_id=set_id, select=1)
        point_df['datatype'].replace({'F':'Float', 'I':'INT', 'B':'BOOL'}, inplace=True)
        columns = point_df['var_name']+' '+point_df['datatype']

        sql = f'''
                CREATE STABLE IF NOT EXISTS {database}.s_{set_id}
                (ts TIMESTAMP, {','.join(columns)})
                TAGS (device NCHAR(20));
             '''
        return self._normalize(sql)

    def _statement_creat_sub_table(self, database, set_id):
        ''' 创建子表语句 
        >>> stm = TDFC._statement_creat_sub_table('test', '10050')
        '''
        turbine_ids = RSDBInterface.read_windfarm_configuration(set_id=set_id, columns='turbine_id')
        sql_lst=[]
        for tid in turbine_ids.squeeze():
            temp = (f'''
                    CREATE TABLE IF NOT EXISTS {database}.d_{tid}
                    USING {database}.s_{set_id} TAGS ("{tid}");
                    ''')
            sql_lst.append(self._normalize(temp))
        return sql_lst

    def init_database(self, dbname:Optional[str]=None, set_id:Optional[str]=None):
        ''' 创建数据库及超级表,默认情况下根据config文件配置库、超级表、子表
        >>> set_id = RSDBInterface.read_windfarm_infomation()['set_id'].iloc[0]
        >>> TDFC.init_database('test', set_id)
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
        set_ids = (RSDBInterface.read_windfarm_configuration(columns='set_id').squeeze().unique()
                   if set_id ==None 
                   else make_sure_list(set_id)) 
        
        conn = TDEngine_Connector(**kwargs)
        conn.query(self._statement_creat_database(dbname)) 
        for i in set_ids:
            conn.query(self._statement_creat_super_table(dbname, i))
            for j in self._statement_creat_sub_table(dbname, i):
                conn.query(j)

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
        return df

    def _select_variable(
            self,
            *,
            set_id:str,
            point_name:Optional[List[str]]=None,
            var_name:Optional[List[str]]=None,
            groupby:Optional[List[str]]=None,
            func_dct:Optional[Mapping[str,List[str]]]=None,
            remote:bool=False,
            ):
        # 不指定point_name或var_name或func_dct，返回全部字段，次数point_df与df可能不匹配
        '''
        >>> set_id = RSDBInterface.read_windfarm_infomation()['set_id'].iloc[0]
        >>> var_name = ['var_355', 'var_101']
        >>> point_name = ['机组总体故障状态', '远方就地控制开关']
        >>> groupby = ['var_101']
        >>> func_dct = {'var_28000':['max', 'min'], 'var_28001':['mean']}
        >>> TDFC._select_variable(set_id=set_id, var_name=var_name, point_name=point_name)
        Traceback (most recent call last):
            ...
        AssertionError: 不能同时给定var_name及point_name
        >>> TDFC._select_variable(set_id=set_id, groupby=groupby)
        Traceback (most recent call last):
            ...
        AssertionError: 给定groupby后，需要指定func_dct
        >>> TDFC._select_variable(set_id=set_id, var_name=var_name, groupby=groupby)
        Traceback (most recent call last):
            ...
        AssertionError: 不能同时指定groupby，及var_name或point_name
        >>> TDFC._select_variable(set_id=set_id, var_name=var_name, func_dct=func_dct)
        Traceback (most recent call last):
            ...
        AssertionError: 不能同时指定func_dct，及var_name或point_name
        >>> cols, point_df = TDFC._select_variable(set_id=set_id, var_name=var_name)
        >>> cols == ['var_355', 'var_101', 'ts', 'device']
        True
        >>> point_df['var_name'].to_list() == ['var_355', 'var_101']
        True
        >>> cols, point_df = TDFC._select_variable(set_id=set_id, func_dct=func_dct, remote=1)
        >>> cols == ['max(var_28000) as var_28000_max','min(var_28000) as var_28000_min','mean(var_28001) as var_28001_mean']
        True
        >>> func_dct = {'var_355':['mean']}
        >>> cols, point_df = TDFC._select_variable(set_id=set_id, func_dct=func_dct, groupby=groupby)
        >>> cols==['mean(var_355) as var_355_mean', 'var_101', 'ts']
        True
        >>> point_df['var_name'].to_list() == ['var_355']
        True
        >>> cols, point_df = TDFC._select_variable(set_id=set_id, func_dct=func_dct)
        >>> cols==['mean(var_355) as var_355_mean', 'ts']
        True
        '''
        func_dct = make_sure_dict(func_dct) 
        var_name = make_sure_list(var_name)
        point_name = make_sure_list(point_name)
        groupby = make_sure_list(groupby)
        if (len(var_name)>0 or len(point_name)>0):
            assert len(groupby)==0, '不能同时指定groupby，及var_name或point_name'
            assert len(func_dct)==0, '不能同时指定func_dct，及var_name或point_name'
        assert not (len(var_name)>0 and len(point_name)>0), '不能同时给定var_name及point_name'
        assert len(func_dct)>0 if len(groupby)>0 else True, '给定groupby后，需要指定func_dct'
        if len(func_dct)>0:
            assert 'ts' not in groupby, '给定func_dct后，ts不能出现在groupby'

        select = None if remote==True else 1
        point_df = RSDBInterface.read_turbine_model_point(set_id=set_id, select=select)
        point_df['var_name'] = point_df['var_name'].str.lower()
        point_df['ref_name'] = point_df['ref_name'].str.lower()

        var_name = [key_ for key_ in func_dct.keys()] if len(func_dct)>0 else var_name
        assert pd.Series(point_name).isin(point_df['point_name']).all() if len(point_name)>0 else True
        point_df = point_df.query('var_name in @var_name') if len(var_name)>0 else point_df
        point_df = point_df.query('point_name in @point_name') if len(point_name)>0 else point_df

        if len(func_dct)>0:
            cols = []
            for key_ in func_dct:
                # 旧版本别名用双引号""，新版本用``
                if remote==True:
                    cols += [f'{f}({key_}) as "{key_}_{f}"' for f in func_dct[key_]]
                else:
                    cols += [f'{f}({key_}) as `{key_}_{f}`' for f in func_dct[key_]]
            if len(cols)==1:
                cols += ['ts']
            # 2.x版本默认加入了group字段
            if len(groupby)>0 and remote==False:
                cols += groupby
        elif len(var_name) or len(point_name)>0:
            cols = point_df['var_name'].to_list()
            cols += ['ts', 'device']
        else:
            cols = ['*']

        cols = pd.Series(cols).str.lower()
        cols_org = cols.tolist()
        cols_org += [] if len(groupby)==0 else groupby

        if remote==True:
            cols.replace({row['var_name']:row['ref_name'] for _,row in point_df.iterrows()}, inplace=True)
        cols_org = pd.Series(cols_org).str.replace('(.*as |"|`)', '',  regex=True)
        return cols.tolist(), cols_org.tolist(), point_df

    def read(
            self,
            *,
            set_id:str,
            turbine_id:str, 
            start_time:Union[str, pd.Timestamp]=None, 
            end_time:Union[str, pd.Timestamp]=None, 
            point_name:Optional[List[str]]=None,
            var_name:Optional[List[str]]=None,
            limit:Optional[int]=None,
            groupby:Optional[List[str]]=None,
            orderby:Optional[List[str]]=None,
            interval:Optional[str]=None,
            sliding:Optional[str]=None,
            func_dct:Optional[Mapping[str,List[str]]]=None,
            remote:bool=False,
            remove_tz:bool=True,
            ):
        ''' 从tsdb读取数据，同时返回相应的字段说明 
        >>> set_id = RSDBInterface.read_windfarm_infomation()['set_id'].iloc[0]
        >>> start_time='2023-01-01'
        >>> end_time='2023-08-01'
        >>> var_name = ['var_355', 'var_101']
        >>> point_name = ['机组总体故障状态', '远方就地控制开关']
        >>> groupby = ['device']
        >>> func_dct = {'var_355':['max', 'min'], 'var_101':['max']}
        >>> turbine_id = 's10001'
        >>> df, point_df =TDFC.read(
        ...     set_id=set_id, turbine_id=turbine_id, start_time=start_time,
        ...     end_time=end_time, var_name=var_name, interval='1m')
        Traceback (most recent call last):
            ...
        AssertionError: 不能同时指定interval及point_name或var_name
        >>> df, point_df =TDFC.read(
        ...     set_id=set_id, turbine_id=turbine_id, start_time=start_time,
        ...     end_time=end_time, groupby=groupby, interval='1m')
        Traceback (most recent call last):
            ...
        AssertionError: 不能同时指定interval及groupby
        >>> df, point_df = TDFC.read(set_id='20835', turbine_id='s1108', 
        ...    start_time='2022-10-01', end_time='2022-05-02', var_name='var_101', remote=True)
        Traceback (most recent call last):
            ...
        ValueError: ('{"status":"error","code":866,"desc":"Table does not exist"}', 'select var_101,ts,device from scada.d_s1108 where ts>="2022-10-01 00:00:00" and ts<"2022-05-02 00:00:00"')
        >>> df, point_df = TDFC.read(set_id='20835', turbine_id='s1108', 
        ...    start_time='2022-10-01', end_time='2022-05-02', var_name='var_101')
        Traceback (most recent call last):
            ...
        ValueError: ('[0x2662]: Fail to get table info, error: Table does not exist', 'select var_101,ts,device from windfarm.d_s1108 where ts>="2022-10-01 00:00:00" and ts<"2022-05-02 00:00:00"')
        >>> df, point_df = TDFC.read(
        ...    set_id=set_id, turbine_id=turbine_id, start_time=start_time, 
        ...    end_time=end_time, var_name=var_name, remote=True, limit=1)
        >>> df.shape[0]==1 and point_df.shape[0]==2
        True
        >>> df, point_df = TDFC.read(
        ...    set_id=set_id, turbine_id=turbine_id, start_time=start_time, 
        ...    end_time=end_time, func_dct=func_dct, remote=True)
        >>> df.columns.tolist()==['var_355_max', 'var_355_min', 'var_101_max'] and point_df['var_name'].tolist()==['var_355', 'var_101']
        True
        >>> df, point_df = TDFC.read(
        ...    set_id=set_id, turbine_id=turbine_id, start_time=start_time, 
        ...    end_time=end_time, remote=True)
        >>> df.shape[1]>500 and point_df.shape[0]>500
        True
        '''
        start_time = pd.to_datetime('2020-01-01 00:00:00') if start_time is None else start_time
        end_time = pd.Timestamp.now() if end_time is None else end_time
        start_time, end_time = make_sure_datetime([start_time, end_time])
        func_dct = make_sure_dict(func_dct)
        groupby = make_sure_list(groupby)
        # 不可用组合
        if (point_name is not None) or (var_name is not None):
            assert interval is None, '不能同时指定interval及point_name或var_name'
        assert len(groupby)==0  if interval is not None else True, '不能同时指定interval及groupby'
        assert interval is None if len(groupby)>0 else True, '不能同时指定interval及groupby'
        # 选定查询变量
        cols, cols_org, point_df = self._select_variable(
            set_id = set_id,
            point_name = point_name,
            var_name = var_name,
            groupby = groupby,
            func_dct = func_dct,
            remote = remote,
            )
        # 查询
        ## 查询列过多
        limit = 10 if point_df.shape[0]>100 and limit==None else limit
        ## 防止忘记限制查询行数
        limit = 1000000 if limit is None else limit
        dbname =get_td_remote_restapi()['database'] if remote==True else get_td_local_connector()['database']
        tbname = f's_{set_id}' if turbine_id is None else f'd_{turbine_id}'
        sql = f'''
            select {','.join(cols)} from {dbname}.{tbname}
            where
            ts>="{start_time}" and
            ts<"{end_time}"
            '''
        if len(func_dct)>0:
            sql = (sql+' group by '+','.join(groupby)) if len(groupby)>0 else sql
        sql = (sql+f' INTERVAL({interval})') if interval is not None else sql
        sql = (sql+f' SLIDING({sliding})') if sliding is not None and interval is not None else sql 
        sql = (sql+f' order by {orderby}') if orderby is not None else sql
        sql = (sql+f' limit {limit}') if limit is not None else sql 
        df = self.query(sql, remote=remote)
        assert isinstance(df, pd.DataFrame), f'\n查询失败:\n{sql},\n 失败信息:\n{df}'
        # 后处理
        if cols==['*']:
            point_df = point_df[point_df['ref_name'].isin(df.columns)]
        elif remote==True:
            df.columns = cols_org
        df = self._conver_dtype(df, point_df)
        point_df['column'] = point_df['point_name'] + '_' + point_df['unit']
        if remove_tz==True and len(df)>0:
            df['ts'] = df['ts'].dt.tz_localize(None)
        return df, point_df
    
    def write(
            self, 
            df:pd.DataFrame, 
            *, 
            set_id:str, 
            turbine_id:str, 
            dbname:Optional[str]=None
            ):
        ''' 将数据写入csv文件再导入数据库 
        >>> import os
        >>> set_id = RSDBInterface.read_windfarm_infomation()['set_id'].iloc[0]
        >>> var_name = RSDBInterface.read_turbine_model_point(set_id=set_id, select=1)['var_name']
        >>> var_name = var_name.str.lower()
        >>> dbname, turbine_id = 'test', 's10001'
        >>> TDFC.init_database(dbname, set_id)
        >>> start_time, end_time = '2023-5-01', '2023-10-02'
        >>> df, point_df = TDFC.read(set_id=set_id, turbine_id=turbine_id, 
        ...     start_time=start_time, end_time=end_time, var_name=var_name, remote=True) 
        >>> TDFC.write(df=df.head(1), set_id=set_id, turbine_id=turbine_id, dbname=dbname)
        >>> _ = TDFC.query(sql='drop database test')
        '''
        df = make_sure_dataframe(df.copy())
        if len(df)<1:
            return
        # 获取字段名称
        temp, _ = TDFC.read(set_id=set_id, turbine_id=turbine_id, start_time=pd.Timestamp.now(),
                         end_time=pd.Timestamp.now()+pd.Timedelta('1d'), limit=1)
        # 只选取数据库中存在的字段名
        df = df[df.columns[df.columns.isin(temp.columns)]]
        df['ts'] = df['ts'].dt.tz_localize(None)
        if 'device' in df.columns:
            df.drop(columns='device', inplace=True)
        columns = df.select_dtypes(['datetimetz', 'datetime', 'datetime64']).columns
        for col in columns:
            df[col] = "'" + df[col].astype(str) + "'"

        # ts字段必须在首位，否则报错
        columns = ['ts'] + df.columns.drop('ts').tolist()
        kwargs = get_td_local_connector()
        if dbname != None:
            kwargs['database'] = dbname
        pathname = Path(get_temp_dir())/f'tmp_{uuid.uuid4().hex}.csv'
        df[columns].to_csv(pathname, index=False)
        sql = f"insert into {kwargs['database']}.d_{turbine_id} file '{pathname.as_posix()}';"
        _ = self.query(sql, driver_kwargs=kwargs)
        pathname.unlink()

TDFC = TDEngine_FACADE()

#%%
if __name__ == "__main__":
    import doctest
    doctest.testmod()