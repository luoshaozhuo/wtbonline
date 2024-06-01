# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import pandas as pd

from wtbonline._report.common import LOGGER
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC

#%% class
class Profile(Base):
    '''
    >>> obj = Base(successors=[Profile()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '概况'
        heading = f'{index} {title}'
        conclusion = ''
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        df = TDFC.read(
            set_id=set_id, 
            device_id=None, 
            start_time=start_date,
            end_time=end_date, 
            columns={'ts':['first', 'last']}, 
            remote=True)
        if len(df)<1:
            raise ValueError(f'无法出具报告，规定时段没有数据：{start_date}至{end_date}')
        sr = df.squeeze()
        
        min_date = pd.to_datetime(sr['ts_first']).date()
        max_date = pd.to_datetime(sr['ts_last']).date()
        farm_df = self.PGFC.read_model_device(set_id=set_id)
        n = len(TDFC.get_deviceID(set_id=set_id, remote=True))
        conclusion = f'''机组型号：{set_id}<br/>
            机组总数：{farm_df.shape[0]} 台<br/>
            可统计机组：{n} 台<br/>
            统计开始时间：{start_date}<br/>
            统计结束时间：{end_date}<br/>
            可统计开始时间：{min_date}<br/>
            可统计结束时间：{max_date}<br/>
            '''

        return self._compose(index, heading, conclusion, tables, graphs, temp_dir)
    
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()