# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:46:05 2023

@author: luosz

数字信号统计域函数
"""
# =============================================================================
# import
# =============================================================================
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from functools import wraps
from typing import List, Callable
from itertools import product

from wtbonline._common.utils import EPS, make_sure_series

# =============================================================================
# fucntion
# =============================================================================
def _dec(func):
    @wraps(func)
    def wrapper(x, *args, **kwargs):
        x = make_sure_series(x)
        return func(x, *args, **kwargs)
    return wrapper

@_dec
def stationarity(x) -> pd.Series:
    ''' 计算时间序列平稳性指标 
    >>> x = np.random.normal(size=1000)
    >>> (stationarity(x)<0.0001).all()
    True
    '''
    regs = ['c', 'ct', 'ctt']
    try:
        values = [adfuller(x, regression=i)[1] for i in regs]
    except:
        values = [-1]*len(regs)
    return pd.Series(values, index=['pv_c', 'pv_t', 'pv_ctt'])


@_dec
def mean(x)->float:
    '''
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(mean(x), float)
    True
    >>> mean(0)
    0.0
    '''
    return x.mean()

@_dec
def std(x)->float:
    '''
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(std(x), float)
    True
    >>> std(0)
    nan
    '''
    return x.std()

@_dec
def skew(x)->float:
    '''
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(skew(x), float)
    True
    >>> skew(0)
    nan
    '''
    return x.skew()

@_dec
def kurt(x)->float:
    '''
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(kurt(x), float)
    True
    >>> kurt(0)
    nan
    '''
    return x.kurt()

@_dec
def rms(x):
    ''' 均方根值 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(rms(x), float)
    True
    >>> rms(0)
    0.0
    >>> rms(-1)
    1.0
    '''
    ms = x.pow(2).sum()/x.shape[0]
    return np.sqrt(ms)

@_dec
def crest(x)->float:
    ''' 波峰系数 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(crest(x), float)
    True
    >>> crest(0)
    0.0
    '''
    return (x.max()-x.min())/(rms(x)+EPS)/2

@_dec
def iqr(x)->float:
    ''' 四分位距 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(iqr(x), float)
    True
    >>> iqr(0)
    0.0
    '''
    return x.quantile(0.75) - x.quantile(0.25)

@_dec
def cv(x)->float:
    ''' robust变异系数 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(cv(x), float)
    True
    >>> cv(0)
    0.0
    '''
    denom = x.median()
    denom = denom if abs(denom)>0 else EPS
    nom = iqr(x)
    return iqr(x)/denom

@_dec
def imp(x)->float:
    ''' 脉冲因子 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(imp(x), float)
    True
    '''
    return iqr(x)/(rms(x)+EPS)/2

@_dec
def zc(x, thd=0)->float:
    ''' 过零率 
    >>> zc([-1,1,-1])
    1.0
    >>> zc([-1,1])
    1.0
    >>> zc([-1,1,1,-1])
    0.667
    >>> zc([-1,1,1,-1,0.1,-0.1,0.1,-0.1], thd=0.1)
    0.286
    >>> zc(0)
    0.0
    '''
    if len(x)<2:
        return 0.0
    n = len(x) - 1
    x = x - x.mean()
    x = x.where(~x.between(-1*thd, thd), np.nan).dropna()
    count = np.sign(x).diff().abs().sum()
    return (0.5*count/n).round(3)

@_dec
def wf(x):
    ''' 波形系数 
    >>> x = np.random.normal(0, 1, size=100)
    >>> isinstance(wf(x), float)
    True
    >>> wf(0)
    0.0
    '''
    return rms(x)/(pd.Series(x).abs().mean()+EPS)

@_dec
def unique(x):
    ''' 唯一值 
    >>> x = ['a','b','c','a']
    >>> unique(x)
    'a,b,c'
    >>> unique('a')
    'a'
    '''
    x = make_sure_series(x)
    return ','.join(x.unique().astype(str))

@_dec
def nunique(x):
    ''' 唯一值个数 
    >>> x = ['a','b','c','a']
    >>> nunique(x)
    3
    >>> nunique('a')
    1
    '''
    x = make_sure_series(x)
    return len(x.unique())

@_dec
def mode(x):
    ''' 出现次数最多的值 
    >>> x = ['a','b','c','a']
    >>> mode(x)
    'a'
    >>> mode('a')
    'a'
    '''
    x = make_sure_series(x)
    # pd.Series.mode 返回一个series，因为mode值可能会重复
    return x.mode().iloc[0]

def agg(df:pd.DataFrame, funcs:List[Callable])->pd.Series:
    rev = []
    index = []
    for func in funcs:
        rev += df.apply(func).tolist()
        index += (df.columns + f'_{func.__name__}').tolist()
    # index = list(product(df.columns, [i.__name__ for i in funcs]))
    # index = ['_'.join(i) for i in index]
    rev = pd.Series(rev, index=index)
    return rev

def numeric_statistics():
    ''' 数值类型变量常用统计量 '''
    return [mean, rms, iqr, std, skew, kurt, wf, crest, zc, cv, imp]

def category_statistics():
    return [mode, unique, nunique]

if __name__ == "__main__":
    import doctest
    doctest.testmod()