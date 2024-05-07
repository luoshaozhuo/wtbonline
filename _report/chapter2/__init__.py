# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:34:47 2023

@author: luosz
"""

from wtbonline._report.chapter2.energy_difference import EnergyDifference
from wtbonline._report.chapter2.energy_rating import EnergyRating
from wtbonline._report.chapter2.power_curve import PowerCurve
from wtbonline._report.chapter2.statistic_fault import StatisticFault
from wtbonline._report.base import Base

CHAPTER2 = Base(successors=[EnergyRating(), EnergyDifference(), PowerCurve(), StatisticFault()], title='设备运行效果分析')

#%% main
if __name__ == "__main__":
    obj = Base(successors=[CHAPTER2])
    outpath = '/mnt/d/'
    set_id = '20080'
    start_date = '2023-10-01'
    end_date = '2024-04-01'
    pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)