'''
作者：luosz
创建日期： 2024.02.17
最后修改日期： 2024.02.17
描述：分析页面
'''

#%% import
import dash
import dash_mantine_components as dmc
import requests
from dash import dcc, html
from dash_iconify import DashIconify

#%% constant

#%% function

#%% layout
dash.register_page(
    __name__,
    section='调度',
    section_order=3,
    item='后台任务',
    item_order=1,
    )

layout = html.Div(
    children='调度-定时任务'
    )

#%% callback