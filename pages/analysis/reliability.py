'''
作者：luosz
创建日期： 2024.02.21
描述：分析——故障
'''
#%% import
import dash
import dash_mantine_components as dmc
from dash import html
from functools import partial

from wtbonline._common import utils 

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='可靠性'
ITEM_ORDER = 5
PREFIX = 'analysis_reliability'

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component

#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout = [html.Div('comming soon')]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)

#%% callback

#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)