'''

'''

import os
from setuptools import setup, find_namespace_packages

def _process_requirements():
    packages = open('./wtbonline/requirements.txt').read().strip().split('\n')
    requires = [pkg for pkg in packages]
    return requires

setup(
    name="wtbonline",
    version="1.0",
    author="luoshaozhuo",
    author_email="luoshaozhuo@163.com",
    description="智能辅助风力发电机性能分析系统",
    packages=find_namespace_packages(), # 不需要包含namespace packge时，改为find_packages()
    python_requires='>3.7, <3.10',
    install_requires=_process_requirements(),
    entry_points={
    'console_scripts':[
        'wtbonline = wtbonline.run:main' # 格式为'命令名 = 模块名:函数名'
    ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ]
)