# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:34:47 2023

@author: luosz
"""

from wtbonline._report.chapter4.anomaly import Anomaly
from wtbonline._report.chapter4.power import Power
from wtbonline._db.rsdb_facade import RSDBFacade

from wtbonline._report.base import Base

df = RSDBFacade.read_turbine_outlier_monitor()
CHAPTER4 = Base(successors=[Power()] + [Anomaly(om_id=id_) for id_ in df['id']], title='关键数据分析')

#%% main
if __name__ == "__main__":
    obj = Base(successors=[CHAPTER4])
    outpath = '/mnt/d/'
    set_id = '20080'
    start_date = '2024-03-01'
    end_date = '2024-04-01'
    pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)