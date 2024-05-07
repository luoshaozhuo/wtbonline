import logging
import logging.handlers
from pathlib import Path    
import os
import pandas as pd
    
from wtbonline._db.rsdb_facade import RSDBFacade

_parent = RSDBFacade.read_app_configuration(key_='log_path').loc[0, 'value']
_parent = Path(_parent)

def get_stream_handler():
    handler = logging.StreamHandler()#默认是sys.stderr
    handler.setLevel(logging.INFO) 
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(pathname)s %(lineno)d pid=%(process)s tid=%(thread)s \n %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    handler.setFormatter(formatter)
    return handler

def get_error_handler(_dir, name:str):
    handler = logging.handlers.TimedRotatingFileHandler(filename=_dir/'err.log', when='W0')
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(pathname)s %(lineno)d pid=%(process)s tid=%(thread)s \n %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    return handler 

def get_info_handler(_dir, name:str):
    handler = logging.handlers.TimedRotatingFileHandler(filename=_dir/'info.log', when='W0')
    formatter = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(pathname)s %(lineno)d pid=%(process)s tid=%(thread)s \n %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler = logging.FileHandler(filename=_dir/'info.log')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    return handler 

def get_logger(name:str):
    '''
    >>> logger = get_logger('test')
    >>> logger.info('info')
    >>> logger.warning('warning')
    >>> try:
    ...     raise ValueError('123')
    ... except Exception as e:
    ...     logger.error(f'{e}', exc_info=True)
    '''

    rev = logging.getLogger(name)
    if len(rev.handlers)>0:
        return rev
    _dir = _parent/name
    _dir.mkdir(parents=True, exist_ok=True)
    rev.setLevel(logging.INFO)
    rev.addHandler(get_info_handler(_dir,name))
    rev.addHandler(get_error_handler(_dir,name))
    rev.addHandler(get_stream_handler())
    return rev

def log_it(logger):
    '''
    >>> logger = get_logger('test')
    >>> @log_it(logger)
    ... def test():
    ...     pass
    >>> test() 
    '''
    def inner(func):
        def wrapper(*args, **kwargs):
            p_args = ', '.join([str(i) for i in args])
            p_kwargs = ', '.join([f'{i}={str(kwargs[i])}' for i in kwargs])
            params = f'{p_args},{p_kwargs}'.strip(',')
            pid = os.getppid()
            logger.info(f'pid={pid}, function={func.__name__}({params}) start')
            rev = None
            try:
                rev = func(*args, **kwargs)
            except Exception as e:
                logger.error(f'pid={pid}, function={func.__name__}({params})  error \n {str(e)}', exc_info=True)
                raise
            else:
                logger.info(f'pid={pid}, function={func.__name__}({params}) finihed')
            return rev
        return wrapper
    return inner 


if __name__ == "__main__":
    import doctest
    doctest.testmod()