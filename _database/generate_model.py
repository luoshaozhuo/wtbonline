# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 11:59:04 2023

@author: luosz

自动生成sqlalchemy模型代码
"""
import os
from platform import platform
from config import URI

conda = 'conda'
env = 'dash'
cmd = f'flask-sqlacodegen {URI} --outfile ./model.py --flask'

if platform().startswith('Windows'):
    cmd = f'{conda} activate {env} && {cmd}'

os.system(cmd)
