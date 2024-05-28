# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
from wtbonline._report.common import LOGGER, DEVICE_DF
from wtbonline._report.base import Base
from wtbonline._plot.classes.yawerror import YawError

#%% constant

#%% class
class YawErrorAnalysis(Base):
    '''
    >>> obj = Base(successors=[YawErrorAnalysis()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '偏航误差分析'
        heading = f'{index} {title}'
        conclusion = ''
        tbl_df = {}
        graphs = {}
        LOGGER.info(heading)
        
        ye = YawError()
        i = 0
        for j in range(len(DEVICE_DF['device_id'])):
            device_id = DEVICE_DF['device_id'].iloc[j]
            try:
                fig = ye.plot(set_id='20080', device_ids=device_id, start_time=start_date, end_time=end_date)
            except ValueError:
                continue
            graphs.update({f'图{index}.{i+1} {DEVICE_DF["device_name"].loc[device_id]}':fig})
            i += 1

        conclusion = '无足够数据进行分析。' if len(graphs)<1 else '不同机组在各风速区间偏航误差如下所示，请结合实际修正误差。'
        return self._compose(index, heading, conclusion, tbl_df, graphs, temp_dir, height=1000)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()