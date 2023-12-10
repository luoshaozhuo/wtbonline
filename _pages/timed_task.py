# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 14:22:56 2023

@author: luosz

账户管理页面
"""

# =============================================================================
# import
# =============================================================================
from dash import html, Input, Output, no_update, callback, State, ctx, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from flask_login import current_user
import requests
import time
from dash_iconify import DashIconify

from wtbonline._pages.tools._decorator import _on_error
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools.utils import is_duplicated_task
from wtbonline._common.code import SCHEDULER_MANIPULATION_FAILED, SCHEDULER_CONNECTION_FAILED, MYSQL_QUERY_FAILED

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'task'

TIMEOUT = 10

_COLUMNS_DCT = {
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
_TABLE_COLUMNS = list(_COLUMNS_DCT.keys())
_TABLE_HEADERS = list(_COLUMNS_DCT.values())

_FUNC_DCT = { 
    "初始化数据库":"wtbonline._process.preprocess.init_tsdb:init_tdengine",
    "拉取原始数据":"wtbonline._process.preprocess.load_tsdb:update_tsdb",
    "拉取ibox数据":"wtbonline._process.preprocess.load_ibox_files:update_ibox_files",
    "统计10分钟样本":"wtbonline._process.statistics.sample:update_statistic_sample",
    "统计24小时样本":"wtbonline._process.statistics.daily:udpate_statistic_daily",
    "检测故障":"wtbonline._process.statistics.fault:udpate_statistic_fault",
    "训练离群值识别模型":"wtbonline._process.model.anormlay.train:train_all",
    "离群值识别":"wtbonline._process.model.anormlay.predict:predict_all",
    "数据统计报告":"wtbonline._report.brief_report:build_brief_report_all",
    "清理缓存":"wtbonline._pages.tools.utils:clear_cache"
    }

_DATE_DATE_FORMAT = '%Y-%m-%d'
_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_URL='http://scheduler:40000/scheduler/jobs'

SUCCESS = 0
FAILED = 1 

# =============================================================================
# function
# =============================================================================
def _make_sure_datetime_string(x):
    if x is None:
        x = '0000000000T00:00:00'
    return x

def read_task_table():
    apschduler_df = RSDBInterface.read_apscheduler_jobs()
    timed_task_df = RSDBInterface.read_timed_task()
    df = pd.merge(timed_task_df, apschduler_df, how='left', left_on='task_id', right_on='id')
    df['next_run_time'] = pd.to_datetime(df['next_run_time'], unit='s') + pd.Timedelta('8h')
    return df[_TABLE_COLUMNS]

def _render_table():
    df = read_task_table()
    df.columns = _TABLE_HEADERS
    data = df.to_dict('records')
    return data

# =============================================================================
# layout
# =============================================================================
def get_notification(_type:int, message:str):
    if _type==SUCCESS:
        autoClose = 1500
        color = 'green'
        title = 'success'
        icon=DashIconify(icon="akar-icons:circle-check")
    elif _type==FAILED:
        autoClose = False
        color = 'red'
        title = 'failed'
        icon=DashIconify(icon="ic:twotone-warning-amber")
    return dmc.Notification(
            id=f'{_PREFIX}_notification',
            title=title,
            action="show",
            message=message,
            icon=icon,
            color=color,
            autoClose=autoClose
        )

def _setting():
    return dbc.Card([
            dbc.CardHeader('任务管理'),
            dbc.CardBody([
            dbc.ButtonGroup([
                dbc.Button(html.I(className='bi bi-play'),  
                            id=f'{_PREFIX}_btn_start', 
                            className='btn-success', 
                            disabled=True,
                            n_clicks=0,
                            ),
                dbc.Button(html.I(className='bi bi-pause-circle'),  
                            id=f'{_PREFIX}_btn_pause', 
                            className='btn-warning', 
                            disabled=True,
                            n_clicks=0,
                            ),
                dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                            id=f'{_PREFIX}_btn_refresh', 
                            className='btn-info', 
                            n_clicks=0,
                            ),
                dbc.Button(html.I(className='bi bi-trash'),  
                            id=f'{_PREFIX}_btn_delete', 
                            className='btn-danger', 
                            disabled=True,
                            n_clicks=0,
                            ),
                ],
                size='sm',
                class_name='mb-2'),
            dmc.LoadingOverlay(
                    dash_table.DataTable(
                    id=f'{_PREFIX}_datatable',
                    columns=[{'name': i, 'id': i} for i in _TABLE_HEADERS],                           
                    row_deletable=False,
                    row_selectable="single",
                    page_action='native',
                    page_current= 0,
                    page_size= 20,
                    style_header = {'font-weight':'bold'},
                    style_table = {'font-size':'small', 'overflowX': 'auto'},
                    style_data={
                        # 'whiteSpace': 'normal',
                        'height': 'auto',
                        'lineHeight': '15px'
                    },                
                    )  
                )
            ])
        ])


def _control():
    return dbc.Card([
            dbc.CardHeader('任务设置'),
            dbc.CardBody([       
                dbc.InputGroup([
                    dbc.InputGroupText("任务类型"), 
                    dbc.Select(
                        id=f'{_PREFIX}_setting',
                        options=[
                            {"label":"周期任务", "value":"interval"},
                            {"label":"一次性任务", "value":"date"},
                            ],
                        )
                    ]),
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_start_date', size='sm', placeholder='默认为当前日期'),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_start_time', size='sm', value='2022-02-02T00:00:00'),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup([
                    dbc.InputGroupText("周期", class_name='small'), 
                    dmc.NumberInput(id=f'{_PREFIX}_interval', size="md", min=1, value=1, style={"width":150}, disabled=True),
                    dbc.Select(
                        id=f'{_PREFIX}_interval_unit',
                        placeholder='单位',
                        value='days',
                        options = [
                            {"label":'周', "value":'weeks'},
                            {"label":'天', "value":'days'}, 
                            {"label":'小时', "value":'hours'},
                            {"label":'分钟', "value":'minutes'},
                            {"label":'秒', "value":'seconds'},
                            ],
                        style={"width":25},
                        class_name='small'
                        )
                    ]),
                html.Hr(),
                dbc.InputGroup([
                    dbc.InputGroupText("任务函数"), 
                    dbc.Select(
                        id=f'{_PREFIX}_func',
                        options = [{"label":key, "value":key} for key in _FUNC_DCT]
                        )
                    ]),
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("截止日", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_end_date', size='sm', value=pd.Timestamp.now().date(), disabled=True),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("最少数据条数", class_name='small'),
                        dmc.NumberInput(id=f'{_PREFIX}_minimum', size="md", min=1, value=3000, style={"width":100}, disabled=True),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("输出记录条数", class_name='small'),
                        dmc.NumberInput(id=f'{_PREFIX}_size', size="md", min=1, value=20, style={"width":100}, disabled=True),
                        ], 
                    className='w-100'
                    ),        
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("时长（天）", class_name='small'),
                        dmc.NumberInput(id=f'{_PREFIX}_delta', size="md", min=1, value=180, style={"width":100}, disabled=True),
                        ], 
                    className='w-100'
                    ), 
                html.Hr(),
                html.Div(
                    dbc.Button('添加任务', color='primary', className='me-1', id=f'{_PREFIX}_btn_add', disabled=True),
                    className='d-grid',
                )
            ])       
        ])


def get_layout():
    layout = [
        dmc.NotificationsProvider(html.Div(id=f'{_PREFIX}_notification_container')),  
        dbc.Row(
            [
                dbc.Col(
                    [   
                     _control()
                     ],
                    width=2, 
                    className='border-end h-100'
                    ),
                dbc.Col(
                    _setting(), 
                    width=10,
                    className='h-100'
                    ),
                ],
            className='g-0 h-100'
            )
        ]
    return layout

# =============================================================================
# callback
# =============================================================================
@callback(
    Output(f'{_PREFIX}_interval', 'disabled'),
    Output(f'{_PREFIX}_interval_unit', 'disabled'),
    Output(f'{_PREFIX}_start_time', 'value'),
    Input(f'{_PREFIX}_setting', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_change_setting(setting):
    disabled = False if setting=='interval' else True
    start_time = '2022-02-02T00:00:00' if setting=='interval' else pd.Timestamp.now()
    return disabled, disabled, start_time

@callback(
    Output(f'{_PREFIX}_btn_add', 'disabled'),
    Output(f'{_PREFIX}_end_date', 'disabled'),
    Output(f'{_PREFIX}_minimum', 'disabled'),
    Output(f'{_PREFIX}_size', 'disabled'),
    Output(f'{_PREFIX}_delta', 'disabled'),
    Input(f'{_PREFIX}_func', 'value'),
    Input(f'{_PREFIX}_setting', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_change_func(func, setting):
    btn_add = True if (func is None or func=='') or (setting is None or setting=='') else False
    end_date = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    minimum = False if func in ['训练离群值识别模型'] else True
    size = False if func in ['离群值识别'] else True
    delta = False if func in ['训练离群值识别模型', '离群值识别', '数据统计报告'] else True
    return btn_add, end_date, minimum, size, delta

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_notification_container', "children", allow_duplicate=True),  
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    State(f'{_PREFIX}_func', 'value'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),
    State(f'{_PREFIX}_setting', 'value'),
    State(f'{_PREFIX}_interval', 'value'),
    State(f'{_PREFIX}_interval_unit', 'value'),
    State(f'{_PREFIX}_end_date', 'value'),
    State(f'{_PREFIX}_minimum', 'value'),
    State(f'{_PREFIX}_size', 'value'),
    State(f'{_PREFIX}_delta', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_add(n, func, job_start_date, job_start_time, setting, interval, unit,  end_date, minimum, size, delta):
    func_name = _FUNC_DCT[func].split(':')[1]
    if 'update_statistic_sample'==func_name and is_duplicated_task(func_name):
        message =  f"{func}：任务已存在，不可以重复添加。"
        return no_update, get_notification(FAILED, message=message)
    
    try:
        username = current_user.username
    except:
        username = 'timed_task_test'
    job_start_time = _make_sure_datetime_string(job_start_time)
    
    job_start_date = pd.Timestamp.now() if job_start_date is None else pd.to_datetime(job_start_date)
    if job_start_time is None or job_start_time=='':
        job_start_time = job_start_date.strftime(_DATE_TIME_FORMAT)
    else:
        job_start_time = job_start_date.strftime(_DATE_DATE_FORMAT) + ' ' + job_start_time[11:]
        
    task_parameter = {'misfire_grace_time':600}
    if setting=='interval':
        task_parameter.update({unit:interval})
    
    end_time = end_date+' 00:00:00' if end_date is not None and end_date!='' else ''
    function_parameter = dict(
        end_time = end_time,
        delta = delta,
        size = size,
        minimum = minimum
        )
    
    task_id = str(pd.Timestamp.now().date()) + '-' + str(np.random.randint(0, 10**6))
    function_parameter.update({"task_id":task_id})
    key_ = 'run_date' if setting=='date' else 'start_date'
    kwargs = {
        'id':task_id, 
        'func':_FUNC_DCT[func], 
        'trigger':setting,
        key_:job_start_time,
        'kwargs':function_parameter,
        }
    kwargs.update(task_parameter)
    
    _type = SUCCESS
    message = ''
    
    try:
        RSDBInterface.insert(
            dict(
                task_id=task_id,
                status='CREATED',
                func=_FUNC_DCT[func],
                setting=setting,
                start_time=job_start_time,
                task_parameter=f'{task_parameter}',
                function_parameter=f'{function_parameter}',
                username=username,
                update_time=pd.Timestamp.now()
                ),
            'timed_task'
            )
    except:
        _type = FAILED
        message = MYSQL_QUERY_FAILED    
    
    return _render_table(),  get_notification(_type, message)


@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_refresh(n):
    return _render_table()

@callback(
    Output(f'{_PREFIX}_btn_start', 'disabled'),
    Output(f'{_PREFIX}_btn_pause', 'disabled'),
    Output(f'{_PREFIX}_btn_delete', 'disabled'),
    Input(f'{_PREFIX}_datatable', 'selected_rows'),
    Input(f'{_PREFIX}_datatable', 'data'),
    )
@_on_error
def timed_task_select_rows(rows, data):
    rev = [True]*3
    if (data is not None) and len(data)>0 and (rows is not None) and len(rows)>0:
        row = pd.DataFrame(data).iloc[rows[0]].squeeze()
        status = row['状态']
        if status=='ADDED':
            rev = [True, False, False]
        elif row['类型']=='interval' and status in ('EXECUTED', 'ERROR', 'MISSED'):
            rev = [True, False, False]
        elif status=='PAUSED':
            rev = [False, True, False]
        elif status=='CREATED':
            rev = [False, True, True]
    return rev


@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'selected_rows', allow_duplicate=True),
    Output(f'{_PREFIX}_notification_container', "children"),
    Input(f'{_PREFIX}_btn_start', 'n_clicks'),
    Input(f'{_PREFIX}_btn_pause', 'n_clicks'),
    Input(f'{_PREFIX}_btn_delete', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_start_pause_delete(n1, n2, n3, indexs, data):  
    # 只有单行，因为datatable不能多选
    row = pd.DataFrame(data).iloc[indexs[0], :]
    _id = ctx.triggered_id
    for _ in range(3):
        try:
            if _id==f'{_PREFIX}_btn_start':
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
                    response = requests.post(_URL, json=kwargs, timeout=TIMEOUT)
                else:
                    response = requests.post(_URL+f"/{row['任务id']}/resume", timeout=TIMEOUT)
            elif _id==f'{_PREFIX}_btn_pause':
                response = requests.post(_URL+f"/{row['任务id']}/pause", timeout=TIMEOUT)
            elif _id==f'{_PREFIX}_btn_delete':
                response = requests.delete(_URL+f"/{row['任务id']}", timeout=TIMEOUT)
        except Exception as e:
            _type = FAILED
            response = None
            message = SCHEDULER_CONNECTION_FAILED
            break
        if response.ok == True:
            _type = SUCCESS
            message = ''
            break
        time.sleep(1)
    else:
        _type = FAILED
        message = f"{SCHEDULER_MANIPULATION_FAILED}：task_id={row['任务id']}, code={response.status_code}, response={response.text}"
    
    return _render_table(), [], get_notification(_type=_type, message=message)


# =============================================================================
# for test
# =============================================================================
if __name__ == '__main__':
    import dash
    app = dash.Dash(__name__, 
                    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
                    suppress_callback_exceptions=True)
    app.layout = html.Div(get_layout())    
    app.run_server(debug=False)