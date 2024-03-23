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
from matplotlib.style import available
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._plot import graph_factory
from wtbonline._db.tsdb_facade import TDFC

import time

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
            dcmpt.select(id=get_component_id('select_device_id'), data=[], value=None, label='风机编号', description='只显示有故障记录的机组'),
            dcmpt.select(id=get_component_id('select_fault_name'), data=[], value=None, label='故障类型', description='只显示存在故障记录的类型'),
            dcmpt.select(id=get_component_id('select_item'), data=[], value=None, label='故障发生时间', description='只显示最新15个'),
            dcmpt.multiselecdt_var_name(id=get_component_id('select_var_name')),
            dmc.Space(h='20px'),
            dmc.LoadingOverlay(
                loaderProps={"size": "sm"},
                children=[
                    dmc.Button(
                        fullWidth=True,
                        disabled=True,
                        id=get_component_id('btn_refresh'),
                        leftIcon=DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH),
                        size=cfg.TOOLBAR_COMPONENT_SIZE,
                        children="刷新图像",
                        ),
                    dmc.Space(h='20px'),
                    dcc.Download(id=get_component_id('download_dataframe')),
                    dmc.Button(
                        fullWidth=True,
                        disabled=True,
                        id=get_component_id('btn_download'),
                        leftIcon=DashIconify(icon="mdi:arrow-collapse-down", width=cfg.TOOLBAR_ICON_WIDTH),
                        size=cfg.TOOLBAR_COMPONENT_SIZE,
                        children="下载数据",
                        color='green'
                        ),
                    ]  
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
    Output(get_component_id('notification'), 'children'),
    Output(get_component_id('select_device_id'), 'data'),
    Output(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    )
def callback_update_select_device_name_fault(set_id):
    if set_id in (None, ''):
        return no_update, [], None
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        set_id=set_id,
        )
    if note is None:
        sr = df['device_id'].unique()
        df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['device_id'].isin(sr)]
        data = [{'label':row['device_name'], 'value':row['device_id']} for _,row in df.iterrows()]
    else:
        data = []
    return note, data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_fault_name'), 'data'),
    Output(get_component_id('select_fault_name'), 'value'),
    Input(get_component_id('select_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_fault_name_fault(device_id):
    if device_id in (None, ''):
        return no_update, [], None
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        device_id=device_id,
        )
    if note is None:
        sr = df['fault_id'].unique()
        fault_types = cfg.WINDFARM_FAULT_TYPE['name'].loc[sr].unique()
        data = [{'label':i, 'value':i} for i in fault_types]
    else:
        data = []
    return note, data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_item'), 'data'),
    Output(get_component_id('select_item'), 'value'),
    Input(get_component_id('select_fault_name'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_item_fault(fault_name, device_id):
    if fault_name in (None, ''):
        return no_update, [], None
    fault_ids = cfg.WINDFARM_FAULT_TYPE[cfg.WINDFARM_FAULT_TYPE['name']==fault_name]['id'].astype(str)
    sql = (
        f'select id, start_time from statistics_fault '
        f'where device_id="{device_id}" and fault_id in ({",".join(fault_ids)}) ' 
        f'ORDER BY start_time desc '
        f'limit 15'
        )
    df, note = dcmpt.dash_dbquery(
        func=RSDB.read_sql,
        stmt=sql,
        )
    if note is None:
        df['start_time'] = df['start_time'].astype(str)
        data = [{'label':row['start_time'], 'value':row['id']} for _,row in df.iterrows()]
    else:
        data = []
    return note, data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_var_name'), 'disabled'),
    Output(get_component_id('select_var_name'), 'data'),
    Output(get_component_id('select_var_name'), 'value'),
    Input(get_component_id('select_item'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_var_name_fault(id_, set_id):
    note = no_update
    disabled = True
    data = []
    value = None
    if id_ in (None, ''):
        return no_update, disabled, data, value
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        id_=id_
        )
    if note is None:
        sr = df.squeeze()
        type_sr = cfg.WINDFARM_FAULT_TYPE.loc[sr['fault_id'], :]
        if type_sr['graph']=='ordinary':
            df = cfg.WINDFARM_VAR_NAME[cfg.WINDFARM_VAR_NAME['set_id']==set_id]
            data = [{'label':row['point_name'], 'value':row['var_name']} for _,row in df.iterrows()]
            value = pd.Series(type_sr['var_names'].split(','))
            value = value[value.isin(df['var_name'])].tolist()
            disabled = False
        else:
            data = []
            value = None
            disabled = True
    return note, disabled, data, value

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('btn_refresh'), 'disabled'),
    Output(get_component_id('btn_download'), 'disabled'),
    Input(get_component_id('select_item'), 'value'), 
    Input(get_component_id('select_var_name'), 'value'), 
    prevent_initial_call=True
    )
def callback_disable_btns_fault(id_, var_names):
    note = no_update
    btn_refresh = True
    btn_download = True
    if id_ in (None, ''):
        return note, btn_refresh, btn_download
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        id_=id_
        )
    if note is None:
        btn_download = False
        btn_refresh = False
        sr = df.squeeze()
        type_sr = cfg.WINDFARM_FAULT_TYPE.loc[sr['fault_id'], :]
        if type_sr['graph']=='ordinary' and (var_names in (None, '') or len(var_names)<1):
            btn_refresh = True
    return note, btn_refresh, btn_download

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_item'), 'value'),
    State(get_component_id('select_var_name'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_fault(n, set_id, device_id, sample_id, var_names):
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        id_=sample_id
        )
    if note is not None:
        return note, {}
    sample_sr = df.iloc[0]
    fault_type_sr = cfg.WINDFARM_FAULT_TYPE.loc[sample_sr['fault_id']]
    grapp_name = fault_type_sr['graph']
    graph_obj = graph_factory(fault_type_sr['graph'])()
    if grapp_name=='ordinary':
        graph_obj.init(var_names=var_names)
    delta = pd.Timedelta(f'{fault_type_sr["time_span"]}m')
    fig, note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL, 
        func=graph_obj.plot,
        set_id=set_id,
        device_ids=device_id,
        start_time=sample_sr['start_time']-delta, 
        end_time=sample_sr['end_time']+delta,
        title=fault_type_sr['name']
        )
    return note, fig

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('download_dataframe'), 'data'),
    Input(get_component_id('btn_download'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_item'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_download_fault(n, set_id, device_id, sample_id):
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_fault,
        id_=sample_id
        )
    if note is not None:
        return note, no_update
    sample_sr = df.iloc[0]
    fault_type_sr = cfg.WINDFARM_FAULT_TYPE.loc[sample_sr['fault_id']]
    delta = pd.Timedelta(f'{fault_type_sr["time_span"]}m')
    columns = pd.Series(fault_type_sr['var_names'].split(','))
    available_cols = cfg.WINDFARM_VAR_NAME[cfg.WINDFARM_VAR_NAME['set_id']==set_id]['var_name']
    columns = columns[columns.isin(available_cols)]
    df, note = dcmpt.dash_dbquery(
        func=TDFC.read,
        set_id=set_id, 
        device_id=device_id,
        start_time=sample_sr['start_time']-delta, 
        end_time=sample_sr['end_time']+delta,
        columns=fault_type_sr['var_names'].split(','),
        remote=True    
        )
    data = dcc.send_data_frame(df.to_csv, "mydf.csv") if note is None else no_update
    return note, data

#%% main
if __name__ == '__main__':     
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)