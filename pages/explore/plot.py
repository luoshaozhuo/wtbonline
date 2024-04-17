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
import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

import wtbonline.configure as cfg
from wtbonline._common import dash_component as dcmpt
from wtbonline._process.tools.common import get_date_range_tsdb
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._plot import graph_factory   

#%% constant
SECTION = '探索'
SECTION_ORDER = 2
ITEM='图形'
ITEM_ORDER = 1
PREFIX =  'explore_plot'

MAX_VALUES = 10 # 最多可以选择的变量数

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[   
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select(id=get_component_id('select_device_id'), data=[], value=None, label='风机编号'),
            dcmpt.date_picker(id=get_component_id('datepicker_date_start'), label="开始日期", description="时间区间为左闭右开"),
            dcmpt.time_input(id=get_component_id('input_time_start'), label='开始时间', value=cfg.TIME_START, description="与开始日期组合为区间左端点"),
            dcmpt.number_input(id=get_component_id('input_span'), label='时长', value=10, min=1, description='单位，分钟'),
            dmc.Space(h='10px'),
            dcmpt.select_general_graph_type(id=get_component_id('select_type')),
            dcmpt.select(id=get_component_id('select_xaxis'), data=[], value=None, label='x坐标（θ坐标）', description='需要先选择类型以及机型编号', ),
            dcmpt.multiselect(id=get_component_id('multiselect_yaxis'), label='y坐标（r坐标）', description='需要先选择类型以及机型编号', clearable=True, maxSelectedValues=MAX_VALUES),
            dmc.Space(h='20px'),
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
            dmc.Space(h='100px'),
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
    dmc.Container(children=[dmc.Space(h='20px'), creat_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )   
    ]

#%% callback
@callback(
    Output(get_component_id('select_device_id'), 'data'),
    Output(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    )
def callback_update_select_device_name_plot(set_id):
    df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['set_id']==set_id]
    data = [] if df is None else [{'label':row['device_name'], 'value':row['device_id']} for _,row in df.iterrows()]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_date_start'), 'disabled'),
    Output(get_component_id('datepicker_date_start'), 'minDate'),
    Output(get_component_id('datepicker_date_start'), 'maxDate'),
    Output(get_component_id('datepicker_date_start'), 'value'),
    Input(get_component_id('select_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_date_start_plot(device_id):
    if device_id in (None, ''):
        return no_update, True, None, None, None
    df, note = dcmpt.dash_dbquery(
        func = get_date_range_tsdb,
        device_id=device_id
        )
    minDate = df['start_date'].max() if note is None else None
    maxDate = df['end_date'].min() if note is None else None
    return note, not(note is None), minDate, maxDate, maxDate

@callback(
    Output(get_component_id('input_time_start'), 'disabled'), 
    Output(get_component_id('input_span'), 'disabled'), 
    Output(get_component_id('select_type'), 'disabled'), 
    Output(get_component_id('select_xaxis'), 'disabled'), 
    Output(get_component_id('multiselect_yaxis'), 'disabled'),    
    Input(get_component_id('datepicker_date_start'), 'value'),
    )
def callback_disable_selections_plot(value):
    disabled = value in [None, '']
    return [disabled]*5

@callback(
    Output(get_component_id('btn_refresh'), 'disabled'), 
    Input(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_xaxis'), 'value'),
    Input(get_component_id('multiselect_yaxis'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    Input(get_component_id('datepicker_date_start'), 'value'),
    Input(get_component_id('input_time_start'), 'value'),
    Input(get_component_id('input_span'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    )
def callback_disable_btn_refresh_plot(*args):
    return  (None in args) or ('' in args) or ([] in args)

@callback(
    Output(get_component_id('select_xaxis'), 'data'),
    Output(get_component_id('select_xaxis'), 'value'),
    Output(get_component_id('multiselect_yaxis'), 'data'),
    Output(get_component_id('multiselect_yaxis'), 'value'),
    Output(get_component_id('multiselect_yaxis'), 'maxSelectedValues'),
    Input(get_component_id('select_type'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_slect_type_plot(type_, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [type_, set_id]:
        return [], None, [], [], 1
    x_data, x_value, y_data, y_values, maxSelectedValues = dcmpt.get_general_plot_selections(set_id, type_)
    return x_data, x_value, y_data, y_values, maxSelectedValues

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'), 
    Input(get_component_id('btn_refresh'), 'n_clicks'), 
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_xaxis'), 'value'),
    State(get_component_id('multiselect_yaxis'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('datepicker_date_start'), 'value'),
    State(get_component_id('input_time_start'), 'value'),
    State(get_component_id('input_span'), 'value'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True 
)
def callback_on_btn_resresh_plot(n, device_id, xcol, ycols, set_id, date_start, time_start, time_span, plot_type):
    var_names = pd.Series([xcol] + ycols).replace('ts', None).dropna()
    start_time = pd.to_datetime(date_start+time_start[-9:])
    end_time = start_time  + pd.Timedelta(f'{time_span}m')
    obj = graph_factory.get(plot_type)(row_height=200)
    obj.init(var_names=var_names)
    fig,note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,
        func=obj.plot,
        set_id=set_id,
        device_ids=device_id,
        start_time=start_time,
        end_time=end_time
        )
    fig = {} if fig is None else fig
    return note, fig

#%% main
if __name__ == '__main__':   
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)