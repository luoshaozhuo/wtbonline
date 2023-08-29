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

from _database.model import db
from _pages.tools.login_manager import login_manager
from config import Default

# =============================================================================
# global
# =============================================================================
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True)

server = app.server
server.config.from_object(Default())

db.init_app(server)
login_manager.init_app(server)
