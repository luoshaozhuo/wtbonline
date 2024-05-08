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

from wtbonline._report.common import FRAME_WIDTH_LATER, Paragraph, Spacer, LOGGER, PS_BODY, PS_HEADINGS, standard, build_graph, build_tables
from wtbonline._common.utils import make_sure_datetime
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._common.utils import send_email
from wtbonline._logging import log_it
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot.classes.power_compare import PowerCompare

#%% constant
DEVICE_DF = PGFacade.read_model_device().set_index('device_id')

#%% class
class EnergyDifference(Base):
    '''
    >>> obj = Base(successors=[EnergyDifference()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '发电量差异'
        heading = f'{index} {title}'
        conclusion = ''
        tbl_df = None
        graphs = {}
        LOGGER.info(heading)
        
        # 原始数据
        df = TDFC.read(
            set_id=set_id, 
            device_id=None, 
            start_time=start_date, 
            end_time=end_date,
            groupby='device', 
            columns={'totalenergy':['first', 'last']},
            remote=True)
        df['发电量（kWh）'] = df['totalenergy_last'] - df['totalenergy_first']
        df['10%/90%分位数'] = 0
        top_10 = df[df['发电量（kWh）']>df['发电量（kWh）'].quantile(0.9)]
        top_10['10%/90%分位数'] = df['发电量（kWh）'].quantile(0.9)
        last_10 = df[df['发电量（kWh）']<df['发电量（kWh）'].quantile(0.1)]
        last_10['10%/90%分位数'] = df['发电量（kWh）'].quantile(0.1)
        tbl_df = pd.concat([top_10, last_10], ignore_index=True)

        fault_df = []
        for i in tbl_df['device_id'].unique():
            temp = PGFacade.read_data_fault(device_id=i, start_time=start_date, end_time=end_date)
            if len(temp)>0:
                fault_df.append(temp)
        fault_df = pd.concat(fault_df)
        fault_df['duration'] = (fault_df['end_tm']-fault_df['begin_tm']).apply(lambda x:x.total_seconds())/3600
        fault_df = fault_df.groupby('device_id').agg({'duration':'sum', 'begin_tm':pd.Series.count}).reset_index()
        fault_df['duration'] = fault_df['duration'].round(1)
        fault_df.columns = ['device_id', '故障持续时间(小时)', '故障次数']

        # 表格
        tbl_df = pd.merge(tbl_df, fault_df, how='left').fillna(0)
        tbl_df['故障次数'] = tbl_df['故障次数'].astype(int)
        tbl_df = standard(set_id, tbl_df)
        
        # 图形
        pc = PowerCompare()
        graphs = {}
        for i in range(len(tbl_df['device_id'])):
            device_id = tbl_df['device_id'].iloc[i]
            title = f'图 {index}.{i+1} {DEVICE_DF["device_name"].loc[device_id]}'
            graphs.update({title:pc.plot(set_id, device_id, start_date, end_date)}) 

        # 总结
        conclusion = f'{len(top_10)}台机组超过90%分位数，{len(last_10)}台机组低于10%分位数，如下表所示。'  
        
        cols = ['device_name', '发电量（kWh）', '10%/90%分位数', '故障次数', '故障持续时间(小时)']
        return self._compose(index, heading, conclusion, tbl_df[cols], graphs, temp_dir)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()