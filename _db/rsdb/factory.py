# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

#%% import
import inspect

from wtbonline._db.rsdb import model

#%% function

#%% class
class ORMFactory:
    def __init__(self):
        self._tbl_mapping = self._get_table_mapping()

    @property
    def tbl_mapping(self):
        return self._tbl_mapping

    def _get_table_mapping(self):
        rev = {}
        for i,j in inspect.getmembers(model, inspect.isclass):
            if str(j).find('rsdb')>-1:
                rev.update({j.__tablename__:j})
        return rev

    def get(self, tbname):
        ''' 通过数据表名获取orm对象 '''
        return self._tbl_mapping.get(tbname)

ORMFactory()