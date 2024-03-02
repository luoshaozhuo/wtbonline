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
from dash import Output, Input, html, dcc, State, callback, no_update, dash_table, ctx
import pandas as pd
import numpy as np
from functools import partial
from flask_login import current_user
import requests
import time

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '任务调度'
SECTION_ORDER = 4
ITEM = '后台任务'
ITEM_ORDER = 1
PREFIX = 'scheduler_job'

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

UNIT = [{'label':i, 'value':i} for i in cfg.SCHEDULER_JOB_INTER_UNIT]

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
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_job_type(id=get_component_id('select_setting')),
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
            dcmpt.time_input(id=get_component_id('timeinput_start_time'), label="开始时间", value=cfg.TIME_START, description="任务开始执行时间"),
            dcmpt.number_input(id=get_component_id('numberinput_interval'), label='执行周期', min=1, value=1),
            dcmpt.select(id=get_component_id('slect_interval_unit'), data=UNIT, value=UNIT[0], label='周期单位'),
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
                leftIcon=DashIconify(icon="mdi:add_circle_outline", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="添加任务",
                ), 
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
    return dmc.Stack(
        children=[
            dmc.Group(
                children = [
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:play-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='teal'),
                        variant="subtle",
                        id=get_component_id('acticon_start'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:pause-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='orange'),
                        variant="subtle",
                        id=get_component_id('acticon_pause'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH, color='blue'),
                        variant="subtle",
                        id=get_component_id('acticon_refresh'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:stop-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='red'),
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
                        page_size= 40,
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
    dmc.Container(children=[creat_content()], size='lg',pt=cfg.HEADER_HEIGHT),
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
    State(get_component_id('datatable_job'), 'data'),
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
def callback_on_refresh_job(n):
    data, note = func_render_table()
    return note, data

@callback(
    Output(get_component_id('numberinput_interval'), 'disabled'),
    Output(get_component_id('slect_interval_unit'), 'disabled'),
    Output(get_component_id('timeinput_start_time'), 'value'),
    Input(get_component_id('select_setting'), 'value'),
    prevent_initial_call=True,
    )
def callback_on_select_type_job(setting):
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
def callback_on_select_func_job(func):
    btn_add = True if (func is None or func=='') else False
    end_date = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    minimum = False if func in ['训练离群值识别模型'] else True
    size = False if func in ['离群值识别'] else True
    delta = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    return btn_add, end_date, minimum, size, delta

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'data', allow_duplicate=True),
    Input(get_component_id('btn_add'), 'n_clicks'),
    State(get_component_id('select_setting'), 'value'),
    State(get_component_id('datepicker_start_date'), 'value'),
    State(get_component_id('timeinput_start_time'), 'value'), 
    State(get_component_id('numberinput_interval'), 'value'),
    State(get_component_id('slect_interval_unit'), 'value'),
    State(get_component_id('slect_func'), 'value'),
    State(get_component_id('datepicker_end_date'), 'value'),
    State(get_component_id('numberinput_delta'), 'value'), 
    State(get_component_id('numberinput_minimun_sample'), 'value'), 
    State(get_component_id('numberinput_num_output'), 'value'),    
    prevent_initial_call=True,
    )
def callback_on_btn_add_job(
    n, setting, start_date, start_time, interval, unit, func, end_date, delta, 
    minimum_sample, num_output
    ):
    esisted_job, note = utils.dash_dbquery(RSDBInterface.read_timed_task)
    if esisted_job is None:
        return note, no_update
    if func=='统计10分钟样本' and func in esisted_job['func']:
       return dcmpt(title='重复任务', msg='请先删除重复任务', _type='error'), no_update 
   # 任务发布者
    try:
        username = current_user.username
    except:
        username = 'timed_task_test'

    task_id = str(pd.Timestamp.now().date()) + '-' + str(np.random.randint(0, 10**6))
    job_start_time = ' '.join([start_date, start_time.split('T')[1]])
    task_parameter = {'misfire_grace_time':cfg.MISFIRE_GRACE_TIME}
    if setting=='interval':
        task_parameter.update({unit:interval})
    
    end_time = end_date+' 00:00:00' if (end_date is not None and end_date!='') else ''
    function_parameter = dict(
        end_time = end_time,
        delta = delta,
        size = minimum_sample,
        minimum = num_output,
        task_id = task_id
        )
    
    dct = dict(
        task_id=task_id,
        status='CREATED',
        func=func,
        setting=setting,
        start_time=job_start_time,
        task_parameter=f'{task_parameter}',
        function_parameter=f'{function_parameter}',
        username=username,
        update_time=pd.Timestamp.now()
        )
    
    _, note = utils.dash_dbquery(
        func =  RSDBInterface.insert,
        df = dct,
        tbname = 'timed_task'
        )
    if note != no_update:
        return note, no_update
    data, note = func_render_table()
    return note, data

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'data', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'selected_rows', allow_duplicate=True),   
    Input(get_component_id('acticon_start'), 'n_clicks'),
    Input(get_component_id('acticon_pause'), 'n_clicks'),
    Input(get_component_id('acticon_delete'), 'n_clicks'),
    State(get_component_id('datatable_job'), 'data'),
    State(get_component_id('datatable_job'), 'selected_rows'),
    prevent_initial_call=True,
    )
def timed_task_on_btn_start_pause_delete(n1, n2, n3, data, rows):  
    # 只有单行，因为datatable不能多选
    row = pd.DataFrame(data).iloc[rows[0], :]
    _id = ctx.triggered_id
    url = cfg.SCHEDULER_URL
    timeout = cfg.SCHEDULER_TIMEOUT
    data = no_update
    for _ in range(3):
        try:
            if _id==get_component_id('acticon_start'):
                if row['状态'] == 'CREATED':
                    task_parameter = eval(row['参数'])
                    funtion_parameter = eval(row['目标函数参数'])
                    funtion_parameter.update({"task_id":row['任务id']})
                    key_ = 'run_date' if row['类型']=='date' else 'start_date'
                    kwargs = {
                        'id':f"{row['任务id']}", 
                        'func':row['目标函数'], 
                        'trigger':row['类型'],
                        key_:row['开始时间'],
                        'kwargs':funtion_parameter,
                        }
                    kwargs.update(task_parameter)
                    response = requests.post(url, json=kwargs, timeout=timeout)
                else:
                    response = requests.post(url+f"/{row['任务id']}/resume", timeout=timeout)
            elif _id==get_component_id('acticon_pause'):
                response = requests.post(url+f"/{row['任务id']}/pause", timeout=timeout)
            elif _id==get_component_id('acticon_delete'):
                response = requests.delete(url+f"/{row['任务id']}", timeout=timeout)
        except Exception as e:
            _type = 'error'
            response = None
            title = cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL
            msg = f'{row["任务id"]} {row["目标函数"]} {e}'
            break
        if response.ok == True:
            _type = 'success'
            title = cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_SUCCESS
            msg =  f'{row["任务id"]} {row["目标函数"]}'
            break
        time.sleep(1)
    else:
        data, note = func_render_table()
        if note!=no_update:
            return note, no_update, no_update 
        _type = 'error'
        title = cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL
        msg = msg = f'{row["任务id"]} {row["目标函数"]} 提交超时'
    note = dcmpt.notification(title, msg, _type), no_update, no_update       
    return note, data, []



#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)