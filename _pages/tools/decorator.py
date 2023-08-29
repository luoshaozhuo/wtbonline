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
        except:
            raise ValueError(('--args:', *args, '--kwargs:', kwargs))
        return rs
    return wrapper