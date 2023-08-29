# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 11:59:04 2023

@author: luosz

自动生成sqlalchemy模型代码
"""
import os
from platform import platform
from wtbonline._db.config import RSDB_URI
from pathlib import Path

if __name__ == '__main__':
    p = Path(__file__).parent/'model.py'
    cmd = f'flask-sqlacodegen {RSDB_URI} --outfile {p} --flask'
    os.system(cmd)