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
from pygments import highlight

from wtbonline._report.common import FRAME_WIDTH_LATER, Paragraph, Spacer, LOGGER, PS_BODY, PS_HEADINGS, standard, build_graph, DEVICE_DF, FAULT_TYPE_DF, FARMCONF_DF, build_tables, build_table_from_sketch
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
class Power(Base):
    '''
    >>> obj = Base(successors=[Power()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2024-03-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '有功功率'
        heading = f'{index} {title}'
        conclusion = ''
        df = None
        tbl_df = {}
        graphs = {}
        LOGGER.info(heading)
        
        # 原始数据
        df = []
        pc = PCurve()
        pc.init()
        for i in DEVICE_DF['device_id']:
            try:
                _, power_curve, _ = pc.read_data(set_id, i, start_date, end_date, pc.var_names, width=0.25)
            except ValueError:
                continue
            df.append(power_curve)
        df = pd.concat(df, ignore_index=True)
        df = df[df['wspd'].between(7, 9.5)]
        df['mean_power'] = df['mean_power'].round(1)
        df = df.pivot(index='device_id', columns=['wspd'], values=['mean_power'])
        df = df.reset_index().droplevel(level=0, axis=1)
        df.columns = ['device_id'] + list(df.columns[1:])
        df = standard(set_id, df).drop(['device_id'], axis=1)
        df = df[['device_name'] + list(df.columns[:-1])]
        df = df.rename(columns={'device_name':'机组号'})
        df = df.reset_index(drop=True)
        mean_ = df.iloc[:, 1:].mean()
        iqr_ = df.iloc[:, 1:].quantile(0.75) - df.iloc[:, 1:].quantile(0.25)
        upper_bound = mean_ + 3*iqr_
        lower_bound = mean_ - 3*iqr_
        
        # 表格
        highlight_cells = []
        for i in range(len(df.columns)-1):
            idxs = df[~df.iloc[:, i+1].between(lower_bound.iloc[i], upper_bound.iloc[i])].index
            highlight_cells += [(idx, i+1) for idx in idxs]
        rs = build_table_from_sketch(df, title=f'{index} 不同风速区间有功功率', highlight_cells=highlight_cells)
        graphs.update(rs)
            
        # 总结
        conclusion = f'各风速区间功率如下表所示，其中超出3倍四分位距的值标红显示。'
        return self._compose(index, heading, conclusion, tbl_df, graphs, temp_dir) 
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()