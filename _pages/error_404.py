# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 19:51:13 2023

@author: luosz

404页面
"""

from dash import html
import dash_bootstrap_components as dbc

def get_layout():
    layout = dbc.Container([
        html.Br(),
        html.H1('Error-404: Page not found')
        ])
    return layout
