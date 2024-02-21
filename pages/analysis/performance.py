'''
作者：luosz
创建日期： 2024.02.18
描述：分析——性能
    1、功率曲线
    2、功率差异
'''

#%% import
import time
import dash
import dash_mantine_components as dmc
from matplotlib.style import available
import requests
from dash import dcc, html, dash_table
from dash_iconify import DashIconify
from dash import Output, Input, clientside_callback, html, dcc, page_container, State, callback, ctx, no_update, ALL, MATCH
import pandas as pd
import numpy as np

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline._plot as plt
import wtbonline.configure as cfg

#%% constant
PREFIX =  'analysis_performance_'

ANALYSIS_TYPES = ['功率曲线', '功率差异']

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

NOW = cfg.NOW
DATE = cfg.DATE
TIME_START = cfg.TIME_START
TIME_END = cfg.TIME_END

GRAPH_PADDING_TOP = cfg.GRAPH_PADDING_TOP
GRAPH_CONF = cfg.GRAPH_CONF
NOTIFICATION_TITLE_DBQUERY = cfg.NOTIFICATION_TITLE_DBQUERY
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

#%% function
def func_fetch_setids():
    return ['20835']

def func_fetch_mapids(set_id):
    return ['a01', 'a02']

def func_get_component_id(suffix):
    return PREFIX+suffix

def func_try(note_title, func, *args, **kwargs):
    try:
        rs = func(*args, **kwargs)
        notification = no_update
    except Exception as e:
        rs = None
        notification = dmc.Notification(
            id=f"simple_notify_{np.random.randint(0, 100)}",
            title=note_title,
            action="show",
            autoClose=False,
            message=f'func={func.__name__},args={args},{kwargs},errmsg={e}',
            color='red',
            icon=DashIconify(icon="mdi:alert-rhombus", width=20),
            )
    return rs, notification    

def func_make_datetime(date, time):
    return date + ' ' + time.split('T')[1]

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=TOOLBAR_PADDING, 
        children=[
            dmc.Select(
                id=func_get_component_id('select_type'),
                label='分析类型',
                size=TOOLBAR_COMPONENT_SIZE,
                placeholder="Select one",
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                value=ANALYSIS_TYPES[0],
                data=[{'label':i, 'value':i} for i in ANALYSIS_TYPES]
                ),
            dmc.Select(
                id=func_get_component_id('select_setid'),
                label="机型编号",
                size=TOOLBAR_COMPONENT_SIZE,
                placeholder="Select one",
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                data=[{'label':i, 'value':i} for i in RSDBInterface.read_windfarm_infomation()['set_id']]
                ),
            dmc.Select(
                id=func_get_component_id('select_mapid'),
                label="风机编号",
                size=TOOLBAR_COMPONENT_SIZE,
                placeholder="Select one",
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                ),
            dmc.DatePicker(
                id=func_get_component_id('datepicker_start'),
                size=TOOLBAR_COMPONENT_SIZE,
                label="开始日期",
                dropdownType='modal',
                description="可选日期取决于24小时统计数据",
                minDate = DATE,
                maxDate = DATE,
                disabledDates = [DATE],
                amountOfMonths=1,
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                initialLevel='year',
                openDropdownOnClear =True
                ),
            dmc.TimeInput(
                id=func_get_component_id('time_start'),
                size=TOOLBAR_COMPONENT_SIZE,
                label="开始时间",
                value=TIME_START,
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                ),
            dmc.DatePicker(
                id=func_get_component_id('datepicker_end'),
                size=TOOLBAR_COMPONENT_SIZE,
                label="结束日期",
                dropdownType='modal',
                dropdownPosition='bottom-start',
                description="可选日期大于等于开始日期",
                minDate = DATE,
                maxDate = DATE,
                disabledDates = [DATE],
                amountOfMonths=1,
                initialLevel='year',
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                ),
            dmc.TimeInput(
                id=func_get_component_id('time_end'),
                size=TOOLBAR_COMPONENT_SIZE,
                label="结束时间",
                description="结束时间需要大于开始时间",
                value=TIME_END,
                style={"width": TOOLBAR_COMPONENT_WIDTH},
                ),
            dmc.Space(h='10px'),
            dmc.ActionIcon(
                DashIconify(icon="mdi:add-box", width=TOOLBAR_ICON_WIDTH),
                variant="subtle",
                id=func_get_component_id('icon_add'),
                ),
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"width": TOOLBAR_COMPONENT_WIDTH, "height": TABLE_HEIGHT},
                children=dash_table.DataTable(
                    id=func_get_component_id('table'),
                    columns=[{"name": i, "id": i} for i in TABLE_COLUMNS],
                    row_deletable=True,
                    data=[],
                    style_cell={'fontSize':TABLE_FONT_SIZE}
                    ),
                ),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=func_get_component_id('btn_refresh'),
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
                id=func_get_component_id('graph'),
                config={'displaylogo':False},
                )
            )

#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    first_noticifation_output = Output('notficiation_container', 'children')
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
else:
    first_noticifation_output = Output('notficiation_container', 'children', allow_duplicate=True)

dash.register_page(
    __name__,
    section='分析',
    section_order=2,
    item='性能',
    item_order=1,
    )

layout =  dmc.NotificationsProvider(
    html.Div(
        children= [
            # html.Div(id="notficiation_container") if __name__=='__main__' else html.Div(),
            html.Div(id=func_get_component_id('notification')),
            dmc.Grid(
                gutter=5,
                children=[
                    dmc.Col(pt=GRAPH_PADDING_TOP, pr=TOOLBAR_SIZE, children=html.Div(children=[creat_content()])),
                    dmc.Col(pt=0, span='content', children=html.Div(creat_toolbar(), style={'width':TOOLBAR_SIZE}))
                    ]
                )
            ]
        )
    )

#%% callback
@callback(
    Output(func_get_component_id('drawer_toolbar'), 'opened'),
    Input(func_get_component_id('toolbar_toggle'), 'n_clicks'),
    prevent_initial_call=True
    )
def callback_open_toolbar_performance(n):
    return True

@callback(
    first_noticifation_output,
    Output(func_get_component_id('select_mapid'), 'data'),
    Input(func_get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_performance(set_id):
    df, note = func_try(
        note_title=NOTIFICATION_TITLE_DBQUERY, 
        func=RSDBInterface.read_windfarm_configuration, 
        set_id=set_id
        )
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return note, data

@callback(
    Output(func_get_component_id('notification'), 'children', allow_duplicate=True),
    Output(func_get_component_id('datepicker_start'), 'disabledDates'),
    Output(func_get_component_id('datepicker_start'), 'minDate'),
    Output(func_get_component_id('datepicker_start'), 'maxDate'),
    Input(func_get_component_id('select_mapid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_start_performance(map_id):
    if map_id is None:
        return no_update
    df, note = func_try(
        note_title = NOTIFICATION_TITLE_DBQUERY, 
        func=RSDBInterface.read_windfarm_configuration, 
        map_id=map_id
        )
    if df is None:
        return note, no_update, no_update, no_update
    df, note = func_try(
        note_title = NOTIFICATION_TITLE_DBQUERY, 
        func=RSDBInterface.read_statistics_daily, 
        turbine_id=df['turbine_id'].iloc[0], 
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
        minDate = pd.Timestamp.now().date()
        maxDate = minDate
        disabledDates = [minDate.date().isoformat()]
    return no_update, disabledDates, minDate, maxDate

@callback(
    Output(func_get_component_id('datepicker_end'), 'disabledDates'),
    Output(func_get_component_id('datepicker_end'), 'minDate'),
    Output(func_get_component_id('datepicker_end'), 'maxDate'),
    Output(func_get_component_id('datepicker_end'), 'value'),
    Input(func_get_component_id('datepicker_start'), 'value'),
    State(func_get_component_id('datepicker_start'), 'maxDate'),
    State(func_get_component_id('datepicker_start'), 'minDate'),
    State(func_get_component_id('datepicker_start'), 'disabledDates'),
    State(func_get_component_id('datepicker_end'), 'value'),
    State(func_get_component_id('time_end'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_start_performance(date_start, maxDate_start, minDate_start, disabledDates_start, date_end, tm):
    minDate = date_start if date_start is not None else minDate_start
    maxDate = maxDate_start
    disabledDates = disabledDates_start
    if (date_end is not None) and (date_start is not None) and (date_start<=date_end):
        value = no_update
    else:
        value = None
    return disabledDates, minDate, maxDate, value

@callback(
    Output(func_get_component_id('select_setid'), 'error'),
    Output(func_get_component_id('select_mapid'), 'error'),
    Output(func_get_component_id('datepicker_start'), 'error'),
    Output(func_get_component_id('datepicker_end'), 'error'),
    Output(func_get_component_id('time_end'), 'error'),
    Output(func_get_component_id('table'), 'data'),  
    Input(func_get_component_id('icon_add'), 'n_clicks'),
    State(func_get_component_id('select_setid'), 'value'),
    State(func_get_component_id('select_mapid'), 'value'),
    State(func_get_component_id('datepicker_start'), 'value'),
    State(func_get_component_id('datepicker_end'), 'value'),
    State(func_get_component_id('time_start'), 'value'),
    State(func_get_component_id('time_end'), 'value'),
    State(func_get_component_id('table'), 'data'),
    prevent_initial_call=True    
    )
def callback_on_icon_add(n, set_id, map_id, date_start, date_end, time_start, time_end, tbl_lst):
    tbl_df = pd.DataFrame(tbl_lst, columns=TABLE_COLUMNS)
    errs = ['变量不能为空' if i is None else '' for i in [set_id, map_id, date_start, date_end, time_end]]
    data = no_update
    if time_start.split('T')[1] >= time_end.split('T')[1]:
        errs[-1] = '需要修改结束时间或开始时间'
    if (pd.Series(errs)=='').all():
        start_time=func_make_datetime(date_start, time_start)
        end_time=func_make_datetime(date_end, time_end)
        temp = pd.DataFrame([['new', map_id, start_time, end_time, set_id]], columns=TABLE_COLUMNS)
        data = pd.concat([tbl_df, temp], ignore_index=True).drop_duplicates(subset=['map_id', 'start_time', 'end_time'])
        data[TABLE_COLUMNS[0]] = [f'E{i}' for i in range(len(data))]
        data = data.to_dict('records')
    return *errs, data

@callback(
    Output(func_get_component_id('btn_refresh'), 'disabled'), 
    Input(func_get_component_id('table'), 'data'),  
    prevent_initial_call=True 
)
def callback_update_btn_resresh_component(tbl_lst):
    return True if tbl_lst is None or len(tbl_lst)==0 else False

@callback(
    Output(func_get_component_id('notification'), 'children', allow_duplicate=True),
    Output(func_get_component_id('graph'), 'figure'),
    Input(func_get_component_id('btn_refresh'), 'n_clicks'),
    State(func_get_component_id('table'), 'data'),
    State(func_get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_performance(n, tbl_lst, _type):
    '''
    由于output里有notficiation_container，
    从主页点击左侧导航栏进入此页面时，此函数会被调用，
    必须检查tbl_lst是否有数据，否则会报错
    '''
    if None in [tbl_lst, _type]:
        return no_update, no_update
    target_df = pd.DataFrame(tbl_lst)
    graph = None
    note = no_update
    if len(target_df)>0:
        graph, note = func_try(
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