# -*- coding: utf-8 -*-
'''
Created on Mon May 15 12:24:50 2023

@author: luosz

分析页面
'''
# =============================================================================
# import
# =============================================================================)
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table, ALL, MATCH
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px 

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools._decorator import _on_error
from wtbonline._plot.figure import PowerCurve

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'analyse' 

SIDEBAR_DF = pd.DataFrame([['性能', '功率曲线', 'powercurve', 1, 1],
                           ['性能', '功率差异', 'pitch_control', 1, 2],
                           ['故障', '齿轮箱', 'gearbox', 2, 1],
                           ['故障', '发电机', 'generator', 2, 2],
                           ['故障', '变流器', 'converter', 2, 3],
                           ['故障', '叶片', 'blade', 2, 4],
                           ['故障', '叶轮', 'hub', 2, 5],
                           ['故障', '超发', 'overpower', 2, 6],
                           ['安全', '叶片净空', 'clearance', 3, 1],
                           ['安全', '塔顶振动', 'vibration', 3, 2],
                           ['可靠性', '可靠性', 'safety', 4, 1]],
                          columns=['category', 'name', 'id', 'order', 'suborder'])


# =============================================================================
# layour
# =============================================================================
def _get_side_bar():
    class_name = 'border border-0 bg-transparent text-primary text-start'
    rev = []
    for _,grp in SIDEBAR_DF.groupby('order'):
        temp = []
        for _,row in grp.sort_values('suborder').iterrows():
            temp.append(dbc.Button(children=row['name'], 
                                   id={'main':f'{_PREFIX}_sidebar', 'sub':row['id']}, 
                                   className=class_name))
        rev.append(dbc.AccordionItem(html.Div(temp, className='d-grid pad-0'),
                                     title=row['category']))
    rev = dbc.Accordion(rev, flush=True)
    return rev                    

def _card_comparison():
    ''' 用于做横向纵向对比的设置选项卡 '''
    card = dbc.Card([dbc.CardHeader('机组号及日期范围'),
                     dbc.CardBody([
                         _modle_dialog_comparison(),
                         html.Div([
                             dbc.Button(html.I(className='bi bi-arrows-expand'), 
                                        id=f'{_PREFIX}_btn_collapse_cmp',
                                        size='sm',
                                        className='btn-secondary me-2 '),
                             dbc.Button('＋', 
                                        id=f'{_PREFIX}_btn_add_cmp',
                                        size='sm',
                                        className='btn-primary me-2'),
                             dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                                        id=f'{_PREFIX}_btn_refresh_cmp',
                                        size='sm',
                                        className='btn-primary'),
                             ], className='mb-2'),
                         dbc.Collapse(
                             dash_table.DataTable(
                                 id=f'{_PREFIX}_datatable_cmp',
                                 columns=[{'name': i, 'id': i} for i in 
                                          ['图例号', '机型编号', '风机编号', '开始日期', '结束日期']],                           
                                 row_deletable=True,
                                 selected_columns=[],
                                 selected_rows=[],
                                 page_action='native',
                                 page_current= 0,
                                 page_size= 10,
                                 style_header = {'font-weight':'bold'},
                                 style_table = {'font-size':'small'}
                                 ),
                             id=f'{_PREFIX}_collapse_cmp',
                             is_open=False,
                             )     
                         ])
                     ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))


def _modle_dialog_comparison():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle('添加分析对象', class_name='fs-4')),
            dbc.ModalBody([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('机型编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_set_id_cmp',
                            class_name='small',
                            )
                        ],
                    className='mb-4'
                    ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('风机编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_map_id_cmp',
                            class_name='small',
                            )
                        ],
                    className='mb-4'
                    ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("开始日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_start_date_cmp', size='md', clearable =False),
                        dbc.InputGroupText("时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_start_time_cmp', size='md', value='2022-02-02 00:00:00'),
                        ], 
                    className='w-100'
                    ),
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("结束日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_end_date_cmp', size='md', clearable =False),
                        dbc.InputGroupText("时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_end_time_cmp', size='md', value='2022-02-02 00:00:00'),
                        ], 
                    className='w-100'
                    ),
                ]), 
            dbc.ModalFooter([
                dbc.Button(
                    '确定', 
                    id=f'{_PREFIX}_btn_confirm_cmp', 
                    className='btn-primary me-2', 
                    n_clicks=0,
                    disabled=True,
                    size='sm'
                    ),
                dbc.Button(
                    '取消', 
                    id=f'{_PREFIX}_btn_cancel_cmp', 
                    className='btn-secondary', 
                    n_clicks=0,
                    size='sm'
                    )
                ]), 
            ], 
    id=f'{_PREFIX}_modal_cmp', 
    is_open=False
    )
    

def _get_card_plot():
    card = dbc.Card([
        dbc.CardHeader('可视化'),
        dbc.CardBody(
            dmc.LoadingOverlay(
                dcc.Graph(
                    id=f'{_PREFIX}_plot',
                    config={'displaylogo':False})
                )
            )
        ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))


def get_layout():
    layout = [
              dbc.Alert(id=f"{_PREFIX}_alert", color = 'danger', duration=3000, is_open=False),
              dcc.Store(data='powercurve', 
                        id=f'{_PREFIX}_store_sidebar', 
                        storage_type='session'),
              dbc.Row(
                  [dbc.Col(_get_side_bar(), 
                           width=2, 
                           className='border-end h-100'),
                   dbc.Col(
                       [dbc.Container(id=f"{_PREFIX}_setting",
                                      fluid=True,
                                      className='m-0'),
                        dbc.Container(_get_card_plot(), 
                                      fluid=True,
                                      className='m-0'
                                      )
                       ],width=10,className='h-100')
                   ], 
                  className='g-0 h-100')
              ]
    return layout

# =============================================================================
# layout
# =============================================================================
@callback(
    Output(f'{_PREFIX}_setting', 'children'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_contianer_setting(n):
    sub = ctx.triggered_id['sub']
    if sub=='powercurve':
        rev = _card_comparison()
    elif sub in ('gearbox', 'generator', 'converter', 'blade', 'hub', 'overpower'):
        rev = ''
    else:
        rev = ''
    return rev

@callback(
    Output(f'{_PREFIX}_store_sidebar', 'data'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_store_sidebar(n):
    return ctx.triggered_id['sub']

@callback(
    Output(f'{_PREFIX}_plot', 'figure'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': 'powercurve'}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_sidbar_powercurv(n):
    return {}


# =============================================================================
# 参数设定区相应函数————对比分析
# =============================================================================
@callback(
    Output(f'{_PREFIX}_collapse_cmp', 'is_open'),
    Input(f'{_PREFIX}_btn_collapse_cmp', 'n_clicks'),
    State(f'{_PREFIX}_collapse_cmp', 'is_open'),
    prevent_initial_call=True
)
@_on_error
def on_analyse_btn_collapse_cmp(n, is_open):
    ''' 显示选定分析对象表格 '''
    return not is_open 


@callback(
    Output(f'{_PREFIX}_modal_cmp', 'is_open'),
    Output(f'{_PREFIX}_dropdown_set_id_cmp', 'options'),
    Output(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'options'),
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'value'),
    Output(f'{_PREFIX}_datatable_cmp', 'data'),
    Input(f'{_PREFIX}_btn_add_cmp', 'n_clicks'),
    State(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    State(f'{_PREFIX}_dropdown_map_id_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_btn_add_cmp(n, set_id, map_id):
    df = RSDBInterface.read_windfarm_configuration()
    # set_id
    set_id_lst = df['set_id'].unique().tolist()
    option_set_id = [{'label':i} for i in set_id_lst]
    set_id = set_id_lst[0]
    # map_id
    map_id_lst = df['map_id'].unique().tolist()
    option_map_id = [{'label':i} for i in map_id_lst]
    map_id = map_id_lst[0]
    return [True, option_set_id, set_id, option_map_id, map_id, no_update]


@callback(
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'options', allow_duplicate=True),
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'value', allow_duplicate=True),
    Input(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_change_set_id_cmp(set_id):
    df = RSDBInterface.read_windfarm_configuration()
    map_id_lst = df['map_id'].unique().tolist()
    option_map_id = [{'label':i} for i in map_id_lst]
    return option_map_id, map_id_lst[0]


@callback(
    Output(f'{_PREFIX}_modal_cmp', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_datatable_cmp', 'data', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_confirm_cmp', 'n_clicks'),
    Input(f'{_PREFIX}_btn_cancel_cmp', 'n_clicks'),
    State(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    State(f'{_PREFIX}_dropdown_map_id_cmp', 'value'),
    State(f'{_PREFIX}_datatable_cmp', 'data'),
    State(f'{_PREFIX}_start_date_cmp', 'value'),
    State(f'{_PREFIX}_start_time_cmp', 'value'),    
    State(f'{_PREFIX}_end_date_cmp', 'value'),
    State(f'{_PREFIX}_end_time_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_dialog_cancel_and_confirm_cmp(n1, n2, set_id, map_id, obj_lst, start_date, start_time, end_date, end_time):
    _id = ctx.triggered_id
    if _id==f'{_PREFIX}_btn_confirm_cmp':
        obj_lst = [] if obj_lst is None else obj_lst
        obj_lst.append({'图例号':'*', '机型编号':set_id, '风机编号':map_id, 
                        '开始日期':start_date+start_time[10:], '结束日期':end_date+end_time[10:]})
        df = pd.DataFrame(obj_lst, index=np.arange(len(obj_lst)))
        df.drop_duplicates(['机型编号','风机编号','开始日期','结束日期'], inplace=True)
        df['图例号'] = [f't_{i}' for i in np.arange(df.shape[0])]
        tbl = df.to_dict('records')
    else:
        tbl = no_update
    return False, tbl

@callback(
    Output(f'{_PREFIX}_end_date_cmp', 'error', allow_duplicate=True),
    Output(f'{_PREFIX}_end_time_cmp', 'error', allow_duplicate=True),
    Output(f'{_PREFIX}_btn_confirm_cmp', 'disabled'),
    Input(f'{_PREFIX}_start_date_cmp', 'value'),
    Input(f'{_PREFIX}_start_time_cmp', 'value'),    
    Input(f'{_PREFIX}_end_date_cmp', 'value'),
    Input(f'{_PREFIX}_end_time_cmp', 'value'),
    State(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    State(f'{_PREFIX}_dropdown_map_id_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_change_date_range_cmp(start_date, start_time, end_date, end_time, set_id, map_id):
    if None in [set_id, map_id, start_date, end_date, start_time, end_time]:
        rev = [no_update, no_update, True]
    else:
        start_dt = pd.to_datetime(start_date + start_time[10:])
        end_dt = pd.to_datetime(end_date + end_time[10:])
        if start_dt > end_dt:
            rev = [True, True, True]
        else:
            rev = [False, False, False]
    return rev


@callback(
    Output(f'{_PREFIX}_start_date_cmp', 'minDate'),
    Output(f'{_PREFIX}_start_date_cmp', 'maxDate'),
    Output(f'{_PREFIX}_start_date_cmp', 'disabledDates'),  
    Output(f'{_PREFIX}_start_date_cmp', 'value'),
    Output(f'{_PREFIX}_end_date_cmp', 'minDate'),
    Output(f'{_PREFIX}_end_date_cmp', 'maxDate'),
    Output(f'{_PREFIX}_end_date_cmp', 'disabledDates'),  
    Output(f'{_PREFIX}_end_date_cmp', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id_cmp', 'value'),
    State(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_change_dropdown_map_id_cmp(map_id, set_id): 
    turbine_id = RSDBInterface.read_windfarm_configuration(map_id=map_id)['turbine_id'].squeeze()
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, 
        turbine_id=turbine_id,
        func_dct={'bin':['date']},
        unique=True,
        )
    if len(df)>0:
        dates = df['bin_date'].squeeze()
        min_date = dates.min()
        max_date = dates.max()
    else:
        now = pd.Timestamp.now()
        min_date = (now - pd.Timedelta('1d')).date()
        max_date = now.date()
        dates = []
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    rev = [min_date, max_date, disabled_days, None]
    rev += [min_date, max_date, disabled_days, None]
    return rev


# =============================================================================
# 绘图区的相应函数
# =============================================================================
@callback(
    Output(f'{_PREFIX}_plot', 'figure', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_refresh_cmp', 'n_clicks'),
    State(f'{_PREFIX}_datatable_cmp', 'data'),
    State(f'{_PREFIX}_store_sidebar', 'data'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_btn_refresh_cmp(n, value_lst, sub):
    if value_lst is None or len(value_lst)==0 or not (sub in ['powercurve']):
        return no_update
    df = pd.DataFrame(value_lst, columns=['图例号', '机型编号', '风机编号', '开始日期', '结束日期'])
    if sub == 'powercurve':
        ret = PowerCurve(df).fig
    else:
        ret = {}   
    return ret



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