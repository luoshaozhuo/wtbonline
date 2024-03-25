'''
作者：luosz
创建日期： 2024.02.18
描述：探索--二维图
    1、时序图
    2、散点图
    3、极坐标图
    4、频谱图
'''

#%% import
import dash
import dash_mantine_components as dmc
from dash import Output, Input, html,  callback, no_update, State, dash_table
from functools import partial
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dash_iconify import DashIconify
import pandas as pd

from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
import wtbonline._common.dash_component as dcmpt
from wtbonline._common.dash_component import notification

#%% constant
PREFIX = 'user_administrate'

TABLE_HEADERS = ['用户名', '权限']
COLUMN_NAME = ['username', 'privilege']
PRIVILEGE = pd.DataFrame([[1, '管理员'], [2,'用户']], columns=['int_', 'str_'])

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)
    
def func_build_table_content(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table    

def func_read_user_table():
    df, note = dcmpt.dash_dbquery(RSDBFacade.read_user, columns=COLUMN_NAME)
    if note is None:
        df['privilege'] = PRIVILEGE.set_index('int_').loc[df['privilege'], 'str_'].tolist()
        df.columns = TABLE_HEADERS
        data = df.to_dict('records')
    else:
        data = no_update
    return data, note


#%% component
def creaet_controlers():
    return dmc.Stack([
        dmc.TextInput(
            id=get_component_id('input_username'), 
            style={"width": 200}, 
            label="用户名:",
            placeholder='username',
            size='xs',
            ),
        dmc.PasswordInput(
            id=get_component_id('input_password'),
            placeholder="password",
            style={"width": 200},
            size='xs',
            label="新密码",
            ),
        dmc.Select(
            id=get_component_id('input_privilege'),
            label='权限',
            size='xs',
            creatable=True,
            style={"width": 200},
            data=PRIVILEGE['str_'].tolist(),
            value=PRIVILEGE['str_'].tolist()[-1]
            ),
        dmc.ActionIcon(
                id=get_component_id('icon_save'),
                size='sm',
                variant="subtle",
                disabled=True,
                children=DashIconify(icon="mdi:content-save", width=30),
                color='indigo'
            )
        ])

def create_table():
    return [
        dmc.ActionIcon(
            id=get_component_id('icon_refresh'),
            size='sm',
            variant="subtle",
            children=DashIconify(icon="mdi:refresh", width=30),
            color='indigo'
            ),
        dmc.Space(h='5px'),
        dmc.LoadingOverlay(
            dash_table.DataTable(
                id=get_component_id('datatable_user'),
                columns=[{'name': i, 'id': i} for i in TABLE_HEADERS],                           
                row_deletable=False,
                row_selectable=False,
                page_action='native',
                page_current= 0,
                page_size= 15,
                style_header = {'font-weight':'bold'},
                style_table = {'font-size':'small', 'overflowX': 'auto'},
                style_data={
                    'height': 'auto',
                    'lineHeight': '15px'
                    },                
                )  
            )
        ]

#%% layout
if __name__ == '__main__':     
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
dash.register_page(__name__)

layout = [
    html.Div(id=get_component_id('notification')),
    dmc.Container(
        size=cfg.CONTAINER_SIZE, 
        pt=cfg.HEADER_HEIGHT,
        children=[
            dmc.Space(h=30),
                dmc.Grid(
                align='flex-start',
                children=[
                    dmc.Col(span='content', children=creaet_controlers()),
                    dmc.Col(span=4, offset=1, children=create_table())
                    ]
                )
            ]
        ),
    ]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)

#%% callback
@callback(
    Output(get_component_id('icon_save'), 'disabled'),
    Input(get_component_id('input_username'), 'value'),
    Input(get_component_id('input_password'), 'value'),
    Input(get_component_id('input_privilege'), 'value'),
    )
def callback_disable_icon_update_administrate(username, password, input_privilege):
    return True if (username is None or username=='') or (password is None and input_privilege is None) else False

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_user'), 'data'),
    Input(get_component_id('icon_refresh'), 'n_clicks'),
    prevent_initial_call=True,
    )
def callback_on_icon_refresh_administrate(n):
    data, note = func_read_user_table()
    return note, data

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_user'), 'data', allow_duplicate=True),
    Output(get_component_id('input_password'), 'error'),
    Input(get_component_id('icon_save'), 'n_clicks'),
    State(get_component_id('input_username'), 'value'),
    State(get_component_id('input_password'), 'value'),
    State(get_component_id('input_privilege'), 'value'),
    prevent_initial_call=True,
    )
def callback_on_icon_save_administrate(n, username, password, privilege):    
    df, note = dcmpt.dash_dbquery(RSDBFacade.read_user)
    if note!=no_update:
        return note, no_update, ''
    privilege = PRIVILEGE.set_index('str_').loc[privilege, 'int_']
    hashed_password = generate_password_hash(password) if password is not None else None
    exist_user = RSDBFacade.read_user()['username'].tolist()
    # 修改用户信息
    is_updating = username in exist_user
    if is_updating:
        new_values = {'privilege':privilege}
        if password is not None:
            new_values.update({'password':hashed_password})
        _, note = dcmpt.dash_dbquery(
            RSDBFacade.update,
            tbname='user',
            new_values=new_values,
            eq_clause={'username':username}
            )
    # 新增用户
    else:
        if privilege is None:
            return no_update, no_update, '指定设置新用户密码'
        df = pd.DataFrame(
            {'username':username, 
            'password':hashed_password,
            'privilege':privilege},
            index=[0])
        _, note = dcmpt.dash_dbquery(
            RSDBFacade.insert,
            df=df,
            tbname='user',
            )        
    if note==no_update:
        data, note = func_read_user_table()
    if note==no_update:
        note = notification(
            title='操作成功',
            msg=f'用户{username}信息已更新' if is_updating else f'已添加用户{username}',
            _type='success'
            )
    return note, data, ''


#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)