# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """
#%% import
from typing import Union
from datetime import date
import pandas as pd

from wtbonline._report.common import DEVICE_DF, mail_report, RSDBFacade, REPORT_OUT_DIR
from wtbonline._report.base import Base
from wtbonline._report.chapter1 import CHAPTER1
from wtbonline._report.chapter2 import CHAPTER2
from wtbonline._report.chapter3 import CHAPTER3
from wtbonline._report.chapter4 import CHAPTER4
from wtbonline._report.common import LOGGER
from wtbonline._logging import log_it

def build_brief_report(
        *, 
        outpath:str, 
        set_id:str, 
        start_date:Union[str, date], 
        end_date:Union[str, date]
        ):
    obj = Base(successors=[CHAPTER1, CHAPTER2, CHAPTER3, CHAPTER4])
    pathname = obj.build_report(set_id, start_date, end_date, outpath)
    encrypted_pathname = obj.encrypt(pathname)
    pathname.unlink()
    is_send = RSDBFacade().read_app_configuration(key_='send_email')['value'].iloc[0]
    if is_send!='0':
        mail_report(encrypted_pathname)

@log_it(LOGGER)
def build_brief_report_all(*args, **kwargs):
    '''
    end_time : 截至时间
    delta : 单位天
    >>> build_brief_report_all(delta=120)
    '''
    delta = kwargs.get('delta', 30)
    end_time = kwargs.get('end_time', None)
    if end_time not in (None, ''):
        end_time = pd.to_datetime(kwargs['end_time']).date()
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{delta}d")
    for set_id in DEVICE_DF['set_id'].unique():
        pathname = REPORT_OUT_DIR
        build_brief_report(
            outpath=pathname.as_posix(), 
            set_id=set_id, 
            start_date=start_time,
            end_date=end_time
            ) 

#%% main
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    build_brief_report_all(end_time='2023-10-01', delta=30)