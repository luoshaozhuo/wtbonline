'''
作者：luosz
创建日期： 2024.02.21
描述：分析——故障
'''
#%% import
import dash
import dash_mantine_components as dmc

from functools import partial
from dash_extensions import Lottie

import wtbonline._common.dash_component as dcmpt 

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='可靠性'
ITEM_ORDER = 5
PREFIX = 'analysis_reliability'

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

#%% component

#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)

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