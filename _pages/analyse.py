# -*- coding: utf-8 -*-
'''
Created on Mon May 15 12:24:50 2023

@author: luosz

分析页面
'''
# =============================================================================
# import
# =============================================================================)
import pstats
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table, ALL, MATCH
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from matplotlib.pyplot import cla
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from wtbonline._db.common import make_sure_datetime 

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools._decorator import _on_error
from wtbonline._pages.tools import utils 
from wtbonline._process.tools.common import get_all_table_tags
import wtbonline._plot as plt

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'analyse' 

SIDEBAR_DF = pd.DataFrame(
    [
        ['性能', '功率曲线', 'powercurve', 1, 1, plt.PowerCurve],
        ['性能', '功率差异', 'power_difference', 1, 2, plt.PowerCompare],
        ['故障', '齿轮箱关键参数超限', '齿轮箱关键参数超限', 2, 1, plt.Gearbox],
        ['故障', '发电机关键参数超限', '发电机关键参数超限', 2, 2, plt.GeneratorOverloaded],
        ['故障', '变流器关键参数超限', '变流器关键参数超限', 2, 3, plt.Convertor],
        ['故障', '风轮方位角异常', '风轮方位角异常', 2, 4, plt.HubAzimuth],
        ['故障', '叶片桨距角不同步', '叶片桨距角不同步', 2, 5, plt.BladeAsynchronous],
        ['故障', '叶根摆振弯矩超限', '叶根摆振弯矩超限', 2, 6, plt.BladeOverloaded],
        ['故障', '叶根摆挥舞矩超限', '叶根摆挥舞矩超限', 2, 6, plt.BladeOverloaded],
        ['故障', '叶根载荷不平衡', '叶根载荷不平衡', 2, 7, plt.BladeUnblacedLoad],
        ['故障', '叶片pitchkick', '叶片pitchkick', 2, 8, plt.BladePitchkick],
        ['安全', '叶片净空', 'clearance', 3, 1, None],
        ['安全', '塔顶振动', 'vibration', 3, 2, None],
        ['通用质量特性', '可靠性', 'reliability', 4, 1, None],
        ['通用质量特性', '可维修性', 'maintainability', 4, 1, None],
        ['通用质量特性', '保障性', 'supportability', 4, 1, None]
        ],
    columns=['category', 'name', 'id', 'order', 'suborder', 'graph_cls']
    )

FAULT_TYPE =  RSDBInterface.read_turbine_fault_type().set_index('name')

# =============================================================================
# layour
# =============================================================================
def uic_dropdown(title, var_name, suffix, options=None, className=None):
    return dbc.InputGroup(
        [
            dbc.InputGroupText(title, class_name='small'),
            dbc.Select(
                id=f'{_PREFIX}_dropdown_{var_name}_{suffix}',
                options=options,
                class_name='small',
                )
            ],
        className = 'mb-4' if className is None else className
        )
    
def uic_dropdown_map_id(suffix, className=None):
    return uic_dropdown('机组编号', 'map_id', suffix, options=None, className=className)
    
    
def uic_dropdown_set_id(suffix, className=None):
    df = RSDBInterface.read_windfarm_configuration(columns='set_id')
    tags_df = get_all_table_tags().rename(columns={'device':'turbine_id'})
    df = pd.merge(df, tags_df, how='inner')

    lst = df['set_id'].unique().tolist()
    options = [{'label':i} for i in lst]
    return uic_dropdown('机型编号', 'set_id', suffix, options=options, className=className)
    
    
def uic_datetime_picker(title, suffix_date, suffix_time):
    return dbc.InputGroup(
        [
            dbc.InputGroupText(title, class_name='small'),
            dmc.DatePicker(id=f'{_PREFIX}_{suffix_date}', size='md', clearable =False),
            dbc.InputGroupText("时间", class_name='small'),
            dmc.TimeInput(id=f'{_PREFIX}_{suffix_time}', size='md', value='2022-02-02 00:00:00'),
            ], 
        className='w-100'
        )

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

def _card_fault():
    ''' 用于故障分析的选项卡 '''
    card = dbc.Card([
        dbc.CardHeader('机组号及日期范围'),
        dbc.CardBody([
            html.Div(
                [
                    uic_dropdown_set_id('fault', className='w-25'),
                    uic_dropdown_map_id('fault', className='w-25'),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText('日期', class_name='small'),
                            dmc.DatePicker(id=f'{_PREFIX}_date_fault', size='md', clearable =False, value=None),  
                            dbc.InputGroupText("开始时间", class_name='small'),
                            dmc.TimeInput(id=f'{_PREFIX}_start_time_fault', size='md', value='2022-02-02T00:00:00'),
                            dbc.InputGroupText("结束时间", class_name='small'),
                            dmc.TimeInput(id=f'{_PREFIX}_end_time_fault', size='md', value='2022-02-02T23:59:00'),
                            ],
                        ),
                    ], 
                className ='hstack gap-3')
            ])
        ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))

def _card_comparison():
    ''' 用于做横向纵向对比的设置选项卡 '''
    card = dbc.Card([
        dbc.CardHeader('机组号及日期范围'),
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
                uic_dropdown_set_id('cmp'),
                uic_dropdown_map_id('cmp'),
                uic_datetime_picker('开始日期', 'start_date_cmp', 'start_time_cmp'),
                html.Br(),
                uic_datetime_picker('结束日期', 'end_date_cmp', 'end_time_cmp'),
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
        dbc.CardBody([
            dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                    id=f'{_PREFIX}_btn_refresh',
                    size='sm',
                    disabled=True,
                    className='btn-primary'),
            dmc.LoadingOverlay(
                dcc.Graph(
                    id=f'{_PREFIX}_graph',
                    config={'displaylogo':False},
                    className='overflow-auto',
                    style={"maxHeight": 700}
                    )
                )
            ])
        ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))


def get_layout():
    layout = [
        dbc.Alert(id=f"{_PREFIX}_alert", color = 'danger', duration=3000, is_open=False),
        dcc.Store(
            data=None, 
            id=f'{_PREFIX}_store_sidebar_item_component', 
            storage_type='session'
            ),
        dcc.Store(
            data=None, 
            id=f'{_PREFIX}_store_talbe_lst', 
            storage_type='session'
            ),
        dcc.Store(
            data=None, 
            id=f'{_PREFIX}_store_data_dct', 
            storage_type='session'
            ),
        dbc.Row(
            [
                dbc.Col(_get_side_bar(), width=2,  className='border-end h-100'),
                dbc.Col(
                    [
                        dbc.Container(id=f"{_PREFIX}_setting",
                                    fluid=True,
                                    className='m-0'),
                        # 绘图区是共用的
                        dbc.Container(
                            _get_card_plot(),
                            id=f"{_PREFIX}_graph_area",
                            fluid=True,
                            className='m-0',
                            )
                        ],
                    width=10,
                    className='h-100'
                    )
                ], 
            className='g-0 h-100'
            )
        ]
    return layout

# =============================================================================
# 侧边栏响应函数
# =============================================================================
@callback(
    Output(f'{_PREFIX}_setting', 'children'),
    Output(f'{_PREFIX}_graph_area', 'children'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_change_setting_card(n):
    sub = ctx.triggered_id['sub']
    new_cat = SIDEBAR_DF[SIDEBAR_DF['id']==sub]['category'].iloc[0]
    if new_cat == '性能':
             card = _card_comparison()
    elif new_cat == '故障':
        card = _card_fault()
    else:
        card = ''
    return card, _get_card_plot()

@callback(
    Output(f'{_PREFIX}_store_sidebar_item_component', 'data'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_store_sidebar_item_component(n):
    # 点击侧边栏选项卡时，记录下当前选择的栏目
    return ctx.triggered_id['sub']

@callback(
    Output(f'{_PREFIX}_store_data_dct', 'data', allow_duplicate=True),
    Output(f'{_PREFIX}_store_talbe_lst', 'data', allow_duplicate=True),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_clear_store_data(n):
    return None, None

# =============================================================================
# 参数设定区响应函数————对比分析
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
    Input(f'{_PREFIX}_btn_add_cmp', 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_btn_add_cmp(n):
    return True

@callback(
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'options', allow_duplicate=True),
    Output(f'{_PREFIX}_dropdown_map_id_cmp', 'value', allow_duplicate=True),
    Input(f'{_PREFIX}_dropdown_set_id_cmp', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_change_set_id_cmp(set_id):
    if set_id is None:
        return [], None
    df = RSDBInterface.read_windfarm_configuration()
    tags_df = get_all_table_tags().rename(columns={'device':'turbine_id'})
    df = pd.merge(df, tags_df, how='inner')
    
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
        if start_dt >= end_dt:
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
        value = max_date
    else:
        now = pd.Timestamp.now()
        min_date = (now - pd.Timedelta('1d')).date()
        max_date = now.date()
        dates = []
        value = None
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    rev = [min_date, max_date, disabled_days, value]
    rev += [min_date, max_date, disabled_days, value]
    return rev


# 由于动态生成页面元素，且公用refresh按钮，所需需要通过store对象来存储绘图设置列表，避免
# component不存在的错误
@callback(
    Output(f'{_PREFIX}_store_talbe_lst', 'data'),
    Input(f'{_PREFIX}_datatable_cmp', 'data'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_store_table_lst(value_lst):
    return value_lst


# =============================================================================
# 参数设定区响应函数————故障分析
# =============================================================================
@callback(
    Output(f'{_PREFIX}_dropdown_map_id_fault', 'options', allow_duplicate=True),
    Output(f'{_PREFIX}_dropdown_map_id_fault', 'value', allow_duplicate=True),
    Input(f'{_PREFIX}_dropdown_set_id_fault', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_on_change_set_id_fault(set_id):
    if set_id is None:
        return [], None
    df = RSDBInterface.read_windfarm_configuration(set_id=set_id)
    tags_df = get_all_table_tags().rename(columns={'device':'turbine_id'})
    df = pd.merge(df, tags_df, how='inner')
    
    map_id_lst = df['map_id'].unique().tolist()
    option_map_id = [{'label':i} for i in map_id_lst]
    return option_map_id, map_id_lst[0]

@callback(
    Output(f'{_PREFIX}_date_fault', 'minDate'),
    Output(f'{_PREFIX}_date_fault', 'maxDate'),
    Output(f'{_PREFIX}_date_fault', 'disabledDates'),  
    Output(f'{_PREFIX}_date_fault', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id_fault', 'value'),
    State(f'{_PREFIX}_dropdown_set_id_fault', 'value'),
    State(f'{_PREFIX}_store_sidebar_item_component', 'data'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_date_picker_fault(map_id, set_id, fault_type): 
    if None in (map_id, set_id, fault_type):
        return [None]*4
    fault_id = FAULT_TYPE.loc[fault_type, 'id']
    turbine_id = utils.mapid_to_tid(set_id=set_id, map_id=map_id)
    df = RSDBInterface.read_statistics_fault(set_id=set_id, turbine_id=turbine_id, fault_id=fault_id)
    if len(df)>0:
        dates = df['date'].squeeze()
        min_date = dates.min()
        max_date = dates.max()
        value = max_date
    else:
        now = pd.Timestamp.now()
        min_date = (now - pd.Timedelta('1d')).date()
        max_date = now.date()
        value = None
        dates = []
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    rev = [min_date, max_date, disabled_days, value]
    return rev

@callback(
    Output(f'{_PREFIX}_start_time_fault', 'value'),    
    Output(f'{_PREFIX}_end_time_fault', 'value'),
    Input(f'{_PREFIX}_date_fault', 'value'),
    State(f'{_PREFIX}_dropdown_set_id_fault', 'value'),
    State(f'{_PREFIX}_dropdown_map_id_fault', 'value'),
    State(f'{_PREFIX}_store_sidebar_item_component', 'data'),
    State(f'{_PREFIX}_start_time_fault', 'value'),    
    State(f'{_PREFIX}_end_time_fault', 'value'),
    prevent_initial_call=True
    )
@_on_error
def analyse_change_date_fault(date, set_id, map_id, fault_type, start_time, end_time):
    if date is None:
        return [None]*2
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)
    date = pd.to_datetime(date)
    # 若修改了日期，则讲开始、结束时间重置为故障前后15分钟
    fault_id = FAULT_TYPE.loc[fault_type, 'id']
    turbine_id = utils.mapid_to_tid(set_id, map_id)
    df = RSDBInterface.read_statistics_fault(set_id=set_id, turbine_id=turbine_id, date=date, fault_id=fault_id)
    if len(df)<1:
        start_time=end_time=no_update
    else:
        start_time = df['timestamp'].iloc[0] - pd.Timedelta('15m')
        # 有可能会是前一天
        if start_time.date() < date.date():
            start_time = '1999-01-01 00:00:00'
        end_time = df['timestamp'].iloc[0] + pd.Timedelta('15m')
        # 有可能是后一天
        if end_time.date() > date.date():
            end_time =  '1999-01-01 23:59:00'
    return start_time, end_time

@callback(
    Output(f'{_PREFIX}_store_data_dct', 'data'),
    Input(f'{_PREFIX}_dropdown_set_id_fault', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id_fault', 'value'),
    Input(f'{_PREFIX}_date_fault', 'value'),
    Input(f'{_PREFIX}_start_time_fault', 'value'),
    Input(f'{_PREFIX}_end_time_fault', 'value'),
    )
@_on_error
def analyse_update_store_data_dct(set_id, map_id, date, start_time, end_time):
    if None in (set_id, map_id, date, start_time, end_time):
        return None
    rev = dict(
        set_id=set_id, 
        map_id=map_id, 
        start_time=f'{date}T{start_time[11:]}',
        end_time=f'{date}T{end_time[11:]}', 
        name=None
        )
    return rev

# =============================================================================
# 绘图区
# =============================================================================
# 控制栏区中所有信息都有值，refresh按钮可用，否则禁用，下面两组函数更新对象相同，但是
# Input不一样。它们不可以合并在一起，因为Input并不是同时存在。
@callback(
    Output(f'{_PREFIX}_btn_refresh', 'disabled', allow_duplicate=True),
    Input(f'{_PREFIX}_datatable_cmp', 'data'),
    prevent_initial_call=True 
    )
@_on_error
def analyse_update_ui_btn_refresh_fault(data):
    return data is None

@callback(
    Output(f'{_PREFIX}_btn_refresh', 'disabled'),
    Input(f'{_PREFIX}_dropdown_set_id_fault', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id_fault', 'value'),
    Input(f'{_PREFIX}_date_fault', 'value'),
    Input(f'{_PREFIX}_start_time_fault', 'value'),
    Input(f'{_PREFIX}_end_time_fault', 'value'),
    prevent_initial_call=True 
    )
@_on_error
def analyse_update_ui_btn_refresh_cmp(set_id, map_id, date, start_time, end_time):
    if None in (set_id, map_id, date, start_time, end_time):
        return True
    if start_time[11:] >= end_time[11:]:
        return True
    return False


# 根据导航栏大类绘制图形
@callback(
    Output(f'{_PREFIX}_graph', 'figure'),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    State(f'{_PREFIX}_store_sidebar_item_component', 'data'),
    State(f'{_PREFIX}_store_talbe_lst', 'data'),
    State(f'{_PREFIX}_store_data_dct', 'data'),
    prevent_initial_call=True
    )
@_on_error
def analyse_update_graph(n, item, value_lst, data_dct):    
    cat = SIDEBAR_DF[SIDEBAR_DF['id']==item]['category'].iloc[0]
    if cat=='性能':
        columns=['图例号', '机型编号', '风机编号', '开始日期', '结束日期']
        data = pd.DataFrame(value_lst, columns=columns)
    elif cat=='故障':
        data = data_dct
    else:
        data = None
        
    if data is None or len(data)<1:
        rev = {}
    else:
        rev = SIDEBAR_DF.set_index('id').loc[item, 'graph_cls'](data, title=item).figs[0]
    return rev


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