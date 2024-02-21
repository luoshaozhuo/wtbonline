'''
作者：luosz
创建日期： 2024.02.21
描述：后台任务管理
'''
#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update, dash_table
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '任务调度'
SECTION_ORDER = 2
ITEM = '后台任务'
ITEM_ORDER = 1
PREFIX = 'scheduler_job'

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

NOTIFICATION_TITLE_DBQUERY = cfg.NOTIFICATION_TITLE_DBQUERY
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

COLUMNS_DCT = {
    'task_id':'任务id', 
    'status':'状态', 
    'setting':'类型', 
    'task_parameter':'参数', 
    'func':'目标函数', 
    'function_parameter':'目标函数参数', 
    'start_time':'开始时间', 
    'next_run_time':'下次运行时间', 
    'username':'拥有者'
}
TABLE_COLUMNS = list(COLUMNS_DCT.keys())
TABLE_HEADERS = list(COLUMNS_DCT.values())

UNIT = [{'label':'秒', 'value':'s'}, {'label':'天', 'value':'d'}, {'label':'月', 'value':'m'}]

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

def func_read_task_table():
    apschduler_df, note = utils.dash_try(
        cfg.NOTIFICATION_TITLE_DBQUERY,
        RSDBInterface.read_apscheduler_jobs
        )
    if note!=no_update:
        return no_update, note
    timed_task_df, note = utils.dash_try(
        cfg.NOTIFICATION_TITLE_DBQUERY,
        RSDBInterface.read_timed_task
        ) 
    if note!=no_update:
        return no_update, note   
    df = pd.merge(timed_task_df, apschduler_df, how='left', left_on='task_id', right_on='id')
    df['next_run_time'] = pd.to_datetime(df['next_run_time'], unit='s') + pd.Timedelta('8h')
    return df[TABLE_COLUMNS], no_update

def func_render_table():
    data, note = func_read_task_table()
    if note==no_update:
        data.columns = TABLE_HEADERS
        data = data.to_dict('records')
    return data, note


#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=TOOLBAR_PADDING, 
        children=[
            dcmpt.select_job_type(id=get_component_id('select_type')),
            dmc.DatePicker(
                id=get_component_id('datepicker_start_date'),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                label="开始日期",
                dropdownType='modal',
                description="任务开始执行日期",
                minDate = pd.Timestamp.now().date(),
                style={"width": cfg.TOOLBAR_COMPONENT_WIDTH},
                openDropdownOnClear =True
                ),
            dcmpt.time_input(id=get_component_id('timeinput_start_time'), label="开始时间", value=TIME_START, description="任务开始执行时间"),
            dcmpt.number_input(id=get_component_id('numberinput_interval'), label='执行周期', min=1, value=1),
            dcmpt.select(id=get_component_id('slect_interval_unit'), data=UNIT, value='d',label='周期单位'),
            dmc.Divider(mt='20px'),
            dcmpt.select(id=get_component_id('slect_func'), data=list(cfg.SCHEDULER_JOB_FUNC.keys()), value=None, label='任务函数'),
            dmc.DatePicker(
                id=get_component_id('datepicker_end_date'),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                label="目标函数数据结束日期",
                dropdownType='modal',
                maxDate = pd.Timestamp.now().date(),
                style={"width": cfg.TOOLBAR_COMPONENT_WIDTH},
                openDropdownOnClear =True
                ),
            dcmpt.number_input(id=get_component_id('numberinput_delta'), label='目标函数数据范围（天）', min=1, value=20, description="从结束日期往前数"),
            dcmpt.number_input(id=get_component_id('numberinput_minimun_sample'), label='最少记录数', min=1, value=3000, description="少于此数函数停止执行"),
            dcmpt.number_input(id=get_component_id('numberinput_num_output'), label='输出记录数', min=1, value=20),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_add'),
                leftIcon=DashIconify(icon="mdi:add_circle_outline", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="添加任务",
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
    return dmc.Stack(
        children=[
            dmc.Group(
                children = [
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:play-circle-outline", width=TOOLBAR_ICON_WIDTH, color='teal'),
                        variant="subtle",
                        id=get_component_id('acticon_start'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:pause-circle-outline", width=TOOLBAR_ICON_WIDTH, color='orange'),
                        variant="subtle",
                        id=get_component_id('acticon_pause'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:refresh", width=TOOLBAR_ICON_WIDTH, color='blue'),
                        variant="subtle",
                        id=get_component_id('acticon_refresh'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:stop-circle-outline", width=TOOLBAR_ICON_WIDTH, color='red'),
                        variant="subtle",
                        id=get_component_id('acticon_delete'),
                        )
                    ]
                ),
            dmc.LoadingOverlay(
                    dash_table.DataTable(
                        id=get_component_id('datatable_job'),
                        columns=[{'name': i, 'id': i} for i in TABLE_HEADERS],                           
                        row_deletable=False,
                        row_selectable="single",
                        page_action='native',
                        page_current= 0,
                        page_size= 20,
                        style_header = {'font-weight':'bold'},
                        style_table = {'font-size':'small', 'overflowX': 'auto'},
                        style_data={
                            'height': 'auto',
                            'lineHeight': '15px'
                            },                
                    )  
                )
            ]
    )


#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
else:
    first_noticifation_output = Output('notficiation_container', 'children', allow_duplicate=True)

dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout =  dmc.NotificationsProvider(children=[
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[creat_content()], size='lg',pt=HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan="lg",
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ])

#%% callback
@callback(
    Output(get_component_id('acticon_start'), 'disabled'), 
    Output(get_component_id('acticon_pause'), 'disabled'), 
    Output(get_component_id('acticon_delete'), 'disabled'), 
    Input(get_component_id('datatable_job'), 'selected_rows'),
    Input(get_component_id('datatable_job'), 'data'),
    )
def callback_enable_actionicons_job(rows, data):
    rev = [True]*3
    if (data is not None) and len(data)>0 and (rows is not None) and len(rows)>0:
        row = pd.DataFrame(data).iloc[rows[0]].squeeze()
        status = row['状态']
        if status=='JOB_ADDED':
            rev = [True, False, False]
        elif row['类型']=='interval' and status in ('JOB_EXECUTED', 'JOB_ERROR', 'JOB_MISSED'):
            rev = [True, False, False]
        elif status=='JOB_STOP':
            rev = [False, True, False]
        elif status=='CREATED':
            rev = [False, True, True]
    return rev

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'data', allow_duplicate=True),
    Input(get_component_id('acticon_refresh'), 'n_clicks'),
    prevent_initial_call=True,
    )
def callback_refresh_table_job(n):
    data, note = func_render_table()
    return note, data

@callback(
    Output(get_component_id('numberinput_interval'), 'disabled'),
    Output(get_component_id('slect_interval_unit'), 'disabled'),
    Output(get_component_id('timeinput_start_time'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    prevent_initial_call=True,
    )
def timed_task_on_change_setting(setting):
    disabled = False if setting=='interval' else True
    start_time = '2022-02-02T00:00:00' if setting=='interval' else pd.Timestamp.now()
    return disabled, disabled, start_time

@callback(
    Output(get_component_id('btn_add'), 'disabled'),
    Output(get_component_id('datepicker_end_date'), 'disabled'),
    Output(get_component_id('numberinput_minimun_sample'), 'disabled'),
    Output(get_component_id('numberinput_num_output'), 'disabled'),
    Output(get_component_id('numberinput_delta'), 'disabled'),
    Input(get_component_id('slect_func'), 'value'),
    )
def timed_task_on_change_func(func):
    btn_add = True if (func is None or func=='') else False
    end_date = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    minimum = False if func in ['训练离群值识别模型'] else True
    size = False if func in ['离群值识别'] else True
    delta = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    return btn_add, end_date, minimum, size, delta



#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)