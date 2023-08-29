"""
Created on Wed Apr 19 15:26:15 2023

@author: luosz

用户管理函数
"""
# =============================================================================
# import
# =============================================================================
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from config import get_db_session
from model import User

# =============================================================================
# function
# =============================================================================
def add_user(username, password, privilege):
    hashed_password = generate_password_hash(password, method='scrypt')
    with get_db_session() as session:
        user = session.query(User).filter(User.username==username).first()
        if user:
            raise ValueError('用户已存在')
        else:
            user = User(username=username, password=hashed_password, privilege=privilege)
            session.add(user)
            session.commit()
            

def update_password(username, password):
    hashed_password = generate_password_hash(password, method='scrypt')
    with get_db_session() as session:
        query = session.query(User).filter(User.username==username) 
        query.update({User.password:hashed_password})
        session.commit()


def get_all_users():
   with get_db_session() as session:
       ret = session.query(User.id, User.username, User.privilege).all()    
   return ret 
