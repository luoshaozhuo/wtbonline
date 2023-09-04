# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 14:22:56 2023

@author: luosz

账户管理页面
"""

# =============================================================================
# import
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

from dash import html, Input, Output, no_update, callback, State, ctx, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd

from _database import _mysql as msql
from _database import model
from _pages.tools._decorator import _on_error
    
# =============================================================================
# constant
# =============================================================================
_PREFIX = 'task'

# =============================================================================
# layout
# =============================================================================
def _card_body():
    rev = [
        dbc.InputGroup(
            [dbc.InputGroupText("任务名称"), 
             dbc.Input(id=f'{_PREFIX}_name', placeholder='Taskname'),
             dbc.InputGroupText("任务类型"), 
             dbc.Select(
                 id=f'{_PREFIX}_type',
                 value='分析报告',
                 options=[{"label":"分析报告", "value":"分析报告"},
                          {"label":"载荷谱", "value":"载荷谱"}],
                 ),
             dbc.InputGroupText("周期"),
             dbc.Input(id=f'{_PREFIX}_period', placeholder="period"),
             dbc.InputGroupText("天", class_name='text-secondary'),
             dbc.InputGroupText("窗宽"),
             dbc.Input(id=f'{_PREFIX}_window', placeholder="window"),
             dbc.InputGroupText("天", class_name='text-secondary'),
             dbc.InputGroupText("开始日期"),
             dmc.DatePicker(
                 id=f'{_PREFIX}_start_date',
                 size='md',
                 clearable=False,
                 inputFormat='YYYY-MM-DD',
                 classNames={'input':'border rounded-0'}
                 ),  
             dbc.InputGroupText("开始时间"),
             dbc.Input(type='time', id=f'{_PREFIX}_start_time'),
             dbc.InputGroupText("重复"),
             dbc.Input(id=f'{_PREFIX}_repeat', placeholder="-1 代表永久生效"),
             dbc.InputGroupText("次", class_name='text-secondary'),
            ],
            className="mb-3",
            ),
        html.Hr(),
        dbc.ButtonGroup([
             dbc.Button(html.I(className='bi bi-plus-circle'),  
                        id=f'{_PREFIX}_btn_add', 
                        className='btn-primary', 
                        n_clicks=0,
                        ),
             dbc.Button(html.I(className='bi bi-play'),  
                        id=f'{_PREFIX}_btn_start', 
                        className='btn-success', 
                        n_clicks=0,
                        ),
             dbc.Button(html.I(className='bi bi-stop-circle'),  
                        id=f'{_PREFIX}_btn_stop', 
                        className='btn-danger', 
                        n_clicks=0,
                        ),
             dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                        id=f'{_PREFIX}_btn_refresh', 
                        className='btn-info', 
                        n_clicks=0,
                        ),
            ],
            size='sm',
            class_name='mb-2'),
        dash_table.DataTable(
            id=f'{_PREFIX}_datatable',
            columns=[{'name': i, 'id': i} for i in 
                     ['图例号', '机型编号', '风机编号', '开始日期', '结束日期']],                           
            row_deletable=False,
            row_selectable="single",
            page_action='native',
            page_current= 0,
            page_size= 10,
            style_header = {'font-weight':'bold'},
            style_table = {'font-size':'small'}
            ),
       ]
    return rev     

def get_layout():
    layout = html.Div([
        dbc.Alert(id=f'{_PREFIX}_alert', color='danger', duration=3000, is_open=False, className='border rounded-0'),
        *_card_body(),
        ], className='w-100 p-3')
    return layout

# =============================================================================
# callback
# =============================================================================
@callback(
    Output(f'{_PREFIX}_datatable', 'data'),
    Output(f'{_PREFIX}_datatable', 'columns'),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    )
@_on_error
def on_timed_task_btn_refresh(n):
    df = msql.read_timed_task()
    columns=[{'name': i, 'id': i} for i in df.columns] 
    return df.to_dict('records'), columns

@callback(
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'color', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'columns', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    State(f'{_PREFIX}_name', 'value'),
    State(f'{_PREFIX}_type', 'value'),
    State(f'{_PREFIX}_period', 'value'),
    State(f'{_PREFIX}_window', 'value'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),
    State(f'{_PREFIX}_repeat', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_timed_task_update_add(n, name, _type, period, window, start_date, 
                             start_time, repeat):
    if None in (name, _type, period, window, start_date, start_time, repeat):
        return '任务参数不完整', True, 'danger', no_update, no_update
    create_time = pd.Timestamp.now()
    start_time = start_date + ' ' + start_time + ':00'
    df = pd.DataFrame({'name':name, 'status':'start', 'type':_type,
                       'period':period, 'window':window, 'start_time':start_time,
                       'repeat':repeat, 'create_time':create_time},
                      index=[1])
    msql.insert(df, model.TimedTask, keys=['name'])
    
    df = msql.read_timed_task()
    columns=[{'name': i, 'id': i} for i in df.columns]     
    return '已添加任务', True, 'success', df.to_dict('records'), columns

@callback(
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'color', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable', 'columns', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_start', 'n_clicks'),
    Input(f'{_PREFIX}_btn_stop', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'selected_rows'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_timed_task_change_task_status(n1, n2, sel_row, tbl):
    # raise ValueError(sel_row, tbl)
    if sel_row is None or len(sel_row)<1:
        return '未选中任何记录', True, 'danger', no_update, no_update
    
    try:
        _id = ctx.triggered_id
    except:
        _id = f'{_PREFIX}_btn_start'
    
    status = 'start' if _id==f'{_PREFIX}_btn_start' else 'stop' 
    sr = pd.Series({'id':tbl[sel_row[0]]['id'], 'status':status})
    msql.update_one(sr, 'id', model.TimedTask)
    
    df = msql.read_timed_task()
    columns=[{'name': i, 'id': i} for i in df.columns]     
    return '已修改任务状态', True, 'success', df.to_dict('records'), columns


# =============================================================================
# for test
# =============================================================================
if __name__ == '__main__':
    import dash
    app = dash.Dash(__name__, 
                    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
                    suppress_callback_exceptions=True)
    app.layout = html.Div(get_layout())
    debug = True if len(sys.argv)>1 else False
    app.run_server(debug=debug)