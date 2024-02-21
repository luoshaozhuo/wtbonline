'''
作者：luosz
创建日期： 2024.02.18
描述：分析——故障
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
    section='分析',
    section_order=2,
    item='故障',
    item_order=2,
    )

layout = html.Div(
    children='分析-故障'
    )

#%% callback