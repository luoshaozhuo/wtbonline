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
from flask_login import LoginManager, UserMixin
    
from _database.model import User as _User
from _database.config import URI

# =============================================================================
# constant
# =============================================================================
login_manager = LoginManager()
login_manager.login_view = '/login'

# =============================================================================
# class
# =============================================================================
class User(UserMixin, _User):
    pass

# =============================================================================
# function
# =============================================================================
@login_manager.user_loader
def load_user(user_id):
    with sessionmaker(create_engine(URI))() as session:
        user = session.query(User).filter(User.id==user_id).first()
    return user