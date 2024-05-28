# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import pandas as pd
import plotly.express as px

from wtbonline._report.common import LOGGER, standard, FAULT_TYPE_DF, FARMCONF_DF
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._report.base import Base


#%% class
class StatisticFault(Base):
    '''
    >>> obj = Base(successors=[StatisticFault()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '故障统计'
        heading = f'{index} {title}'
        conclusion = ''
        tbl_df = {}
        graphs = {}
        LOGGER.info(heading)
        
        # 原始数据
        is_offshore = FARMCONF_DF['is_offshore'].loc[set_id]
        sub_df = FAULT_TYPE_DF[(FAULT_TYPE_DF['is_offshore']==is_offshore) & (FAULT_TYPE_DF['type']=='fault')]
        df = RSDBFacade.read_statistics_fault(
            set_id=set_id,
            fault_id=sub_df['id'],
            start_time=start_date,
            end_time=end_date
            ).sort_values(['start_time'], ascending=False)
        df = pd.merge(df, sub_df, how='left', left_on='fault_id', right_on='id')
        df['date'] = df['start_time'].dt.date
        df = standard(set_id, df)
        if len(df)==0:
            conclusion = '统计时间段内没发生指定故障。'
            return self._compose(index, heading, conclusion, tbl_df, graphs, temp_dir) 
        
        # 表格
        tbl_df = df.groupby(['name', 'device_name']).agg({'device_id':len}).reset_index()
        tbl_df.sort_values(['name', 'device_id'], inplace=True, ascending=False)
        tbl_df.columns = ['故障名称', '设备名称', '故障次数']
        
        # 图形
        plot_df = df.groupby(['date', 'name']).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
        plot_df.columns = ['日期', '故障名称', '发生次数']
        fig = px.bar(plot_df, x="日期", y="发生次数", color="故障名称", width=900, height=500)
        graphs.update({f'图{index}.1 故障发生趋势':fig})
        
        plot_df = df.groupby(['name', 'device_name']).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
        plot_df.columns = ['故障名称', '设备编号', '发生次数']
        fig = px.sunburst(
            plot_df, 
            path=['故障名称', '设备编号'], 
            values='发生次数',
            color='发生次数', 
            color_continuous_scale='RdBu',
            color_continuous_midpoint=plot_df['发生次数'].mean()
            )
        graphs.update({f'图{index}.2 故障占比':fig})
        
        # 总结
        stat_df = df.groupby(['name'])
        descr = '，'.join([f'{name}发生{len(grp)}次' for name,grp in df.groupby('name')])
        conclusion = f'总共发生故障{len(df)}次，其中{descr}。'
        return self._compose(index, heading, conclusion, {f'表 {index}.1 故障统计结果':tbl_df}, graphs, temp_dir) 
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()