# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
from typing import Union
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from plotly.subplots import make_subplots
from pygments import highlight

from wtbonline._report.common import FRAME_WIDTH_LATER, Paragraph, Spacer, LOGGER, PS_BODY, PS_HEADINGS, standard, build_graph, DEVICE_DF, FAULT_TYPE_DF, FARMCONF_DF, build_tables, build_table_from_sketch, POINT_DF
from wtbonline._common.utils import make_sure_datetime, make_sure_dataframe, make_sure_list
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._common.utils import send_email
from wtbonline._logging import log_it
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot.classes.powercurve import PowerCurve as PCurve
from wtbonline._plot import graph_factory

#%% constant

#%% class
class Outlier(Base):
    '''
    >>> obj = Base(successors=[Outlier(om_id=1)])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2024-03-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    def __init__(self, successors=[], title='', om_id:str=None):
        assert om_id is not None, '必须指定turbine_outlier_monitor的记录id'
        self.om_id = om_id
        super().__init__(successors, title)
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        sr = RSDBFacade.read_turbine_outlier_monitor(id_=self.om_id).squeeze()
        if len(sr)==0:
            raise ValueError(f'turbine_outlier_monitor 无id={self.om_id}的记录')
        title = f'{sr["system"]}关键参数异常值'
        heading = f'{index} {title}'
        conclusion = ''
        df = None
        graphs = {}
        LOGGER.info(heading)
        
        # 分析涉及的变量
        var_names = pd.Series(pd.Series(sr.var_names.split(',')).unique())
        var_names = var_names[var_names.isin(TDFC.get_filed(set_id, remote=True))]
        if len(var_names)==0:
            raise ValueError(f'tdengine里没有以下字段:{var_names}')
        # plot_var_names = sr['plot_var_names'].split(',') if sr['plot_var_names'] is not None else []
        # plot_var_names = pd.Series(plot_var_names.unique()) if len(plot_var_names)>0 else var_names
        
        # 表格数据
        select_stmt = [
            (
                f'(3*PERCENTILE({i}, 75) - PERCENTILE({i}, 25)) as {i}_3iqr, '
                f'avg({i}) as {i}_mean,'
                f'max({i}) as {i}_max,'
                f'min({i}) as {i}_min'
                )
            for i in sr.var_names.split(',')
            ]
        df = []
        for device_id in DEVICE_DF['device_id']:
            sql = (
                f'select {",".join(select_stmt)} from scada.d_{device_id} '
                f'where ts>"{pd.to_datetime(start_date)}" and ts<"{pd.to_datetime(end_date)}"'
                )
            temp = TDFC.query(sql, remote=True)
            if len(temp)>0:
                temp.insert(0, 'device_id', device_id)
                df.append(temp)
        df = pd.concat(df, ignore_index=True)
        df = standard(set_id, df).drop(columns='device_id').set_index('device_name', drop=True)
        df.columns = pd.MultiIndex.from_product([var_names, ['3iqr', 'mean', 'max', 'min']])
        df = df.reset_index()
        
        # 生成表格
        point_names = POINT_DF[POINT_DF['set_id']==set_id].set_index('var_name')['point_name']
        columns = ['机组编号', '3倍四分位距', '均值', '最大值', '最小值']
        for i in range(len(var_names)):
            var = var_names[i]
            sub_df = df.loc[:, var].copy().reset_index(drop=True)
            upper_bound = sub_df['mean'] + sub_df['max']
            lower_bound = sub_df['min'] - sub_df['mean']
            highlight_rows = sub_df[(sub_df['max']>upper_bound) | (sub_df['min']<lower_bound)].index 
            sub_df.insert(0, 'device_name', df['device_name'])
            sub_df.columns = columns
            rs = build_table_from_sketch(sub_df, f'{index}.{i+1} {point_names[var]}离群值识别结果', highlight_rows=highlight_rows)
            if len(rs)>0:
                graphs.update(rs)
        
        # 绘图
        n = len(var_names)  
        colors = px.colors.qualitative.Dark2
        point_sub = POINT_DF[POINT_DF['set_id']==set_id].set_index('var_name')
        k=1
        for device_id in DEVICE_DF['device_id']:
            plot_df = TDFC.read(
                set_id=set_id, 
                device_id=device_id, /
                start_time=start_date, 
                end_time=end_date, 
                columns={i:['max', 'min'] for i in var_names}, 
                interval='10m',
                remote=True
                )
            if len(plot_df)<1:
                continue
            device_name = DEVICE_DF.loc[device_id, 'device_name']
            fig = make_subplots(int(n/3)+1, 3)
            for i in range(n):
                var = var_names[i]
                point_name = '_'.join(point_sub.loc[var, ['point_name', 'unit']])
                sub_df = df[df['device_name']==device_name].loc[:, var]
                upper_bound = (sub_df['mean'] + sub_df['max']).iloc[0]
                lower_bound = (sub_df['min'] - sub_df['mean']).iloc[0]
                row=int(i/3)+1
                col=i%3+1
                for suffix,color in [('max', colors[2]), ('min', colors[5])]:
                    fig.add_trace(
                        go.Scatter(
                            x=plot_df['ts'], 
                            y=plot_df[f'{var}_{suffix}'],
                            mode='lines+markers',           
                            marker={'opacity':0.5, 'size':2, 'color':color},
                            line={'color':color},
                            name=suffix,
                            showlegend=False
                            ),
                        row=row,
                        col=col
                        )
                    fig.update_yaxes(title_text=point_name, row=row, col=col)
                for y,text in [(upper_bound,'上限'),(lower_bound, '下限')]:
                    fig.add_hline(
                        y=y, 
                        annotation_text=text,
                        annotation_font_size=10, 
                        line_width=1, 
                        line_dash="dash", 
                        line_color="red",
                        row=row,
                        col=col
                        ) 
            fig.update_xaxes(title_text='时间', row=1, col=1)
            fig.update_layout(
                showlegend=False,
                width=1000, 
                height=200*(int(n/3)+1),
                margin=dict(l=20, r=20, t=20 if title in ('', None) else 70, b=20)
                )
            graphs.update({f'图 {index}.{k} {device_name}各关键变量最小最大值时序':fig})
            k += 1
            
        # 总结
        conclusion = f'以每一台机组的{sr.system}的关键参数的3倍四位位距为边界，识别离群数据，结果如下表所示。'
        return self._compose(index, heading, conclusion, graphs=graphs, temp_dir=temp_dir) 
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()