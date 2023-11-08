import pandas as pd
from collections.abc import Iterable
from typing import Union, Optional
import numpy as np
import datetime

def make_sure_dict(x)->dict:
    '''
    >>> make_sure_dict(1)
    {}
    >>> make_sure_dict({'a':1})
    {'a': 1}
    >>> make_sure_dict(pd.Series([1,2]))
    {0: 1, 1: 2}
    >>> make_sure_dict(pd.DataFrame([['a','b'],[1,2]]))
    {'a': 'b', 1: 2}
    >>> make_sure_dict(None)
    {}
    '''
    if isinstance(x, dict):
        return x
    
    if isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze()
        elif x.shape[1]==2:
            x = {row[0]:row[1] for _,row in x.iterrows()}
    if isinstance(x, pd.Series):
        x = x.to_dict()
    if not isinstance(x, dict):
        x = {}
    return x

def make_sure_dataframe(x)->pd.DataFrame:
    '''
    >>> make_sure_dataframe(1)
    Empty DataFrame
    Columns: []
    Index: []
    >>> make_sure_dataframe({'a':1,'b':2})
       a  b
    1  1  2
    >>> make_sure_dataframe(pd.Series([1,2], name='x'))
       x
    0  1
    1  2
    >>> make_sure_dataframe(pd.DataFrame([['a','b'],[1,2]]))
       0  1
    0  a  b
    1  1  2
    >>> make_sure_dataframe(None)
    Empty DataFrame
    Columns: []
    Index: []
    '''
    if isinstance(x, pd.DataFrame):
        return x
    
    if isinstance(x, dict):
        x = pd.DataFrame(x, index=[1])
    elif isinstance(x, (list, tuple)):
        x = pd.DataFrame(x, index=np.arange(len(x)))
    elif isinstance(x, pd.Series):
        x = x.to_frame()
    elif isinstance(x, np.ndarray):
        x = pd.DataFrame(x)
    
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame()
    return x

def make_sure_series(x)->pd.Series:
    '''
    # >>> make_sure_series(1)
    # 0    1
    # dtype: int64
    # >>> make_sure_series({'a':1})
    # a    1
    # dtype: int64
    # >>> make_sure_series(pd.Series([1,2], name='x'))
    # 0    1
    # 1    2
    # Name: x, dtype: int64
    >>> make_sure_series(pd.DataFrame([['a','b'],[1,2]]))
    0
    a    b
    1    2
    Name: 1, dtype: object
    >>> make_sure_series(None)
    Series([], dtype: object)
    '''
    if isinstance(x, pd.Series):
        return x

    if isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze()
        elif x.shape[1]==2:
            x = x.set_index(x.columns[0]).squeeze()
        else:
            x = pd.Series()
    elif x is None:
        x = pd.Series()
    elif isinstance(x, str):
        x = pd.Series(x)
    elif isinstance(x, Iterable):
        x = pd.Series([i for i in x])
    else:
        x = pd.Series([x])
    return x

def make_sure_list(x)->list:
    ''' 确保输入参数是一个list 
    >>> make_sure_list('abc')
    ['abc']
    >>> make_sure_list(1)
    [1]
    >>> make_sure_list(pd.Series([1,2]))
    [1, 2]
    >>> make_sure_list(pd.DataFrame([1,2]))
    [1, 2]
    >>> make_sure_list(pd.DataFrame([[1,2],[3,4]]))
    [[1, 3], [2, 4]]
    '''
    if isinstance(x, list):
        rev = x
    elif x is None:
        x = []
    elif isinstance(x, str):
        x = [x]
    elif hasattr(x, 'tolist'):
        x = x.tolist()
    elif isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            x = x.squeeze().tolist()
        else:
            x = [x[i].tolist() for i in x]        
    elif isinstance(x, Iterable):
        x = [i for i in x]
    else:
        x = [x]
    return x

def make_sure_datetime(
        x:Union[str, Iterable]
        )->Optional[Union[pd.Timestamp, list[pd.Timestamp], pd.Series]]:
    '''
    >>> type(make_sure_datetime('2020-10-01'))
    <class 'pandas._libs.tslibs.timestamps.Timestamp'>
    >>> a,b = make_sure_datetime(['2020-10-01', '2020-10-02'])
    >>> type(a)
    <class 'pandas._libs.tslibs.timestamps.Timestamp'>
    '''
    if isinstance(x, (pd.Timestamp, datetime.date)):
        rev = x
    elif isinstance(x, str):
        rev = pd.to_datetime(x)
    elif isinstance(x, (list, tuple)):
        rev = pd.to_datetime(x).tolist()
    elif isinstance(x, pd.Series):
        rev = pd.to_datetime(x)
    elif isinstance(x, pd.DataFrame):
        x = x.squeeze()
        if isinstance(x, pd.Series):
            rev = pd.to_datetime(x.squeeze())
        else:
            rev = None
    else:
        rev = None
    return rev

if __name__ == "__main__":
    import doctest
    doctest.testmod()