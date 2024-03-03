'''
作者：luosz
创建日期： 2024.02.21
描述：分析——故障
'''
#%% import
import dash
from dash import html
import dash_mantine_components as dmc
from functools import partial
from dash_extensions import Lottie

from wtbonline._common import utils

#%% constant
SECTION = '任务调度'
SECTION_ORDER = 4
ITEM='系统状态'
ITEM_ORDER = 2
PREFIX = 'scheduler_status'

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component

#%% layout
if __name__ == '__main__':     
    app = dash.Dash(__name__, assets_folder='../../assets', suppress_callback_exceptions=True)

dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout = dmc.Center(
    style={'height':'100vh'},
    children=dmc.Stack(
        align='center',
        children=[
            dmc.Text('我在哪里？', size='xs'),
            Lottie(
                options=dict(loop=True, autoplay=True),
                isClickToPauseDisabled=True,
                url="/assets/unavailable.json",
                height='100px',
                )
            ]
        )
    )


#%% callback

#%% main
if __name__ == '__main__':
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)