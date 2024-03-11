# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:33:43 2023

@author: luosz

"""

#%% import
from typing import List, Union, Optional, Mapping
from sqlalchemy import create_engine, text, func, select, delete, update, insert

from wtbonline._db.rsdb.factory import ORMFactory

#%% constant
type_ = Optional[Union[List[str], Mapping[str, List[str]]]]

#%% class
class Select():
    '''
    >>> print(Select()(ORMFactory().get('user'), 'username'))
    SELECT "user".username 
    FROM "user"
    >>> print(Select()(ORMFactory().get('user'), {'username':'avg'}))
    SELECT avg("user".username) AS username_avg 
    FROM "user"
    '''
    def __call__(self, model_, params:type_=None):
        if params is None:
            stmt = select(model_)
        else:
            if isinstance(params, (list, tuple, str)):
                if isinstance(params, str):
                    params = [params]
                assert len(params)>0, f'参数长度小于1，parmas={params}'
                columns = [getattr(model_, i) for i in params]
            elif isinstance(params, dict):
                assert len(params)>0, f'参数长度小于1，parmas={params}'
                columns = []
                for key_ in params:
                    funcs = params[key_]
                    if isinstance(funcs, str):
                        funcs = [funcs]
                    assert len(funcs)>0, f'{key_}的聚合函数长度为0，funcs={params}'
                    columns += [
                        eval(f'func.{f}')(getattr(model_, key_)).label(f'{key_}_{f}')
                        for f in funcs
                        ]
            else:
                raise ValueError(f'支持参数类型为{type_}， 传入{type(params)}')
            stmt = select(*columns)
        return stmt


    
if __name__ == "__main__":
    import doctest
    doctest.testmod()