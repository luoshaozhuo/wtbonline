# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

# import pandas as pd

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, text
# import inspect
# from typing import Union, Optional, Mapping, List, Any
# from collections.abc import Iterable

# from wtbonline.db.config import RSDB_URI
# from wtbonline.db.rsdb import model
# from wtbonline.db.common import (make_sure_list, make_sure_dict, make_sure_dataframe)

# # class
# DB_ENGINE = create_engine(RSDB_URI)

# def get_session():
#     '''
#     返回类sessionmaker对象的调用
#     '''
#     return sessionmaker(DB_ENGINE)()

# class ORMFactory:
#     def __init__(self, uri=RSDB_URI):
#         self._get_table_mapping()

#     @property
#     def tbl_mapping(self):
#         return self._tbl_mapping

#     def _get_table_mapping(self):
#         self._tbl_mapping = {}
#         for i,j in inspect.getmembers(model, inspect.isclass):
#             if str(j).find('rsdb')>-1:
#                 self._tbl_mapping.update({j.__tablename__:j})

#     def get(self, tbname):
#         ''' 通过数据表名获取orm对象 '''
#         return self._tbl_mapping.get(tbname)