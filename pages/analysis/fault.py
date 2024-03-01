'''
作者：luosz
创建日期： 2024.02.21
描述：分析——故障
'''
#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='故障'
ITEM_ORDER = 2
PREFIX = 'analysis_fault'

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

CONTAINER_SIZE = cfg.CONTAINER_SIZE

NOW = cfg.NOW
DATE = cfg.DATE
TIME_START = cfg.TIME_START
TIME_END = cfg.TIME_END

GRAPH_PADDING_TOP = cfg.GRAPH_PADDING_TOP
GRAPH_CONF = cfg.GRAPH_CONF[cfg.GRAPH_CONF['item']==ITEM].set_index('clause')
NOTIFICATION_TITLE_DBQUERY = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH_FAIL

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=TOOLBAR_PADDING, 
        children=[
            dcmpt.select_analysis_type(id=get_component_id('select_type'), data=list(GRAPH_CONF.index), label='故障类型'),
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select_mapid(id=get_component_id('select_mapid')),
            dcmpt.date_picker(id=get_component_id('datepicker_date'), label="开始日期", description="可选日期取决于否存在选定故障"),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_refresh'),
                leftIcon=DashIconify(icon="mdi:refresh", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="刷新图像",
                ), 
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
    return  dmc.LoadingOverlay(       
            dcc.Graph(
                id=get_component_id('graph'),
                config={'displaylogo':False},
                )
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
    dmc.Container(children=[creat_content()], size=CONTAINER_SIZE,pt=HEADER_HEIGHT),
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
    Output(get_component_id('select_mapid'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_fault(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_date'), 'disabledDates'),
    Output(get_component_id('datepicker_date'), 'minDate'),
    Output(get_component_id('datepicker_date'), 'maxDate'),
    Output(get_component_id('datepicker_date'), 'value'),
    Input(get_component_id('select_mapid'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_date_fault(map_id, _type):
    if None in (map_id, _type):
        return no_update, no_update, no_update, no_update, None    
    turbine_id = utils.interchage_mapid_and_tid(map_id=map_id)
    df, note = utils.dash_try(
        note_title = NOTIFICATION_TITLE_DBQUERY, 
        func=RSDBInterface.read_statistics_fault, 
        turbine_id=turbine_id if turbine_id is not None else '', 
        fault_id=utils.get_fault_id(name=_type),
        columns=['date']
        )
    if df is None:
        return note, no_update, no_update, no_update
    if len(df)>0:
        availableDates = df['date'].squeeze()
        minDate = availableDates.min()
        maxDate = availableDates.max()
        disabledDates = pd.date_range(minDate, maxDate)
        disabledDates = disabledDates[~disabledDates.isin(availableDates)]
        disabledDates = [i.date().isoformat() for i in disabledDates]
    else:
        minDate = DATE
        maxDate = DATE
        disabledDates = [DATE]
    return no_update, disabledDates, minDate, maxDate, None

@callback(
    Output(get_component_id('btn_refresh'), 'disabled'), 
    Input(get_component_id('datepicker_date'), 'value'),  
    prevent_initial_call=True 
)
def callback_update_btn_resresh_fault(dt):
    return True if dt is None else False

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_type'), 'value'),
    State(get_component_id('datepicker_date'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_fault(n, set_id, map_id, _type, dt):
    turbine_id = utils.interchage_mapid_and_tid(map_id)
    df, note = utils.dash_dbquery( 
        func=RSDBInterface.read_statistics_fault, 
        turbine_id = turbine_id,
        date = dt
        )
    if note!=no_update:
        return note, no_update
    dt = df['timestamp'].iloc[0]
    delta = pd.Timedelta('10m')
    target_df = dict(set_id=set_id, map_id=map_id, start_time=dt-delta, end_time=dt+delta)
    graph = None
    if len(target_df)>0:
        graph, note = utils.dash_try(
            note_title=NOTIFICATION_TITLE_GRAPH,   
            func=GRAPH_CONF.loc[_type]['class'], 
            target_df = target_df,
            title = _type
            )
    figure = no_update if graph is None else graph.figs[0]
    return note, figure


#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)