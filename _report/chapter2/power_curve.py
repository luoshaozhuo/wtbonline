# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import numpy as np

from wtbonline._report.common import LOGGER, standard
from wtbonline._report.base import Base
from wtbonline._plot.classes.powercurve import PowerCurve as PCurve

#%% constant

#%% class
class PowerCurve(Base):
    '''
    >>> obj = Base(successors=[PowerCurve()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '功率曲线'
        heading = f'{index} {title}'
        conclusion = ''
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        df = self.RSDBFC.read_statistics_sample(set_id=set_id, columns={'bin':['count']}, start_time=start_date, end_time=end_date, groupby='device_id')
        df = df[df['bin_count']>100]
        df = standard(set_id, df).sort_values('device_id')
        pc = PCurve()
        graphs = {}
        for i in range(int(np.ceil(len(df)/4))):
            device_ids = df.iloc[i*4:].head(4)['device_id']
            title = f'图 {index}.{i+1}'
            graphs.update({title:pc.plot(set_id, device_ids, start_date, end_date)}) 
        
        return self._compose(index, heading, conclusion, tables, graphs, temp_dir)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()