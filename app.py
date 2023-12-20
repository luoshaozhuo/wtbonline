# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:35:00 2023

@author: luosz
"""

# =============================================================================
# import
# =============================================================================
import dash
import dash_bootstrap_components as dbc

from wtbonline._pages.tools.login_manager import login_manager
from wtbonline.config import Default
from wtbonline._db.rsdb.model import db

# =============================================================================
# global
# =============================================================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

server = app.server
server.config.from_object(Default())

db.init_app(server)
login_manager.init_app(server)
