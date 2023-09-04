# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 00:07:46 2023

@author: luosz
"""

# =============================================================================
# decorator
# =============================================================================
def _on_error(func):
    def wrapper(*args, **kwargs):
        try:
            rs = func(*args, **kwargs)
        except Exception as e :
            p_args = ', '.join([str(i) for i in args])
            p_kwargs = ', '.join([f'{i}={str(kwargs[i])}' for i in kwargs])
            params = f'{p_args},{p_kwargs}'.strip(',')
            raise ValueError(f'{func.__name__}({params}) error \n {str(e)}')
        return rs
    return wrapper