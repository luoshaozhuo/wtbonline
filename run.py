# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:24:08 2023

@author: luosz

首页
"""
# =============================================================================
# import
# =============================================================================
from dash import html, dcc, Input, Output, no_update
import dash_bootstrap_components as dbc
from flask_login import logout_user, current_user

from _pages import login, error_404, diagnose, analyse, explore, account, timed_task
from wtbonline import wtbonline

# =============================================================================
# layout
# =============================================================================
navbar_children = [
    dbc.NavItem(dbc.NavLink("探索", href="explore")),
    dbc.NavItem(dbc.NavLink("分析", href="analyse")),
    dbc.NavItem(dbc.NavLink("设计", href="design")),
    dbc.NavItem(dbc.NavLink("诊断", href="diagnose")),
    dbc.NavItem(dbc.NavLink("定时任务", href="timedtask")),
    dbc.NavItem(dbc.NavLink("账户管理", href="account")),
    dbc.NavItem(dbc.NavLink("退出登录", id='run_logout', href="#")),
    ]

navbar = dbc.NavbarSimple(
    children=navbar_children,
    brand = dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/logo.jpg', height="30px")),
                        dbc.Col(dbc.NavbarBrand("数据分析系统", className="ms-2 fs-6")),
                    ],
                    align="center",
                    className="px-3",
                ),
    color="primary",
    fluid=True,
    dark=True,
    id='navBar',
    class_name='p-1',
    style={'font-size':'small'},
    fixed='top'
)

layout = html.Div(
    [
     dcc.Location(id='run_location', refresh=False),
     navbar,
     html.Div(
             id='run_page',
             className='mt-5 h-100 w-100',
             )
     ],
    className='position-absolute vw-100 vh-100 vstack'
    )


# =============================================================================
# callback
# =============================================================================
@wtbonline.callback(Output('run_page', 'children'),
              Output('run_location', 'pathname'),
              Output('navBar', 'children'),
              [Input('run_location', 'pathname')])
def show_Page(pathname):
    if pathname == '/login' or not current_user.is_authenticated:
        return login.get_layout(), '/login', ''
 
    if pathname in ('/', '/diagnose'):
        return diagnose.get_layout(), no_update, navbar_children
    elif pathname == '/analyse':
        return analyse.get_layout(), no_update, navbar_children
    elif pathname == '/explore':
        return explore.get_layout(), no_update, navbar_children
    elif pathname == '/account':
        return account.get_layout(), no_update, navbar_children
    elif pathname == '/timedtask':
        return timed_task.get_layout(), no_update, navbar_children
    
    return error_404.get_layout(), no_update, ''    

@wtbonline.callback(
    Output('run_location', 'pathname', allow_duplicate=True),
    Input('run_logout', 'n_clicks'),
    prevent_initial_call=True,
    )
def on_run_logout(nclick):
    if nclick:
        logout_user()
        return '/login'
    else: 
        return no_update


# =============================================================================
# main
# =============================================================================
wtbonline.layout = layout
server = wtbonline.server

def main():
    import sys
    debug = True if len(sys.argv)>1 else False
    wtbonline.run_server(debug=debug)    

if __name__ == '__main__':
    main()