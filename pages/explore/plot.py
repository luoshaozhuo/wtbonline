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
import json

from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._plot.functions import simple_plot, get_simple_plot_parameters
from wtbonline._common import dash_component as dcmpt
from wtbonline._process.tools.common import get_date_range_tsdb
from wtbonline._db.tsdb_facade import TDFC

#%% constant
SECTION = '探索'
SECTION_ORDER = 2
ITEM='图形'
ITEM_ORDER = 1
PREFIX =  'explore_plot'

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
            dcmpt.date_picker(id=get_component_id('datepicker_end'), label="结束日期", description="此日期的零点为区间右端"),
            dcmpt.number_input(id=get_component_id('input_span'), label='时长', value=1, min=1, description='单位，天'),
            dmc.Space(h='10px'),
            dcmpt.select(id=get_component_id('select_type'), data=cfg.SIMPLE_PLOT_TYPE, value=None, label='类型'),  
            dcmpt.select(id=get_component_id('select_xaxis'), data=[], value=None, label='x坐标（θ坐标）', description='需要先选择类型以及机型编号', ),
            dcmpt.select(id=get_component_id('select_yaxis'), data=[], value=None, label='y坐标（r坐标）', description='需要先选择类型以及机型编号', clearable=True),
            dmc.Space(h='20px'),
            dmc.LoadingOverlay(
                dmc.Button(
                    fullWidth=True,
                    disabled=True,
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
    dcc.Store(id=get_component_id('store_figure'), storage_type='session', data={}),
    dmc.Container(children=[creat_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
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
def callback_update_select_device_name_fault(set_id):
    df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['set_id']==set_id]
    data = [] if df is None else [{'label':row['device_name'], 'value':row['device_id']} for _,row in df.iterrows()]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_end'), 'disabled'),
    Output(get_component_id('datepicker_end'), 'minDate'),
    Output(get_component_id('datepicker_end'), 'maxDate'),
    Output(get_component_id('datepicker_end'), 'value'),
    Input(get_component_id('select_device_id'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_end_performance(device_id):
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
    Output(get_component_id('select_xaxis'), 'data'),
    Output(get_component_id('select_xaxis'), 'value'),
    Output(get_component_id('select_yaxis'), 'data'),
    Output(get_component_id('select_yaxis'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_slect_type_plot(_type, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [_type, set_id]:
        return [no_update]*6
    df = cfg.WINDFARM_VAR_NAME[cfg.WINDFARM_VAR_NAME['set_id']==set_id]
    if _type=='时序图':
        x_data = [{'label':'时间', 'value':'ts'}]
        x_value = 'ts'
        y_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in df.iterrows()]
        y_value = None
    elif _type=='散点图':
        sub_df = df[df['datatype'].isin(['F', 'I'])]
        x_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in sub_df.iterrows()]
        x_value = None
        y_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in sub_df.iterrows()]
        y_value = None
    elif _type=='极坐标图':
        sub_df = df[(df['point_name'].str.find('角')>-1) & (df['unit']=='°')]
        x_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in sub_df.iterrows()]
        x_value = None
        y_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in sub_df.iterrows()]
        y_value = None    
    elif _type=='频谱图':
        sub_df = df[df['datatype']=='F']
        x_data = [{'label':'频率', 'value':'ts'}]
        x_value = 'ts'
        y_data = [{'label':row['point_name'],'value':row['var_name']} for _,row in sub_df.iterrows()]
        y_value = None
    return x_data, x_value, y_data, y_value

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('btn_refresh'), 'disabled'), 
    Output(get_component_id('store_figure'), 'data'), 
    Input(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_xaxis'), 'value'),
    Input(get_component_id('select_yaxis'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    Input(get_component_id('datepicker_end'), 'value'),
    Input(get_component_id('input_span'), 'value'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True 
)
def callback_update_btn_resresh_plot(device_id, xcol, ycol, set_id, date_end, time_span, plot_type):
    if pd.Series([device_id, plot_type, xcol, ycol, date_end, time_span]).isna().any():
        return no_update, True, {}
    columns = pd.Series([xcol, ycol]).drop_duplicates().replace(['ts', '时间','频率'], None).dropna()
    end_time = pd.to_datetime(date_end)
    start_time = end_time - pd.Timedelta(f'{time_span}d')
    df, note = dcmpt.dash_dbquery(
            func=TDFC.read,
            set_id=set_id, 
            device_id=device_id, 
            columns=columns, 
            start_time=start_time,
            end_time=end_time,
            sample=cfg.SIMPLE_PLOT_SAMPLE_NUM,
            remote=True        
        )
    if note is not None:
        return note, True, {}
    xcol, xtitle, ycol, ytitle = get_simple_plot_parameters(xcol, ycol, plot_type, set_id)
    fig, note = dcmpt.dash_try(
        note_title='绘图失败',
        func=simple_plot,
        df = df,
        xcol=xcol, 
        ycol=ycol, 
        xtitle=xtitle,
        ytitle=ytitle, 
        type_=plot_type, 
        title=None,
        height=700,
        )
    fig = fig.to_json() if note is None else {}
    return note, not(note is None), fig

@callback(
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('store_figure'), 'data'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_plot(n, figure):
    return figure if isinstance(figure, dict) else json.loads(figure)

#%% main
if __name__ == '__main__':   
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)