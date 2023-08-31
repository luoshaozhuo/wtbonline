# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 11:58:00 2023

@author: luosz

登录页
"""

# =============================================================================
# imoprt
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
from flask_login import login_user
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from wtbonline._db.config import RSDB_URI
from wtbonline._db.rsdb.model import User

# =============================================================================
# constant
# =============================================================================
def get_layout():
    layout = html.Div([
            dcc.Location(id='login_location', refresh=False),
            dbc.Alert(
                "用户名密码错误",
                id="login_alert",
                color = 'danger',
                duration=3000,
                is_open=False,
                ),
            html.Div([
                dbc.Container(children=[
                    dcc.Input(
                        placeholder='用户名',
                        type='text',
                        id='login_input_username',
                        className='form-control form-control-sm',
                        n_submit=0,
                    ),
                    html.Br(),
                    dcc.Input(
                        placeholder='密码',
                        type='password',
                        id='login_input_password',
                        className='form-control form-control-sm',
                        n_submit=0,
                    ),
                    html.Br(),
                    html.Button(
                        children='登录',
                        n_clicks=0,
                        type='submit',
                        id='login_button_login',
                        className='btn btn-primary btn-sm'
                    ),
                    html.Br(),
                ], className='form-group'),
            ], className='w-25 position-absolute start-50 top-50 translate-middle')
        ])
    return layout

# =============================================================================
# callback
# =============================================================================
@callback(Output('login_location', 'pathname'),
          Output('login_location', 'refresh'),
          Output('login_alert', 'is_open'),
          Input('login_button_login', 'n_clicks'),
          State('login_input_username', 'value'),
          State('login_input_password', 'value'),
          prevent_initial_call=True,
          )
def on_login_button_login(n_clicks, username, password):
    with sessionmaker(create_engine(RSDB_URI))() as session:
        user = session.query(User).filter_by(username=username).first()
    if user and password and check_password_hash(user.password, password):
        login_user(user)
        return '/', True, no_update
    return no_update, False, True

if __name__ == '__main__':
    import dash
    app = dash.Dash(__name__, 
                    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
                    suppress_callback_exceptions=True)
    app.layout = html.Div(get_layout())
    app.run_server(debug=False)