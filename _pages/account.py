# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 14:22:56 2023

@author: luosz

账户管理页面
"""

# =============================================================================
# import
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

from dash import html, dcc, Input, Output, no_update, callback, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from _database import _mysql as msql
from _database import model
from _pages.tools.decorator import _on_error
    
    
# =============================================================================
# constant
# =============================================================================
_PREFIX = 'account'

# =============================================================================
# layout
# =============================================================================
_old_password = dbc.Row(
    [
    dbc.Label("旧密码", width=2),
    dbc.Col(
        dbc.Input(
            type="password", id=f'{_PREFIX}_old_password', 
            placeholder="Enter password"
        ),
    ),
    ],
    className="mb-3"
    )

_new_password = dbc.Row(
    [
     dbc.Label("新密码", width=2),
     dbc.Col(
         dbc.Input(
             type="password", id=f'{_PREFIX}_new_password', 
             placeholder="Enter password"
         ),
         width=6,
     ),
     dbc.Col(
         dbc.Button('修改',id=f'{_PREFIX}_btn_update'),
         className="d-grid",
     ),
    ],
    className="mb-3"
    )

_user_name = dbc.Row(
    [
     dbc.Label("用户名", width=2),
     dbc.Col(
         dbc.Input(
             type="text", id=f'{_PREFIX}_user_name', placeholder="Enter username"
         ),
         width=10,
     ),
    ],
    className="mb-3"
    )

_password = dbc.Row(
    [
     dbc.Label("密码", width=2),
     dbc.Col(
         dbc.Input(
             type="password", id=f'{_PREFIX}_password', placeholder="Enter password"
         ),
         width=10,
     ),
    ],
    className="mb-3"
    )

_privilege = dbc.Row(
    [
     dbc.Label("权限", width=2),
     dbc.Col(
         dcc.Dropdown(
             id=f'{_PREFIX}_dropdwon_privilege',
             value='用户',
             clearable=False,
             options=['管理员','用户']
             ),
         width=6,
     ),
     dbc.Col(
         dbc.Button('提交',id=f'{_PREFIX}_btn_admit'),
         className="d-grid",
     ),
    ],
    align="center",
    className="mb-3"
    )

def _card_body():
    try:
        privilege = current_user.privilege
    except:
        privilege = 1   
    rev = [_old_password, _new_password]
    if privilege == 1:
        rev += [html.Hr(),
                _user_name,
                _password,
                _privilege,
                html.Hr(),
                dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                           id=f'{_PREFIX}_btn_refresh',
                           size='sm',
                           className='btn-secondary mb-1'),
                dash_table.DataTable(
                    id=f'{_PREFIX}_datatable',
                    columns=[{'name': i, 'id': i} for i in ['用户名', '权限']],                           
                    row_deletable=False,
                    page_action='native',
                    page_current= 0,
                    page_size= 10,
                    style_header = {'font-weight':'bold'},
                    style_table = {'font-size':'small'}
                    )]
    return rev     

def get_layout():
    layout = [
        dbc.Alert(id=f'{_PREFIX}_alert', color='danger', duration=3000, is_open=False, className='border rounded-0'),
        dbc.Card(
            [dbc.CardHeader(dbc.ModalTitle('账户管理', class_name='fs-4')),
             dbc.CardBody(_card_body())],
            style={'width':'500px'},
            class_name='position-absolute top-50 start-50 translate-middle',
            )
        ]
    return layout

# =============================================================================
# callback
# =============================================================================
@callback(
    Output(f'{_PREFIX}_datatable', 'data'),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    )
@_on_error
def on_account_btn_refresh(n):
    df = msql.read_user(columns=['username', 'privilege'])
    df['privilege'].replace({1:'管理员', 0:'用户'})
    df.columns = ['用户名', '权限']
    return df.to_dict('records')

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'color', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_admit', 'n_clicks'),
    State(f'{_PREFIX}_user_name', 'value'),
    State(f'{_PREFIX}_password', 'value'),
    State(f'{_PREFIX}_dropdwon_privilege', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_account_btn_admit(n, user_name, password, privilege):
    if None in (user_name, password):
        return no_update, '用户名或密码为空', True, 'danger'
    privilege = 1 if privilege=='管理员' else 0
    hashed_password = generate_password_hash(password, method='scrypt')
    df = pd.DataFrame({'username':user_name, 
                       'password':hashed_password,
                       'privilege':privilege},
                      index=[0])
    msql.insert(df, model.User, keys='username')
    df = msql.read_user(columns=['username', 'privilege'])
    df['privilege'].replace({1:'管理员', 0:'用户'})
    df.columns = ['用户名', '权限']
    return df.to_dict('records'), '提交成功', True, 'success'

@callback(
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'color', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_update', 'n_clicks'),
    State(f'{_PREFIX}_old_password', 'value'),
    State(f'{_PREFIX}_new_password', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_account_btn_update(n, old_password, new_password):
    if None in (old_password, new_password):
        return '新密码或旧密码为空', True, 'danger'
    
    try:
        _ = current_user.password
        this_user = current_user
    except:
        this_user = msql.read_user('admin').squeeze()
    
    if not check_password_hash(this_user.password, old_password):
        return '旧密码不正确', True, 'danger'
    
    new_password = generate_password_hash(new_password, method='scrypt')
    sr = pd.Series({'password':new_password, 'username':this_user.username})    
    msql.update_one(sr, 'username', model.User)
    
    return '密码已修改', True, 'success'

# =============================================================================
# for test
# =============================================================================
if __name__ == '__main__':     
    import dash
    app = dash.Dash(__name__, 
                    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
                    suppress_callback_exceptions=True)
    app.layout = html.Div(get_layout())
    debug = True if len(sys.argv)>1 else False
    app.run_server(debug=debug)
    