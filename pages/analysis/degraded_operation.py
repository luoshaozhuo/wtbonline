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

from wtbonline._db.rsdb_facade import RSDBFC
import wtbonline.configure as cfg
from wtbonline._common import dash_component as dcmpt
from wtbonline._db.rsdb.dao import RSDB
from wtbonline._plot import graph_factory
from wtbonline._db.tsdb_facade import TDFC

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='降容'
ITEM_ORDER = 2
PREFIX = 'analysis_dg'

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

FAULT_TYPE = cfg.WINDFARM_FAULT_TYPE.dropna(subset=['var_names', 'index', 'value'])
FAULT_TYPE = FAULT_TYPE[FAULT_TYPE['name']=='机组降容']

MAX_VALUES = 10 # 最大可选择的变量数

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

def load_figure(sample_id, var_names):
    df, note = dcmpt.dash_dbquery(
        func=RSDBFC.read_statistics_fault,
        id_=sample_id
        )
    if note is not None:
        return {}, note
    sample_sr = df.iloc[0]
    fault_type_sr = cfg.WINDFARM_FAULT_TYPE.loc[sample_sr['fault_id']]
    grapp_name = fault_type_sr['graph']
    graph_obj = graph_factory.get(grapp_name)(row_height=300)
    if grapp_name=='ordinary':
        graph_obj.init(var_names=var_names)
    delta = pd.Timedelta(f"{max(int(fault_type_sr['time_span']), 1)}m")
    fig, note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA, 
        func = graph_obj.plot,
        set_id=sample_sr['set_id'],
        device_ids=sample_sr['device_id'],
        start_time=sample_sr['start_time']-delta, 
        end_time=sample_sr['end_time']+delta,
        title=fault_type_sr['name']+'_'+fault_type_sr['cause'],
        )
    fig = {} if fig is None else fig
    return fig, note


#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.date_picker(
                id=get_component_id('datepicker_end'), 
                label="结束日期", 
                disabled=False, 
                maxDate=pd.Timestamp.now().date(), 
                value=pd.Timestamp.now().date(), 
                description="日期范围是闭区间"
                ),
            dcmpt.number_input(id=get_component_id('input_span'), label='时长', value=30, min=1, description='单位，天'),
            dcmpt.select(id=get_component_id('select_device_id'), data=[], value=None, label='风机编号', description='只显示有记录的机组'),
            dcmpt.select(id=get_component_id('select_fault_cause'), data=[], value=None, label='降容原因', description='只显示存在记录的类型'),
            dcmpt.select(id=get_component_id('select_itemid'), data=[], value=None, label='降容记录', description='按开始时间降序排列'),
            dcmpt.multiselecdt_var_name(id=get_component_id('select_var_name'), label='选择绘图变量', maxSelectedValues=MAX_VALUES),
            dmc.Space(h='20px'),
            dmc.LoadingOverlay(
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
                        id=get_component_id('btn_download_tdengine'),
                        leftIcon=DashIconify(icon="mdi:arrow-collapse-down", width=cfg.TOOLBAR_ICON_WIDTH),
                        size=cfg.TOOLBAR_COMPONENT_SIZE,
                        children="下载tdengine数据",
                        color='green'
                        ),
                    dmc.Space(h='20px'),
                    dmc.Button(
                        fullWidth=True,
                        disabled=True,
                        id=get_component_id('btn_download_plc'),
                        leftIcon=DashIconify(icon="mdi:arrow-collapse-down", width=cfg.TOOLBAR_ICON_WIDTH),
                        size=cfg.TOOLBAR_COMPONENT_SIZE,
                        children="下载plc数据",
                        color='green'
                        ),
                    ],
                loaderProps={"size": "sm"},
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
    dmc.Container(children=[dmc.Space(h='20px'), creat_content()], size=cfg.CONTAINER_SIZE,pt=cfg.HEADER_HEIGHT),
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
    Input(get_component_id('datepicker_end'), 'value'),
    Input(get_component_id('input_span'), 'value'),
    )
def callback_update_select_device_id_dg(set_id, end_date, delta):
    if pd.Series([set_id, end_date, delta]).isin([None, '']).any():
        return None, [], None
    end_time = pd.to_datetime(end_date)
    start_time = end_time - pd.Timedelta(f'{delta}d')
    fault_ids = ",".join(FAULT_TYPE["id"].astype(str))
    sql = (
        f'select distinct device_id from statistics_fault '
        f'where set_id={set_id} and start_time>="{start_time}" and start_time<="{end_time}" and fault_id in ({fault_ids})' 
        )
    df, note = dcmpt.dash_dbquery(
        func=RSDB.read_sql,
        stmt=sql,
        )
    if note is None:
        sub_df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['device_id'].isin(df['device_id'])]
        device_data = [{'label':row['device_name'], 'value':row['device_id']} for _,row in sub_df.iterrows()]
    else:
        device_data = []
    return note, device_data, None    

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_fault_cause'), 'data'),
    Output(get_component_id('select_fault_cause'), 'value'),
    Input(get_component_id('select_device_id'), 'value'),
    State(get_component_id('datepicker_end'), 'value'),
    State(get_component_id('input_span'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_id_dg(device_id, end_date, delta):
    if device_id in (None, ''):
        return no_update, [], None
    end_time = pd.to_datetime(end_date)
    start_time = end_time - pd.Timedelta(f'{delta}d')
    fault_ids = ",".join(FAULT_TYPE["id"].astype(str))
    sql = (
        f'select distinct fault_id from statistics_fault '
        f'where device_id="{device_id}" and start_time>="{start_time}" and start_time<="{end_time}" and fault_id in ({fault_ids})' 
        )
    df, note = dcmpt.dash_dbquery(
        func=RSDB.read_sql,
        stmt=sql,
        )
    if note is None:
        sr = df['fault_id'].unique()
        fault_types = FAULT_TYPE[FAULT_TYPE['id'].isin(sr)]['cause'].unique()
        data = [{'label':i, 'value':i} for i in fault_types]
    else:
        data = []
    return note, data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_itemid'), 'data'),
    Output(get_component_id('select_itemid'), 'value'),
    Input(get_component_id('select_fault_cause'), 'value'),
    State(get_component_id('datepicker_end'), 'value'),
    State(get_component_id('input_span'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_fault_cause_dg(fault_name, end_date, delta, device_id):
    if fault_name in (None, ''):
        return no_update, [], None
    fault_ids = FAULT_TYPE[FAULT_TYPE['cause']==fault_name]['id'].astype(str)
    end_time = pd.to_datetime(end_date)
    start_time = end_time - pd.Timedelta(f'{delta}d')
    sql = (
        f'select id, start_time from statistics_fault '
        f'where device_id="{device_id}" and start_time>="{start_time}" and start_time<="{end_time}" and fault_id in ({",".join(fault_ids)})' 
        f'ORDER BY start_time desc '
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
    Input(get_component_id('select_itemid'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_itemid_dg(id_, set_id):
    note = no_update
    disabled = True
    data = []
    value = None
    if id_ in (None, ''):
        return no_update, disabled, data, value
    df, note = dcmpt.dash_dbquery(
        func=RSDBFC.read_statistics_fault,
        id_=id_
        )
    if note is None:
        sr = df.squeeze()
        type_sr = FAULT_TYPE.loc[sr['fault_id'], :]
        if type_sr['graph']=='ordinary':
            df = cfg.WINDFARM_VAR_NAME[cfg.WINDFARM_VAR_NAME['set_id']==set_id]
            df = df[df['var_name'].isin(TDFC.get_filed(set_id=set_id, remote=True))]
            data = [{'label':row['point_name'], 'value':row['var_name']} for _,row in df.iterrows()]
            value = pd.Series(type_sr['var_names'].split(','))
            value = value[value.isin(df['var_name'])].head(MAX_VALUES).tolist()
            disabled = False
        else:
            data = []
            value = None
            disabled = True
    return note, disabled, data, value

@callback(
    Output(get_component_id('btn_refresh'), 'disabled'),
    Output(get_component_id('btn_download_tdengine'), 'disabled'),
    Output(get_component_id('btn_download_plc'), 'disabled'),
    Input(get_component_id('select_itemid'), 'value'), 
    Input(get_component_id('select_var_name'), 'value'),
    prevent_initial_call=True
    )
def callback_disable_btns_dg(v1, v2):
    disabled = pd.Series([v1, v2]).isin([None, '', []]).any()
    return [disabled]*3

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('select_itemid'), 'value'), 
    State(get_component_id('select_var_name'), 'value'), 
    prevent_initial_call=True
    )
def callback_on_btn_refresh_dg(n, sample_id, var_names):
    if sample_id in (None, ''):
        return None, {}
    figure, note = load_figure(sample_id, var_names)
    return note, figure

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('download_dataframe'), 'data'),
    Input(get_component_id('btn_download_tdengine'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_itemid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_download_tdengine_dg(n, set_id, device_id, sample_id):
    df, note = dcmpt.dash_dbquery(
        func=RSDBFC.read_statistics_fault,
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
    now = pd.Timestamp.now().strftime('%y%m%d%H%M%S')
    data = dcc.send_data_frame(df.to_csv, f"data{now}.csv") if note is None else no_update
    return note, data

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('download_dataframe'), 'data', allow_duplicate=True),
    Input(get_component_id('btn_download_plc'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_itemid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_download_plc_dg(n, set_id, device_id, sample_id):
    return None, []


#%% main
if __name__ == '__main__':     
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=False)