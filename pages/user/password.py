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
from dash import Output, Input, html,  callback, no_update, State
from functools import partial
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from wtbonline._db.rsdb_facade import RSDBFC
import wtbonline.configure as cfg
import wtbonline._common.dash_component as dcmpt
from wtbonline._common.dash_component import notification

#%% constant
PREFIX = 'user_password'

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

#%% component

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
        children=dmc.Grid(dmc.Col(
            span=4,
            children=[
                dmc.Space(h=30),
                dmc.PasswordInput(
                    id=get_component_id('input_oldPassword'),
                    label="旧密码",
                    placeholder="password",
                    style={"width": 200},
                    size='xs',
                    withAsterisk=True
                    ),
                dmc.PasswordInput(
                    id=get_component_id('input_newPassword'),
                    label="新密码",
                    placeholder="password",
                    style={"width": 200},
                    size='xs',
                    withAsterisk=True
                    ),
                dmc.Space(h=30),
                dmc.Button("提交", id=get_component_id("btn_submit"), size='xs'),
                ]
            ))
        )
    ]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)


#%% callback
@callback(
    Output(get_component_id("notification"), 'children'),
    Output(get_component_id("input_oldPassword"), 'error'),
    Output(get_component_id("input_newPassword"), 'error'),
    Input(get_component_id("btn_submit"), 'n_clicks'),
    State(get_component_id("input_oldPassword"), 'value'),
    State(get_component_id("input_newPassword"), 'value'),
    prevent_initial_call=True,
    )
def callback_on_btn_submit_pasword(n, oldPassword, newPassword):
    username, note = dcmpt.dash_get_username(current_user, __name__=='__main__')
    error_oldPassword = error_newPassword = ''
    for _ in range(1):
        # 无法获取用户名
        if note is not None:
            break
        # 缺输入
        if None in (oldPassword, newPassword) or '' in (oldPassword, newPassword):
            error_oldPassword = '输入旧密码' if oldPassword in (None, '') else ''
            error_newPassword = '输入新密码' if oldPassword in (None, '') else ''
            break
        # 旧密码错误
        this_user = RSDBFC.read_user(username=username).squeeze()
        if not check_password_hash(this_user.password, oldPassword):
            error_oldPassword = '旧密码错误'
            break
        # 更新密码
        newPassword = generate_password_hash(newPassword)
        _, note = dcmpt.dash_dbquery(
                RSDBFC.update,
                tbname='user',
                new_values={'password':newPassword}, 
                eq_clause={'username':this_user.username}
            )
        if note is None:
            note = notification(
                title='密码已修改',
                msg=f'{this_user.username}密码修改成功',
                _type='success'
                )
    return note, error_oldPassword, error_newPassword

#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)