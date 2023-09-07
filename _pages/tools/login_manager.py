# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:12:26 2023

@author: luosz

用户登录管理
"""
# =============================================================================
# imports
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_login import LoginManager
from flask_login import UserMixin  
  
from wtbonline._db.rsdb.model import User
from wtbonline._db.config import RSDB_URI

# =============================================================================
# constant
# =============================================================================
login_manager = LoginManager()
login_manager.login_view = '/login'

# =============================================================================
# function
# =============================================================================
@login_manager.user_loader
def load_user(user_id):
    with sessionmaker(create_engine(RSDB_URI))() as session:
        user = session.query(User).filter(User.id==user_id).first()
    return user