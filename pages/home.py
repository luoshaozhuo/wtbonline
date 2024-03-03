# -*- coding: utf-8 -*-
#%% import
import dash
from dash import html
import dash_mantine_components as dmc
from functools import partial
from dash_extensions import Lottie

from wtbonline._common import utils


#%% constant
PREFIX = 'home'

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component

#%% layout
if __name__ == '__main__':     
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)

dash.register_page(__name__,  path="/", title="Winturbine Data Assistant System")

layout = dmc.Center(
    style={'height':'100vh'},
    children=dmc.Stack(
        align='center',
        children=[
            html.Div(
                dmc.Image(
                    src="/assets/logo_home.png",
                    height=50,
                    radius=0,
                    )
                ),
            dmc.Space(h='30px'),
            dmc.Text("Hi，我是你的数据助理~", size='sm'),
            dmc.Group(
                align='end',
                children=[
                Lottie(
                    options=dict(loop=True, autoplay=True),
                    isClickToPauseDisabled=True,
                    url="/assets/home.json",
                    height='50px',
                    ),  
                dmc.Title("Powered by 恩德新能源", order=6),           
                ])
            ]
        )
    )

#%% callback

#%% main
if __name__ == '__main__':
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)