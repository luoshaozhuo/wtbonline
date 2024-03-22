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

from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt
from wtbonline._db.rsdb.dao import RSDB

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='故障'
ITEM_ORDER = 2
PREFIX = 'analysis_fault'

GRAPH_CONF = cfg.GRAPH_CONF[cfg.GRAPH_CONF['item']==ITEM].set_index('clause')

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select_device_name(id=get_component_id('select_device_name')),
            dcmpt.select(id=get_component_id('select_fault_name'), data=[], value=None, label='故障类型'),
            dcmpt.select(id=get_component_id('select_item'), data=[], value=None, label='故障发生时间'),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_refresh'),
                leftIcon=DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="刷新图像",
                ),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_download'),
                leftIcon=DashIconify(icon="mdi:arrow-collapse-down", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="下载数据",
                color='green'
                ),
            dmc.Space(h='200px'), 
            ]
        )

def creat_toolbar():
    return dmc.Aside(
        fixed=True,
        width={'base': cfg.TOOLBAR_SIZE},
        position={"right": 0, 'top':cfg.HEADER_HEIGHT},
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
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)

dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout = [
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[creat_content()], size=cfg.CONTAINER_SIZE,pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ]

#%% callback
@callback(
    Output(get_component_id('select_device_name'), 'data'),
    Output(get_component_id('select_device_name'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_device_name_fault(set_id):
    if set_id in (None, ''):
        return [], None
    sr = RSDBFacade.read_statistics_fault(set_id=set_id)['device_id'].unique()
    device_names = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['device_id'].isin(sr)]['device_name']
    return [{'label':i, 'value':i} for i in device_names], None

@callback(
    Output(get_component_id('select_fault_name'), 'data'),
    Output(get_component_id('select_fault_name'), 'value'),
    Input(get_component_id('select_device_name'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_fault_name_fault(device_name):
    if device_name in (None, ''):
        return [], None
    device_id = cfg.WINDFARM_MODEL_DEVICE['device_id'][device_name]
    sr = RSDBFacade.read_statistics_fault(device_id=device_id)['fault_id'].unique()
    fault_types = cfg.WINDFARM_FAULT_TYPE['name'].loc[sr].unique()
    return [{'label':i, 'value':i} for i in fault_types], None

@callback(
    Output(get_component_id('select_item'), 'data'),
    Output(get_component_id('select_item'), 'value'),
    Input(get_component_id('select_fault_name'), 'value'),
    State(get_component_id('select_device_name'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_item_fault(fault_name, device_name):
    if fault_name in (None, ''):
        return [], None
    device_id = cfg.WINDFARM_MODEL_DEVICE['device_id'][device_name]
    fault_ids = cfg.WINDFARM_FAULT_TYPE[cfg.WINDFARM_FAULT_TYPE['name']==fault_name]['id'].astype(str)
    sql = (
        f'select id, start_time from statistics_fault '
        f'where device_id="{device_id}" and fault_id in ({",".join(fault_ids)}) ' 
        f'ORDER BY start_time desc '
        f'limit 15'
        )
    df = RSDB.read_sql(sql, 10)
    df['start_time'] = df['start_time'].astype(str)
    return [{'label':row['start_time'], 'value':row['id']} for _,row in df.iterrows()], None




# @callback(
#     Output(get_component_id('notification'), 'children', allow_duplicate=True),
#     Output(get_component_id('datepicker_date'), 'disabledDates'),
#     Output(get_component_id('datepicker_date'), 'minDate'),
#     Output(get_component_id('datepicker_date'), 'maxDate'),
#     Output(get_component_id('datepicker_date'), 'value'),
#     Input(get_component_id('select_device_name'), 'value'),
#     Input(get_component_id('select_type'), 'value'),
#     prevent_initial_call=True
#     )
# def callback_update_datepicker_date_fault(map_id, _type):
#     if None in (map_id, _type):
#         return no_update, no_update, no_update, no_update, None    
#     turbine_id = utils.interchage_device_name_and_tid(map_id=map_id)
#     df, note = utils.dash_try(
#         note_title = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL, 
#         func=RSDBFacade.read_statistics_fault, 
#         turbine_id=turbine_id if turbine_id is not None else '', 
#         fault_id=utils.get_fault_id(name=_type),
#         columns=['date']
#         )
#     if df is None:
#         return note, no_update, no_update, no_update
#     if len(df)>0:
#         availableDates = df['date'].squeeze()
#         minDate = availableDates.min()
#         maxDate = availableDates.max()
#         disabledDates = pd.date_range(minDate, maxDate)
#         disabledDates = disabledDates[~disabledDates.isin(availableDates)]
#         disabledDates = [i.date().isoformat() for i in disabledDates]
#     else:
#         minDate = cfg.DATE
#         maxDate = cfg.DATE
#         disabledDates = [cfg.DATE]
#     return no_update, disabledDates, minDate, maxDate, None

# @callback(
#     Output(get_component_id('btn_refresh'), 'disabled'), 
#     Input(get_component_id('datepicker_date'), 'value'),  
#     prevent_initial_call=True 
# )
# def callback_update_btn_resresh_fault(dt):
#     return True if dt is None else False

# @callback(
#     Output(get_component_id('notification'), 'children', allow_duplicate=True),
#     Output(get_component_id('graph'), 'figure'),
#     Input(get_component_id('btn_refresh'), 'n_clicks'),
#     State(get_component_id('select_setid'), 'value'),
#     State(get_component_id('select_device_name'), 'value'),
#     State(get_component_id('select_type'), 'value'),
#     State(get_component_id('datepicker_date'), 'value'),
#     prevent_initial_call=True
#     )
# def callback_on_btn_refresh_fault(n, set_id, map_id, _type, dt):
#     turbine_id = utils.interchage_device_name_and_tid(map_id)
#     df, note = utils.dash_dbquery( 
#         func=RSDBFacade.read_statistics_fault, 
#         turbine_id = turbine_id,
#         date = dt
#         )
#     if note is not None:
#         return note, no_update
#     dt = df['timestamp'].iloc[0]
#     delta = pd.Timedelta('10m')
#     target_df = dict(set_id=set_id, map_id=map_id, start_time=dt-delta, end_time=dt+delta)
#     graph = None
#     if len(target_df)>0:
#         graph, note = utils.dash_try(
#             note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,   
#             func=GRAPH_CONF.loc[_type]['class'], 
#             target_df=target_df,
#             title=_type
#             )
#     figure = no_update if graph is None else graph.figs[0]
#     return note, figure


#%% main
if __name__ == '__main__':     
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)