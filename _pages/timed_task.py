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

from wtbonline._pages.tools._decorator import _on_error
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.rsdb.dao import RSDB
    
# =============================================================================
# constant
# =============================================================================
_PREFIX = 'task'
_COLUMNS = ['id', '状态', '目标函数', '设定', '参数', '下次运行时间', '最近运行结果',  '发布者']
_FUNC_DCT = { 
    "初始化数据库":"wtbonline._db.init_tdengine:init_tdengine",
    "原始数据ETL":"wtbonline._process.preprocess:update_tsdb",
    "数据统计":"wtbonline._process.statistic:update_statistic_sample",
    "训练模型":"wtbonline._process.modelling:train_all",
    "离群值识别":"wtbonline._process.modelling:predict_all",
    "简报":"wtbonline._report.brief_report:build_brief_report_all",
    }
_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_URL='scheduler:40000/scheduler/jobs'

# =============================================================================
# function
# =============================================================================
def _make_sure_datetime_string(x):
    if x is None:
        x = '0000000000T00:00:00'
    return x

def read_task_table():
    # ['id', '状态', '目标函数', '设定', '参数', '下次运行时间', '最近运行结果',  '发布者']
    sql='''
        select e.id, e.status, e.func, e.setting, e.parameter, f.next_run_time, e.success, e.username from apscheduler_jobs f
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
    return RSDB.read_sql(sql)

def _render_table():
    df = read_task_table()
    df.columns = _COLUMNS
    data = df.to_dict('records')
    tooltip_data=[
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in data
        ]
    return data, tooltip_data

# =============================================================================
# layout
# =============================================================================
def _setting():
    return dbc.Card([
            dbc.CardHeader('任务管理'),
            dbc.CardBody([
            dbc.ButtonGroup([
                dbc.Button(html.I(className='bi bi-plus-circle'),  
                            id=f'{_PREFIX}_btn_add', 
                            className='btn-primary',
                            disabled=True, 
                            n_clicks=0,
                            ),
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
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    },
                tooltip_duration=None
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
                        dmc.DatePicker(id=f'{_PREFIX}_next_run_date', size='sm', clearable =False, placeholder='不填代表立即执行一次'),
                        ], 
                    className='w-100'
                    ), 
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("运行时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_next_run_time', size='sm'),
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
                    dbc.InputGroupText("周期"), 
                    dmc.NumberInput(id=f'{_PREFIX}_interval', size="md", min=1, value=1, style={"width":100}, disabled=True),
                    dbc.InputGroupText("天"), 
                    ]),
                html.Hr(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("截止日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_end_date', size='sm', clearable =False, value=pd.Timestamp.now().date(), disabled=True),
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
    Input(f'{_PREFIX}_setting', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_change_setting(setting):
    rev = True if setting=='一次性任务' else False
    return rev

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
    Output(f'{_PREFIX}_datatable', 'tooltip_data', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    State(f'{_PREFIX}_func', 'value'),
    State(f'{_PREFIX}_next_run_date', 'value'),
    State(f'{_PREFIX}_next_run_time', 'value'),
    State(f'{_PREFIX}_setting', 'value'),
    State(f'{_PREFIX}_interval', 'value'),
    State(f'{_PREFIX}_end_date', 'value'),
    State(f'{_PREFIX}_minimum', 'value'),
    State(f'{_PREFIX}_size', 'value'),
    State(f'{_PREFIX}_delta', 'value'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_add(n, func, next_run_date, next_run_time, setting, interval, end_date, minimun, size, delta):
    try:
        username = current_user.username
    except:
        username = 'timed_task_test'
    create_time = pd.Timestamp.now()
    next_run_time = _make_sure_datetime_string(next_run_time)
    status = 'pause'
    if next_run_date is None:
        next_run_time = pd.Timestamp.now().strftime(_DATE_TIME_FORMAT)
    else:
        next_run_time = next_run_date + next_run_time[11:]
    
    parameter = {'next_run_time':next_run_time, 'misfire_grace_time':600}
    if setting=='interval':
        parameter.update({'interval':interval})
    if func in ['训练模型', '离群值识别', '简报']:
        parameter.update({'end_time': end_date+' 00:00:00'})
    if func in ['训练模型']:
        parameter.update({'minimun': minimun})
    if func in ['离群值识别']:
        parameter.update({'size': size})
    if func in ['简报']:
        parameter.update({'delta': delta})
    if func in ['训练模型', '离群值识别']:
        start_time = pd.to_datetime(end_date) - pd.Timedelta(f'{delta}d')     
        parameter.update({'start_time': start_time.strftime(_DATE_TIME_FORMAT)})

    RSDBInterface.insert(
        dict(
            status=status,
            func=_FUNC_DCT[func],
            setting=setting,
            parameter=f'{parameter}',
            username=username,
            create_time=create_time
            ),
        'timed_task'
        )
    return _render_table()

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'tooltip_data', allow_duplicate=True),
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
    )
@_on_error
def timed_task_select_rows(rows):
    rev = True if rows is None or rows=='' or len(rows)<1 else False
    return [rev]*3

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'tooltip_data', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_start', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_start(n, rows, data):
    df = pd.DataFrame(data).iloc[rows]
    for _,row in df.iterrows():
        data_object = {'id':row['id'], 'func':row['目标函数'], 'trigger':row['设定']}
        parameter = eval(row['参数'])
        if row['设定'] == 'date':
            parameter['next_run_time'] = max(pd.Timestamp.now(), pd.to_datetime(parameter['next_run_time']))
        data_object.update(parameter)
        rev = requests.post(_URL, data=data_object)
        if isinstance(rev, list):
            ...
        else:
            rev_aug = [True, f"开始任务失败，id={row['id']}", 'danger']
            break
        RSDBInterface.update({'status':'start'}, eq_clause=row['id'])         
    return list(_render_table()) + rev_aug

@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'tooltip_data', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_pause', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_pause(n, rows, data):
    df = pd.DataFrame(data).iloc[rows]
    for _,row in df.iterrows():
        rev = requests.post(_URL+f'/{row[id]}/pause')
        if isinstance(rev, list):
            ...
        else:
            rev_aug = [True, f"暂停任务失败，id={row['id']}", 'danger']
            break
        RSDBInterface.update({'status':'pause'}, eq_clause=row['id']) 
    return list(_render_table()) + rev_aug


@callback(
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'tooltip_data', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open'),
    Output(f'{_PREFIX}_alert', 'chldren'),
    Output(f'{_PREFIX}_alert', 'color'),
    Input(f'{_PREFIX}_btn_delete', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True,
    )
@_on_error
def timed_task_on_btn_delete(n, rows, data):
    df = pd.DataFrame(data).iloc[rows]
    for _,row in df.iterrows():
        rev = requests.delete(_URL+f'/{row[id]}')
        if isinstance(rev, list):
            ...
        else:
            rev_aug = [True, f"删除任务失败，id={row['id']}", 'danger']
            break
        RSDBInterface.update({'status':'delete'}, eq_clause=row['id']) 
    return list(_render_table()) + rev_aug

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