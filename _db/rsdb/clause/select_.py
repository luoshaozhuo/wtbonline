# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

#%% import
from typing import List, Union, Optional, Mapping
from sqlalchemy import func, select

from wtbonline._db.rsdb.factory import ORMFactory
from wtbonline._common import utils

#%% constant
type_ = Optional[List[Union[str, Mapping[str, List[str]]]]]

#%% class
class Select():
    '''
    >>> model_ = ORMFactory().get('user')
    >>> print(Select()(model_, 'username'))
    SELECT "user".username 
    FROM "user"
    >>> print(Select()(model_, {'username':'avg'}))
    SELECT avg("user".username) AS username_avg 
    FROM "user"
    >>> print(Select()(model_, ['username', {'username':'avg'}]))
    SELECT "user".username, avg("user".username) AS username_avg 
    FROM "user"
    '''
    def __call__(self, model_, params:type_=None, stmt=None):# -> Select[Tuple] | Select[Any]:
        params = utils.make_sure_list(params)
        if len(params)==0:
            stmt = select(model_)
        else:
            columns = []
            for i in params:
                if isinstance(i, str):
                    columns.append(getattr(model_, i))
                elif isinstance(i, dict):
                    for key_ in i:
                        funcs = utils.make_sure_list(i[key_])
                        assert len(funcs)>0, f'{key_}的聚合函数长度为0，funcs={i}'
                        columns += [
                            eval(f'func.{f}')(getattr(model_, key_)).label(f'{key_}_{f}')
                            for f in funcs
                            ]
                else:
                    raise ValueError(f'支持参数类型为str, dict， 传入{type(i)}')
                stmt = select(*columns)
        return stmt
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()