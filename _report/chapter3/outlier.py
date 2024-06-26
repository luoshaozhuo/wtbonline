# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
from wtbonline._report.common import LOGGER, DEVICE_DF
from wtbonline._report.base import Base
from wtbonline._plot import graph_factory

#%% constant

#%% class
class Outlier(Base):
    '''
    >>> obj = Base(successors=[Outlier()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '离群识别'
        heading = f'{index} {title}'
        conclusion = ''
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        anormaly_df = self.RSDBFC.read_model_anormaly(
            set_id=set_id, start_time=start_date, end_time=end_date
            ).drop_duplicates('sample_id')
        if len(anormaly_df)<1:
            conclusion = '通过对转矩、转速、叶片角度、偏航误差、机组振动等进行分析，本期报告时段内无离群值识别记录。'
            return self._compose(index, heading, conclusion, tables, graphs, temp_dir) 
        
        label_df = self.RSDBFC.read_model_label(set_id=set_id).drop_duplicates('sample_id')
        total = anormaly_df.shape[0]
        left = total - label_df.shape[0]

        # 取最后一个样本点
        device_ids = anormaly_df['device_id'].sort_values().unique()
        for i in range(len(device_ids)):
            device_id = device_ids[i]
            fig = graph_factory.get('Anomaly')().plot(
                set_id=set_id,
                device_ids=device_id,
                start_time=start_date,
                end_time=end_date,
                )
            graphs.update({f'图{index}.{i+1} {DEVICE_DF["device_name"].loc[device_id]}':fig})
        
        # 总结
        label_df = self.RSDBFC.read_model_label(set_id=set_id).drop_duplicates('sample_id')
        total = anormaly_df.shape[0]
        left = total - label_df.shape[0]
        conclusion = f'通过对转矩、转速、叶片角度、偏航误差、机组振动等进行分析，本期报告时段内共有离群数据：{total}条, 待鉴别{left}条，具体如下所示。'
        return self._compose(index, heading, conclusion, tables, graphs, temp_dir) 
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()