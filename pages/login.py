# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 11:58:00 2023

@author: luosz

登录页
"""

#%% import
import dash_bootstrap_components as dbc
import dash
import dash_mantine_components as dmc
from dash import dcc, callback, Input, Output, State, no_update
from flask_login import login_user
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import partial

from wtbonline._db.config import RSDB_URI
from wtbonline._db.rsdb.model import User
from wtbonline._common import utils


#%% constant
PREFIX = 'login'

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component

#%% layout
if __name__ == '__main__':     
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

dash.register_page(__name__,  path="/login", title="Winturbine Data Assistant System")

layout = dmc.Center(
    style={'height':'100vh'},
    children=[
        dcc.Location(id=get_component_id('location'), refresh=False),
        dmc.Stack(
            align='center',
            children=[
                dmc.TextInput(
                    id=get_component_id('input_username'), 
                    style={"width": 200}, 
                    label="用户名:",
                    placeholder='username',
                    size='xs',
                    withAsterisk=True,
                    ),
                dmc.PasswordInput(
                    id=get_component_id('input_password'),
                    placeholder="password",
                    style={"width": 200},
                    size='xs',
                    label="密码",
                    withAsterisk=True,
                    ),
                dmc.Button("登录", id=get_component_id("btn_login"), size='xs'),
                ]
            ), 
        ]
    )

# =============================================================================
# callback
# =============================================================================
@callback(
    Output(get_component_id("location"), 'pathname'),
    Output(get_component_id("location"), 'refresh'),
    Output(get_component_id("input_username"), 'error'),
    Output(get_component_id("input_password"), 'error'),
    Input(get_component_id("btn_login"), 'n_clicks'),
    State(get_component_id("input_username"), 'value'),
    State(get_component_id("input_password"), 'value'),
    prevent_initial_call=True,
    )
def on_login_button_login(n_clicks, username, password):
    location = no_update
    refresh = False
    error_username = '忘记什么了吧' if username in [None, ''] else ''
    error_password = '忘记什么了吧' if password in [None, ''] else ''
    if error_username=='' and error_password=='':
        with sessionmaker(create_engine(RSDB_URI))() as session:
            user = session.query(User).filter_by(username=username).first()
        if user and password and check_password_hash(user.password, password):
            login_user(user)
            location = '/'
            refresh = True
            error_username = error_password = ''
        else:
            error_username = error_password = '用户名或密码错误'
    return location, refresh, error_username, error_password

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)