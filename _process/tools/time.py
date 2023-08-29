# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:46:05 2023

@author: luosz

数字信号时域函数
"""
# =============================================================================
# import
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

# =============================================================================
# fucntion
# =============================================================================
def resample(df:pd.DataFrame, *, rule:str='1s', limit:int=2):
    ''' 重采样，令时间对齐
    rule : str
        重采样周期
    limit, int
        Maximum number of consecutive NaNs to fill
    >>> import numpy as np
    >>> index = pd.date_range('2022-01-01 11:11:09.7', 
    ...     '2022-01-01 11:11:14.7', inclusive='left', freq='500ms')
    >>> df = pd.DataFrame({'a':np.arange(10), 'ts':index})
    >>> resample(df)['a'].sum()
    20
    >>> df['a'] = df['a'].astype('float')
    >>> resample(df)['a'].sum()
    23.0
    >>> df['a'] = ['good', 'bad', None, 'bad', 'bad'] + [None]*5
    >>> resample(df)['a'].value_counts()
    a
    bad     2
    good    1
    Name: count, dtype: int64
    '''
    df = df.set_index('ts')
    rev = df.resample(rule=rule).asfreq()
    rev = pd.concat([df,rev]).sort_index().reset_index()
    rev = rev.drop_duplicates('ts').reset_index(drop=True)
    # bool、category、object，只做forward fill
    sub = df.select_dtypes(include=['bool', 'category', 'object']).columns
    # rev[sub] = rev[sub].fillna(method='ffill', limit=limit)
    rev[sub] = rev[sub].ffill(limit=limit)
    # float类型数据做线性插值
    rev.set_index('ts', inplace=True)
    sub = df.select_dtypes(include='number').columns
    rev[sub] = rev[sub].astype('float').interpolate('index', limit=limit)
    # 去掉非整数秒的数据
    rev = rev.resample('1s').asfreq()
    rev = rev.dropna(how='any')
    # 保留原数据类型
    rev = rev.astype(df.dtypes.to_dict())
    rev.reset_index(inplace=True)
    return rev

def bin(x, length:str='10min'):
    ''' 数据分仓 '''
    return x.dt.floor(length)

if __name__ == "__main__":
    import doctest
    doctest.testmod()