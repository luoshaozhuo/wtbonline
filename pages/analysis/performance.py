'''
作者：luosz
创建日期： 2024.02.18
描述：分析——性能
    1、功率曲线
    2、功率差异
'''

#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

import wtbonline.configure as cfg
from wtbonline._common import dash_component as dcmpt
from wtbonline._process.tools.common import get_date_range_statistics_sample
from wtbonline._plot import graph_factory

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='性能'
ITEM_ORDER = 1
PREFIX =  'analysis_performance'

TABLE_COLUMNS = cfg.TOOLBAR_TABLE_COLUMNS
TABLE_FONT_SIZE = cfg.TOOLBAR_TABLE_FONT_SIZE
TABLE_HEIGHT = cfg.TOOLBAR_TABLE_HEIGHT

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

TYPE_  = [
    {'label':'功率曲线', 'value':'PowerCurve'},
    {'label':'功率对比', 'value':'PowerCompare'}
    ]

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_analysis_type(id=get_component_id('select_type'), data=TYPE_, label='分析类型'),
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.multiselect_device_id(id=get_component_id('multiselect_device_id')),
            dcmpt.date_picker(id=get_component_id('datepicker_end'), label="结束日期", description="此日期的零点为区间右端"),
            dcmpt.number_input(id=get_component_id('input_span'), label='时长', value=90, min=1, description='单位，天'),
            dmc.Space(h='10px'),
            dmc.LoadingOverlay(
                dmc.Button(
                    fullWidth=True,
                    disabled=False,
                    id=get_component_id('btn_refresh'),
                    leftIcon=DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH),
                    size=cfg.TOOLBAR_COMPONENT_SIZE,
                    children="刷新图像",
                    ),
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
    dmc.Container(children=[creat_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ]

#%% callback
@callback(
    Output(get_component_id('multiselect_device_id'), 'data'),
    Output(get_component_id('multiselect_device_id'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    )
def callback_update_multiselect_device_id_performance(set_id):
    df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['set_id']==set_id]
    data = [] if df is None else [{'label':row['device_name'], 'value':row['device_id']} for _,row in df.iterrows()]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_end'), 'disabled'),
    Output(get_component_id('datepicker_end'), 'minDate'),
    Output(get_component_id('datepicker_end'), 'maxDate'),
    Output(get_component_id('datepicker_end'), 'value'),
    Output(get_component_id('btn_refresh'), 'disabled'), 
    Input(get_component_id('multiselect_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_update_components_performance(device_ids):
    if device_ids in (None, '') or len(device_ids)<1:
        return no_update, True, None, None, None, True
    df, note = dcmpt.dash_dbquery(
        func = get_date_range_statistics_sample,
        device_id=device_ids
        )
    ids = df['device_id'].unique().tolist()
    if len(device_ids) != len(ids):
        note = dcmpt.notification(
            title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA,
            msg=f'部分机组查询数据失败，返回{ids}，需求{device_ids}',
            _type='error'
            )
    minDate = df['start_date'].max() if note is None else None
    maxDate = df['end_date'].min() if note is None else None
    disabled = not(note is None)
    return note, disabled, minDate, maxDate, maxDate, disabled

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('datepicker_end'), 'value'),
    State(get_component_id('input_span'), 'value'),
    State(get_component_id('select_type'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('multiselect_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_performance(n, end_date, span, type_, set_id, device_ids):
    end_time = pd.to_datetime(end_date)   
    start_time =  pd.to_datetime(end_date) - pd.Timedelta(f'{span}d')
    figure, note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA,   
        func=graph_factory.get(type_)().plot, 
        set_id=set_id,
        device_ids=device_ids,
        start_time=start_time,
        end_time=end_time
        )
    figure = {} if figure is None else figure
    return note, figure

#%% main
if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout, limit=5)   
    app.layout = layout
    app.run_server(debug=True)