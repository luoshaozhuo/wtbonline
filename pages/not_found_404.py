import dash
import dash_mantine_components as dmc
from dash_extensions import Lottie

dash.register_page(__name__, path="/404")

layout = dmc.Stack(
    align="center",
    children=[
        dmc.Space(h='50px'),
        Lottie(
            options=dict(loop=True, autoplay=True),
            isClickToPauseDisabled=True,
            url="/assets/404.json",
            width="40%",
        ),
        dmc.Text("If you think this page should exist, tontact the administrator."),
        dmc.Anchor("Go back to home ->", href="/", underline=False),
    ],
)
