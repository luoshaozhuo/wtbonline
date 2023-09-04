# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:36:48 2023

@author: luosz

APP配置
"""
# =============================================================================
# import
# =============================================================================
import os
from _database.config import URI

# =============================================================================
# class
# =============================================================================
class Default:
    SECRET_KEY=os.urandom(12)
    SQLALCHEMY_DATABASE_URI=URI
    SQLALCHEMY_TRACK_MODIFICATIONS=False