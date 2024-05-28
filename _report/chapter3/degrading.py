# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
from wtbonline._report.common import FAULT_TYPE_DF, FARMCONF_DF, plot_stat, plot_sample_ts, standard, LOGGER
from wtbonline._report.base import Base

#%% constant

#%% class
class Degrading(Base):
    '''
    >>> obj = Base(successors=[Degrading()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '机组降容分析'
        heading = f'{index} {title}'
        conclusion = ''
        tbl_df = None
        graphs = {}
        LOGGER.info(heading)
        
        is_offshore = FARMCONF_DF['is_offshore'].loc[set_id]
        sub_df = FAULT_TYPE_DF[(FAULT_TYPE_DF['is_offshore']==is_offshore) & (FAULT_TYPE_DF['name']=='机组降容')]
        record_df = self.RSDBFC.read_statistics_fault(
            fault_id=sub_df['id'],
            start_time=start_date,
            end_time=end_date,
            ).sort_values('start_time', ascending=False)
        record_df = standard(set_id, record_df)
        if len(record_df)<1:
            conclusion = '报告期内没有发生机组降容。'
            return self._compose(index, heading, conclusion, tbl_df, graphs, temp_dir)
        ext_df = pd.merge(record_df, sub_df, left_on='fault_id', right_on='id', how='left')
        
        # 表
        tbl_df = ext_df.groupby(['cause', 'device_name'])['device_id'].count().reset_index()
        tbl_df.sort_values(['cause', 'device_id'], inplace=True, ascending=False)
        tbl_df.columns = ['降容原因', '机组名', '发生次数']
        
        # 图
        rs = plot_stat(ext_df)
        graphs = {f'图{index}.1 降容发展趋势':rs[0], f'图{index}.2 降容原因占比':rs[1]}
        sub_df = ext_df.drop_duplicates(subset=['cause', 'device_name'])
        i = 3
        for _,row in sub_df.iterrows():
            try:
                rs = plot_sample_ts(row)
                graphs.update({f"图{index}.{i} {row['device_name']}_{row['cause']}":rs[0]})  
            except ValueError:
                continue
            i += 1    

        # 总结
        group = ext_df.groupby('cause')
        stmt = '，'.join([f'{cause}发生{len(grp)}次' for cause,grp in group])
        conclusion = f'报告期内发生降容{len(ext_df)}次。其中{stmt}。'
        return self._compose(index, heading, conclusion, {f'表 {index}.1 降容原因统计结果':tbl_df}, graphs, temp_dir)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()