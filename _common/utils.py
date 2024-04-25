import pandas as pd
from collections.abc import Iterable
from typing import Union, Optional
import numpy as np
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
import pathlib

EPS = np.finfo(np.float32).eps

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
        try:
            rev = pd.DataFrame(x, index=[1])
        except:
            rev = pd.DataFrame(x)
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
    if isinstance(x, list):
        rev = x
    if isinstance(x, (tuple, set)):
        rev = list(x)
    elif x is None:
        rev = []
    elif isinstance(x, (str, dict, np.number, int, float)):
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
        rev = [x]
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

def send_email(recv:str, title:str, content:str, user_name:str='hzfdtest@126.com', password:str='YHWERYTJAMTBCLBE', host='smtp.126.com', port=25, pathname:str=None, ):
    '''
    >>> send_email('luoshaozhuo@163.com', '测试', '测试', pathname='/mnt/d/ll/report/系统架构.pptx')
    '''
    if pathname:
        msg = MIMEMultipart()
        # 构建正文
        part_text = MIMEText(content)
        msg.attach(part_text)  # 把正文加到邮件体里面去

        # 构建邮件附件
        part_attach1 = MIMEApplication(open(pathname, 'rb').read())  # 打开附件
        part_attach1.add_header('Content-Disposition', 'attachment', filename =pathlib.Path(pathname).name)  # 为附件命名
        msg.attach(part_attach1)  # 添加附件
    else:
        msg = MIMEText(content)  # 邮件内容
    msg['Subject'] = title  # 邮件主题
    msg['From'] = user_name # 发送者账号
    msg['To'] = recv  # 接收者账号列表
    try:
        smtp = smtplib.SMTP(host, port)
        smtp.login(user_name, password)  # 登录
        smtp.sendmail(user_name, recv, msg.as_string())
        smtp.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(e.smtp_code, e.smtp_error.decode('gbk'))
        raise

if __name__ == "__main__":
    import doctest
    doctest.testmod()