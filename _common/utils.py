import pandas as pd
from collections.abc import Iterable
from typing import Union, Optional
import numpy as np

def make_sure_dict(x)->dict:
    '''
    >>> make_sure_dict(1)
    Traceback (most recent call last):
    ...
    ValueError: not support type <class 'int'>
    >>> make_sure_dict({'a':1})
    {'a': 1}
    >>> make_sure_dict(pd.Series([1,2]))
    {0: 1, 1: 2}
    >>> make_sure_dict(pd.DataFrame([['a','b'],[1,2]]))
    {'a': 'b', 1: 2}
    >>> make_sure_dict(None)
    {}
    '''
    if x is None:
        rev = {} 
    elif isinstance(x, dict):
        rev = x
    elif isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            rev = x.squeeze().to_dict()
        if x.shape[1]==2:
            rev = {row[0]:row[1] for _,row in x.iterrows()}
    elif isinstance(x, pd.Series):
        rev = x.to_dict()
    else:
        raise ValueError(f'not support type {type(x)}')   
    return rev

def make_sure_dataframe(x)->pd.DataFrame:
    '''
    >>> make_sure_dataframe(1)
    Traceback (most recent call last):
    ...
    ValueError: not support type <class 'int'>
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
    if x is None:
        rev = pd.DataFrame()
    elif isinstance(x, pd.DataFrame):
        rev = x
    elif isinstance(x, dict):
        rev = pd.DataFrame(x, index=[1])
    elif isinstance(x, (list, tuple)):
        rev = pd.DataFrame(x, index=np.arange(len(x)))
    elif isinstance(x, pd.Series):
        rev = x.to_frame()
    elif isinstance(x, np.ndarray):
        rev = pd.DataFrame(x)
    else:
        raise ValueError(f'not support type {type(x)}')  
    return rev

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
    if isinstance(x, (tuple, list, set)):
        rev = list(x)
    elif x is None:
        rev = []
    elif isinstance(x, (str, int, float, bool)):
        rev = [x]
    elif hasattr(x, 'tolist'):
        rev = x.tolist()
    elif isinstance(x, pd.DataFrame):
        if x.shape[1]==1:
            rev = x.squeeze().tolist()
        else:
            rev = [x[i].tolist() for i in x]        
    elif isinstance(x, Iterable):
        rev = [i for i in x]
    else:
        raise ValueError(f'not support type {type(x)}')
    return rev

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
    if x is None:
        rev = None
    elif isinstance(x, str):
        rev = pd.to_datetime(x)
    elif isinstance(x, (list, tuple, set, pd.Series, dict)):
        rev = pd.to_datetime(pd.Series(x)).tolist()
    else:
        try:
            rev = pd.to_datetime(x)
        except:
            raise ValueError(f'not support type {type(x)}')
    return rev

if __name__ == "__main__":
    import doctest
    doctest.testmod()