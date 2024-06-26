# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:34:47 2023

@author: luosz
"""

from wtbonline._report.chapter1.profile import Profile
from wtbonline._report.base import Base

CHAPTER1 = Profile()

#%% main
if __name__ == "__main__":
    obj = Base(successors=[CHAPTER1])
    outpath = '/mnt/d/'
    set_id = '20080'
    start_date = '2023-10-01'
    end_date = '2024-04-01'
    pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)