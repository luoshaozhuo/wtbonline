# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import pandas as pd

from wtbonline._report.common import FAULT_TYPE_DF, FARMCONF_DF, plot_stat, plot_sample_ts, standard, LOGGER, plot_ts
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC

#%% constant

#%% class
class Degrading(Base):
    '''
    >>> obj = Base(successors=[Degrading()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20835'
    >>> start_date = '2024-02-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '机组降容分析'
        heading = f'{index} {title}'
        conclusion = ''
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        sub_df = FAULT_TYPE_DF[FAULT_TYPE_DF['name']=='机组降容']
        record_df = self.RSDBFC.read_statistics_fault(
            fault_id=sub_df['id'],
            start_time=start_date,
            end_time=end_date,
            ).sort_values('start_time', ascending=False)
        record_df = standard(set_id, record_df)
        if len(record_df)<1:
            conclusion = '报告期内没有发生机组降容。'
            return self._compose(index, heading, conclusion, tables, graphs, temp_dir)
        ext_df = pd.merge(record_df, sub_df, left_on='fault_id', right_on='id', how='left')
        
        # 表
        tbl_df = ext_df.groupby(['cause', 'device_name'])['device_id'].count().reset_index()
        tbl_df.sort_values(['cause', 'device_id'], inplace=True, ascending=False)
        tbl_df.columns = ['降容原因', '机组名', '发生次数']
        tables.update({f'表 {index}.1 降容原因统计结果':tbl_df})
        
        # 图
        rs = plot_stat(ext_df)
        graphs = {f'图{index}.1 降容发展趋势':rs[0], f'图{index}.2 降容原因占比':rs[1]}

        fields = TDFC.get_filed(set_id=set_id, remote=True)        
        sub_df = ext_df.drop_duplicates(subset=['cause', 'device_name'])
        i = len(graphs)+1
        for _,row in sub_df.iterrows():
            try:
                var_names = pd.Series(row['var_names'].split(','))
                var_names = var_names[var_names.isin(fields)]
                if len(var_names)<1:
                    continue
                df = TDFC.read(set_id=set_id, device_id=row['device_id'], start_time=row['start_time'],
                               end_time=row['end_time'], columns=row['var_names'])
                if len(df)<1:
                    continue
                fig = plot_ts(df, var_names=var_names, set_id=set_id)
                graphs.update({f"图{index}.{i} {row['device_name']}_{row['cause']}":fig})   
            except ValueError:
                continue
            i += 1    

        # 总结
        group = ext_df.groupby('cause')
        stmt = '，'.join([f'{cause}发生{len(grp)}次' for cause,grp in group])
        conclusion = f'报告期内发生降容{len(ext_df)}次。其中{stmt}。'
        return self._compose(index, heading, conclusion, tables, graphs, temp_dir)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()