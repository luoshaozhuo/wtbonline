# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

#%% import
from typing import List, Mapping

from wtbonline._db.rsdb.factory import ORMFactory
from wtbonline._db.rsdb.clause.select_ import Select
from wtbonline._common import utils

#%% constant

#%% class
class Where():
    '''
    >>> model_ = ORMFactory().get('user')
    >>> print(Where()(
    ... model_, 
    ... {'eq':{'username':'admin'}, 
    ...  'in':{'username':['a', 'b']}, 
    ...  'lge':{'privilege':1},
    ...  'lt':{'privilege':2}}
    ... ))
    SELECT "user".id, "user".username, "user".password, "user".privilege 
    FROM "user" 
    WHERE "user".username = :username_1 AND "user".username IN (__[POSTCOMPILE_username_2]) AND "user".privilege >= :privilege_1 AND "user".privilege < :privilege_2
    '''
    def __call__(self, model_, params:Mapping[str, Mapping[str, List[str]]], stmt=None):
        stmt = Select()(model_) if stmt is None else stmt
        params = utils.make_sure_dict(params)
        conditions = []
        for type_ in params.keys():
            values = params[type_]
            values = utils.make_sure_dict(values)
            if type_=='eq':
                for key_ in values:
                    conditions.append(getattr(model_, key_)==values[key_])
            elif type_=='lge':
                for key_ in values:
                    conditions.append(getattr(model_, key_)>=values[key_])
            elif type_=='lt':
                for key_ in values:
                    conditions.append(getattr(model_, key_)<values[key_])
            elif type_=='in':
                for key_ in values:
                    conditions.append(getattr(model_, key_).in_(values[key_]))
            else:
                raise ValueError('pamrams里的关键词必须是eq,lge,lt,in中的一个')
        if len(conditions)>0:
            stmt = stmt.where(*conditions)
        return stmt
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()