
import dash_mantine_components as dmc
from dash_iconify import DashIconify

SUCCESS = 0
FAILED = 1 

def get_notification(prefix:str, _type:int, message:str):
    if _type==SUCCESS:
        autoClose = 1500
        color = 'green'
        title = 'success'
        icon=DashIconify(icon="akar-icons:circle-check")
    elif _type==FAILED:
        autoClose = False
        color = 'red'
        title = 'failed'
        icon=DashIconify(icon="ic:twotone-warning-amber")
    return dmc.Notification(
            id=f'{prefix}_notification',
            title=title,
            action="show",
            message=message,
            icon=icon,
            color=color,
            autoClose=autoClose
        )