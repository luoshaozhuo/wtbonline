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
from flask_login import current_user
import requests
import time

from wtbonline._pages.tools._decorator import _on_error
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.rsdb.dao import RSDB
    
# =============================================================================
# constant
# =============================================================================
_PREFIX = 'task'
_COLUMNS = ['id', '状态', '目标函数', '设定', '任务参数', '目标函数参数', '设定执行时间', '下次运行时间', '最近运行结果',  '发布者']
_FUNC_DCT = { 
    "初始化数据库":"wtbonline._process.preprocess:init_tdengine",
    "原始数据ETL":"wtbonline._process.preprocess:update_tsdb",
    "数据统计":"wtbonline._process.statistic:update_statistic_sample",
    "训练模型":"wtbonline._process.modelling:train_all",
    "离群值识别":"wtbonline._process.modelling:predict_all",
    "简报":"wtbonline._report.brief_report:build_brief_report_all",
    "更新缓存":"wtbonline._pages.tools.utils:update_cache",
    "心跳":"wtbonline._process.preprocess:heart_beat",
    }
_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_URL='http://scheduler:40000/scheduler/jobs'

# =============================================================================
# function
# =============================================================================
def _make_sure_datetime_string(x):
    if x is None:
        x = '0000000000T00:00:00'
    return x

def read_task_table():
    # ['id', '状态', '目标函数', '设定', '任务参数', '目标函数参数', '设定执行时间', '下次运行时间', '最近运行结果',  '发布者']
    sql='''
        select e.id, e.status, e.func, e.setting, e.task_parameter, e.function_parameter, e.start_time, f.next_run_time, e.success, e.username from apscheduler_jobs f
        right join 
        (
            select * from timed_task c 
            left join 
            (
                select a.task_id, a.success, a.end_time from timed_task_log a
                right join
                (select task_id, max(end_time) as end_time from timed_task_log GROUP BY task_id) b
                on b.task_id=a.task_id and a.end_time=b.end_time
            ) d
            on d.task_id=c.id
            where c.status='start' or c.status='pause'
        ) e
        on f.id=e.id
        '''
    df = RSDB.read_sql(sql)
    df['next_run_time'] = pd.to_datetime(df['next_run_time'], unit='s') + pd.Timedelta('8h')
    return df

def _render_table():
    df = read_task_table()
    df.columns = _COLUMNS
    data = df.to_dict('records')
    return data

# =============================================================================
# layout
# =============================================================================
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
            dash_table.DataTable(
                id=f'{_PREFIX}_datatable',
                columns=[{'name': i, 'id': i} for i in _COLUMNS],                           
                row_deletable=False,
                row_selectable="single",
                page_action='native',
                page_current= 0,
                page_size= 20,
                style_header = {'font-weight':'bold'},
                style_table = {'font-size':'small'},
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px'
                },                
                )
            ])
        ])


def _control():
    return dbc.Card([
            dbc.CardHeader('任务设置'),
            dbc.CardBody([
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
                        dbc.InputGroupText("运行日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_start_date', size='sm', clearable =False, placeholder='默认为当前日期'),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("运行时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_start_time', size='sm'),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup([
                    dbc.InputGroupText("任务设定"), 
                    dbc.Select(
                        id=f'{_PREFIX}_setting',
                        options=[
                            {"label":"周期任务", "value":"interval"},
                            {"label":"一次性任务", "value":"date"},
                            ],
                        )
                    ]),
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
        dbc.Alert(id=f'{_PREFIX}_alert', color='danger', duration=3000, is_open=False, className='border rounded-0'),
        dbc.Row(
            [
                dbc.Col(
                    _control(), 
                    width=2, 
                    className='border-end h-100'
                    ),
                dbc.Col(
                    _setting(), 
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
    Input(f'{_PREFIX}_setting', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_change_setting(setting):
    rev = False if setting=='interval' else True
    return [rev]*2

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
    end_date = False if func in ['训练模型', '离群值识别', '简报'] else True
    minimum = False if func in ['训练模型'] else True
    size = False if func in ['离群值识别'] else True
    delta = False if func in ['训练模型', '离群值识别', '简报'] else True
    return btn_add, end_date, minimum, size, delta

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
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
    try:
        username = current_user.username
    except:
        username = 'timed_task_test'
    job_start_time = _make_sure_datetime_string(job_start_time)
    status = 'pause'
    if job_start_date is None:
        job_start_time = pd.Timestamp.now().strftime(_DATE_TIME_FORMAT)
    else:
        job_start_time = job_start_date + ' ' + job_start_time[11:]
        
    task_parameter = {'misfire_grace_time':600}
    if setting=='interval':
        task_parameter.update({unit:interval})
    
    end_time = end_date+' 00:00:00' if end_date is not None and end_date!='' else ''
    function_parameter = dict(
        end_time = end_time,
        delta = delta,
        size = size,
        minimum =minimum
        )
    
    RSDBInterface.insert(
        dict(
            status=status,
            func=_FUNC_DCT[func],
            setting=setting,
            start_time=job_start_time,
            task_parameter=f'{task_parameter}',
            function_parameter=f'{function_parameter}',
            username=username,
            create_time=pd.Timestamp.now()
            ),
        'timed_task'
        )
    return _render_table()

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
        df = pd.DataFrame(data).iloc[rows]
        status = df['状态'].iloc[0]
        if status=='start':
            rev = [True, False, False]
        elif status=='pause':
            rev = [False, True, False]
    return rev

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open'),
    Output(f'{_PREFIX}_alert', 'children'),
    Output(f'{_PREFIX}_alert', 'color'),
    Input(f'{_PREFIX}_btn_start', 'n_clicks'),
    Input(f'{_PREFIX}_btn_pause', 'n_clicks'),
    Input(f'{_PREFIX}_btn_delete', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_start_pause_delete(n1, n2, n3, rows, data):  
    df = pd.DataFrame(data).iloc[rows]
    _id = ctx.triggered_id
    for _,row in df.iterrows():
        exist=False
        # 考虑超时会导致scheduler丢失mysql连接，重试2次，让其恢复
        for i in range(2):
            response = requests.get(_URL+f"/{row['id']}")
            if response.reason=='OK':
                exist = True
                break
            time.sleep(0.1)
        if _id==f'{_PREFIX}_btn_start':
            if exist:
                response = requests.post(_URL+f"/{row['id']}/resume")
            else:
                task_parameter = eval(row['任务参数'])
                funtion_parameter = eval(row['目标函数参数'])
                funtion_parameter.update({"task_id":row['id']})
                key_ = 'run_date' if row['设定']=='date' else 'start_date'
                kwargs = {
                    'id':f"{row['id']}", 
                    'func':row['目标函数'], 
                    'trigger':row['设定'],
                    key_:row['设定执行时间'],
                    'kwargs':funtion_parameter,
                    }
                kwargs.update(task_parameter)
                response = requests.post(_URL, json=kwargs)
            status = 'start'
        elif _id==f'{_PREFIX}_btn_pause':
            response = requests.post(_URL+f"/{row['id']}/pause")
            status = 'pause'
        else:
            response = requests.delete(_URL+f"/{row['id']}")
            status = 'delete'
        if response.ok==False and pd.Series(response.text).str.match('.*Job .* not found').all() == False:
            rev_aug = [True, f"操作失败：task_id={row['id']}, code={response.status_code}, response={response.text}", 'danger']
            return [_render_table()] + rev_aug
        RSDBInterface.update('timed_task', {'status':status}, eq_clause={'id':row['id']})         
    rev_aug = [True, f"操作成功", 'success']
    return [_render_table()] + rev_aug


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