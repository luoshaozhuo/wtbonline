'''
作者：luosz
创建日期： 2024.02.18
描述：探索--二维图
    1、时序图
    2、散点图
    3、极坐标图
    4、频谱图
'''

#%% import
from tkinter import N
import dash
import dash_mantine_components as dmc
from dash import dcc, html, dash_table
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._plot.functions import scatter_matrix_anormaly
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '识别'
SECTION_ORDER = 1
ITEM='异常状态'
ITEM_ORDER = 1
PREFIX =  'recognize_anomaly'

HEADER_HEIGHT = cfg.HEADER_HEIGHT

TOOLBAR_SIZE = cfg.TOOLBAR_SIZE
TOOLBAR_PADDING = cfg.TOOLBAR_PADDING
TOOLBAR_TOGGLE_SIZE = cfg.TOOLBAR_TOGGLE_SIZE
TOOLBAR_TOGGLE_ICON_WIDTH = cfg.TOOLBAR_TOGGLE_ICON_WIDTH
TOOLBAR_TOGGLE_POS_TOP = cfg.TOOLBAR_TOGGLE_POS_TOP
TOOLBAR_TOGGLE_POS_RIGHT = cfg.TOOLBAR_TOGGLE_POS_RIGHT
TOOLBAR_COMPONENT_SIZE = cfg.TOOLBAR_COMPONENT_SIZE
TOOLBAR_ICON_WIDTH = cfg.TOOLBAR_ICON_WIDTH
TOOLBAR_COMPONENT_WIDTH = cfg.TOOLBAR_COMPONENT_WIDTH
TOOLBAR_FONT_SIZE = cfg.TOOLBAR_FONT_SIZE
TOOLBAR_HIDE_SMALLER_THAN =  cfg.TOOLBAR_HIDE_SMALLER_THAN
TOOLBAR_ICON_COLOR = cfg.TOOLBAR_ICON_COLOR

CONTAINER_SIZE = cfg.CONTAINER_SIZE

NOW = cfg.NOW
DATE = cfg.DATE
TIME_START = cfg.TIME_START
TIME_END = cfg.TIME_END

GRAPH_PADDING_TOP = cfg.GRAPH_PADDING_TOP
DBQUERY_FAIL = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL
DBQUERY_NODATA = cfg.NOTIFICATION_TITLE_DBQUERY_NODATA
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH_FAIL

TABLE_COLUMNS = cfg.TOOLBAR_TABLE_COLUMNS
TABLE_FONT_SIZE = cfg.TOOLBAR_TABLE_FONT_SIZE
TABLE_HEIGHT = cfg.TOOLBAR_TABLE_HEIGHT

SELECT_STATUS = [{'label':i, 'value':i} for i in ['未标注', '异常', '正常']]
SCATTER_PLOT_SAMPLE_NUM = 10000
SCATTER_PLOT_VARIABLES = tuple([
    'var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean',
    'var_382_mean', 'var_383_mean'
    ])
#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=TOOLBAR_PADDING, 
        children=[   
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select_mapid(id=get_component_id('select_mapid')),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_next'),
                rightIcon=DashIconify(icon="mdi:navigate-next", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="下一条样本",
                ), 
            dmc.Space(h='10px'),
            dmc.LoadingOverlay(dmc.List(
                size="xs",
                spacing="xs",
                children=[
                    dmc.ListItem(
                        id=get_component_id('listItem_ts'),
                        icon=DashIconify(
                            icon="mdi:clock-time-four-outline",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_wspd'),
                        icon = DashIconify(
                            icon="mdi:windsock",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_rspd'),
                        icon = DashIconify(
                            icon="mdi:axis",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_power'),
                        icon = DashIconify(
                            icon="mdi:thunder-outline",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_pitchAngle'),
                        icon = DashIconify(
                            icon="mdi:angle-acute",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    ],
                )),
            dmc.Space(h='10px'),
            dcmpt.select(id=get_component_id('select_status'), data=SELECT_STATUS, value=None, label='状态标注', description='标注当前十分钟数据样本状态'),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_update'),
                leftIcon=DashIconify(icon="mdi:file-document-edit-outline", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="更新样本标注",
                ), 
            dmc.Space(h='100px'),
            ]
        )

def creat_toolbar():
    return dmc.Aside(
        fixed=True,
        width={'base': TOOLBAR_SIZE},
        position={"right": 0, 'top':HEADER_HEIGHT},
        zIndex=2,
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=create_toolbar_content(),
                )
            ],
        )

def creat_content():
    return  dmc.Grid(
        gutter="xs",
        children=[
            dmc.Col(
                lg=8,
                md=12,
                children=
                dmc.LoadingOverlay(dcc.Graph(
                    id=get_component_id('graph_scatter'),
                    config={'displaylogo':False},
                    )
                    )),
            dmc.Col(
                lg=4,
                md=12,
                children=dmc.Stack(
                    spacing='xs',
                    children=[
                        dmc.LoadingOverlay(dcc.Graph(
                            id=get_component_id('graph_line'),
                            config={'displaylogo':False},
                            )),
                        
                        dmc.LoadingOverlay(dcc.Graph(
                            id=get_component_id('graph_spectrum'),
                            config={'displaylogo':False},
                            )),
                        ]
                    ),  
                )
            ]
        )
    

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

layout = [
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[creat_content()], size=CONTAINER_SIZE, pt=HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )   
    ]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)


#%% callback
@callback(
    Output(get_component_id('select_mapid'), 'data'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_anomaly(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data

@callback(
    Output(get_component_id('btn_next'), 'disabled'),
    Input(get_component_id('select_mapid'), 'value'),
    )
def callback_disable_btn_next_anomaly(map_id): 
    return False if map_id is not None else True

@callback(
    Output(get_component_id('btn_update'), 'disabled'),
    Input(get_component_id('select_status'), 'value'),
    )
def callback_disable_btn_update_anomaly(map_id): 
    return False if map_id is not None else True

@callback(
    Output(get_component_id('notification'), 'children'),
    Output(get_component_id('graph_scatter'), 'figure'),
    Output(get_component_id('graph_line'), 'figure'),
    Output(get_component_id('graph_spectrum'), 'figure'),
    Output(get_component_id('listItem_ts'), 'children'),
    Output(get_component_id('listItem_wspd'), 'children'),
    Output(get_component_id('listItem_rspd'), 'children'),
    Output(get_component_id('listItem_power'), 'children'),
    Output(get_component_id('listItem_pitchAngle'), 'children'),
    Input(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_mapid_anomaly(map_id, set_id):
    '''
    map_id改变时，切换散点图，清空时序图、频谱图及样本信息
    '''
    graph_scatter = no_update
    df, note = utils.dash_try(
        note_title='读取异常数据失败',
        func=utils.read_scatter_matrix_anormaly,
        set_id=set_id,
        map_id=map_id,
        columns=SCATTER_PLOT_VARIABLES
        )
    if note==no_update:
        graph_scatter, note = utils.dash_try(
        note_title='绘图失败',
        func=scatter_matrix_anormaly,
        df=df,
        columns=SCATTER_PLOT_VARIABLES,
        set_id=set_id
        )
    return no_update, graph_scatter, *[None]*2, *['-']*5

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_line'), 'figure', allow_duplicate=True),
    Output(get_component_id('graph_spectrum'), 'figure', allow_duplicate=True),
    Output(get_component_id('listItem_ts'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_wspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_rspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_power'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_pitchAngle'), 'children', allow_duplicate=True),
    Input(get_component_id('select_next'), 'n_clicks'),
    prevent_initial_call=True
    )
def callback_on_btn_next_anomaly(n):
    '''
    点击next时，清空时序图、频谱图，更新样本信息
    '''
    note = no_update
    graph_line = None
    graph_spectrum = None
    ts = no_update
    wspd = no_update
    rspd = no_update
    power = no_update
    pitchAngle = no_update
    return note, graph_line, graph_spectrum, ts, wspd, rspd, power, pitchAngle

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_scatter'), 'figure', allow_duplicate=True),
    Input(get_component_id('select_mapid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_update_anomaly(n):
    '''
    点击update时，更新散点图及后台数据
    '''
    fig = no_update
    return no_update, fig


#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)