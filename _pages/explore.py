# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:28:04 2023

@author: luosz

探索页面
"""
# =============================================================================
# import
# ============================================================================
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools.plot import simple_plot
from wtbonline._pages.tools._decorator import _on_error
from wtbonline._pages.tools.utils import mapid_to_tid, read_raw_data

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'explore' 
_ACCORDION_ITEMS = {
    '时序图':{'y轴坐标':f'{_PREFIX}_dropdown_timeseries_y'},
    '散点图':{'x轴坐标':f'{_PREFIX}_dropdown_scatter_x', 
           'y轴坐标':f'{_PREFIX}_dropdown_scatter_y'},
    '雷达图':{'θ轴坐标':f'{_PREFIX}_dropdown_radar_theta',
           'r轴坐标':f'{_PREFIX}_dropdown_radar_r'},
    '频谱图':{'y轴坐标':f'{_PREFIX}_dropdown_spectrum_y'},
    } 

# =============================================================================
# layout
# =============================================================================
def _make_sure_datetime_string(x):
    if x is None:
        x = '0000000000T00:00:00'
    return x

def _get_accordion_item(item_dct, title):
    content = []
    for i in item_dct:
        content.append(
            dbc.InputGroup(
                [
                    dbc.InputGroupText(i, class_name='small'),
                    dbc.Select(id=item_dct[i],class_name='small')
                ],
                className='mb-4'
                )
            )
    
    return dbc.AccordionItem(content, title=title)

def _get_side_bar():
    content = []
    for i in _ACCORDION_ITEMS:
        content.append(_get_accordion_item(_ACCORDION_ITEMS[i], i))
    return dbc.Accordion(content, id=f'{_PREFIX}_accordion', flush=True)

def _get_card_plot():
    card = dbc.Card([dbc.CardHeader('绘图区'),
                     dbc.CardBody([
                         dcc.Graph(id=f'{_PREFIX}_plot',
                                   config={'displaylogo':False})
                         ])
                     ]),
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))

def _get_card_select():
    card = dbc.Card([dbc.CardHeader('机组号及日期范围'),
                     dbc.CardBody([
                         html.Div([
                             dbc.Button(html.I(className='bi bi-arrows-expand'), 
                                        id=f'{_PREFIX}_btn_collapse',
                                        size='sm',
                                        className='btn-secondary me-2 '),
                             dbc.Button('＋', 
                                        id=f'{_PREFIX}_btn_add',
                                        size='sm',
                                        className='btn-primary me-2'),
                             dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                                        id=f'{_PREFIX}_btn_refresh',
                                        size='sm',
                                        className='btn-primary'),
                             ], className='mb-2'),
                         dbc.Collapse(
                             dash_table.DataTable(
                                 id=f'{_PREFIX}_datatable',
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
                             id=f'{_PREFIX}_collapse',
                             is_open=False,
                             )     
                         ])
                     ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))


def _get_modle_dialog():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle('添加分析对象', class_name='fs-4')),
            dbc.ModalBody([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('机型编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_set_id',
                            class_name='small',
                            )
                        ],
                    className='mb-4'
                    ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('风机编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_map_id',
                            class_name='small',
                            )
                        ],
                    className='mb-4'
                    ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("开始日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_start_date', size='md', clearable =False),
                        dbc.InputGroupText("时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_start_time', size='md'),
                        ], 
                    className='w-100'
                    ),
                html.Br(),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("结束日期", class_name='small'),
                        dmc.DatePicker(id=f'{_PREFIX}_end_date', size='md', clearable =False),
                        dbc.InputGroupText("时间", class_name='small'),
                        dmc.TimeInput(id=f'{_PREFIX}_end_time', size='md'),
                        ], 
                    className='w-100'
                    ),
                ]), 
            dbc.ModalFooter([
                dbc.Button(
                    '确定', 
                    id=f'{_PREFIX}_btn_confirm', 
                    className='btn-primary me-2', 
                    n_clicks=0,
                    disabled=True,
                    size='sm'
                    ),
                dbc.Button(
                    '取消', 
                    id=f'{_PREFIX}_btn_cancel', 
                    className='btn-secondary', 
                    n_clicks=0,
                    size='sm'
                    )
                ]), 
            ], 
    id=f'{_PREFIX}_modal', 
    is_open=False
    )

def get_layout():
    layout = [
        _get_modle_dialog(),
        dbc.Alert(id=f'{_PREFIX}_alert', color='danger', duration=3000, is_open=False, className='border rounded-0'),
        dbc.Row([dbc.Col(_get_side_bar(), 
                        width=2, 
                        className='border-end h-100'),
                 dbc.Col([
                          dbc.Container(_get_card_select(), 
                                        fluid=True,
                                        className='m-0'),                                                 
                          dbc.Container(_get_card_plot(),
                                        fluid=True,
                                        className='m-0')
                            ],
                         width=10,
                         className='h-100')
                 ],
                className='g-0 h-100'
                )
        ]
    return layout

# =============================================================================
# callback
# =============================================================================
@callback(
    Output(f'{_PREFIX}_collapse', 'is_open'),
    Input(f'{_PREFIX}_btn_collapse', 'n_clicks'),
    State(f'{_PREFIX}_collapse', 'is_open'),
    prevent_initial_call=True
)
@_on_error
def on_explore_btn_collapse(n, is_open):
    ''' 显示选定分析对象表格 '''
    return not is_open 

@callback(
    Output(f'{_PREFIX}_modal', 'is_open'),
    Output(f'{_PREFIX}_dropdown_set_id', 'options'),
    Output(f'{_PREFIX}_dropdown_set_id', 'value'),
    Output(f'{_PREFIX}_dropdown_map_id', 'options'),
    Output(f'{_PREFIX}_dropdown_map_id', 'value'),
    Output(f'{_PREFIX}_datatable', 'data'),
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    Input(f'{_PREFIX}_btn_confirm', 'n_clicks'),
    Input(f'{_PREFIX}_btn_cancel', 'n_clicks'),
    Input(f'{_PREFIX}_dropdown_set_id', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    Input(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),    
    State(f'{_PREFIX}_end_date', 'value'),
    State(f'{_PREFIX}_end_time', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_dialog(n1, n2, n3, set_id, map_id, obj_lst, start_date, start_time, end_date, end_time):
    ''' 显示/隐藏添加分析对象对话框，更新分析对象数据 '''
    _id = ctx.triggered_id
    # 点击增加，打开对话框，修改set_id及map_id的可选项以及默认值
    if _id==f'{_PREFIX}_btn_add':
        df = RSDBInterface.read_windfarm_configuration()
        # set_id
        set_id_lst = df['set_id'].unique().tolist()
        option_set_id = [{'label':i} for i in set_id_lst]
        set_id = set_id_lst[0]
        # map_id
        map_id_lst = df['map_id'].unique().tolist()
        option_map_id = [{'label':i} for i in map_id_lst]
        map_id = map_id_lst[0]
        rev = [True, option_set_id, set_id, option_map_id, map_id, no_update]
    # 选择新set_id后，变更map_id可选项以及默认值
    elif _id==f'{_PREFIX}_dropdown_set_id':
        map_id_lst = df['map_id'].unique().tolist()
        option_map_id = [{'label':i} for i in map_id_lst]
        map_id = map_id_lst[0]
        rev = [no_update, no_update, no_update, option_map_id, map_id, no_update]
    # 点击对话框里的确定按钮，关闭对话框，更新系列列表
    elif _id==f'{_PREFIX}_btn_confirm':
        obj_lst = [] if obj_lst is None else obj_lst
        start_time = _make_sure_datetime_string(start_time)
        end_time = _make_sure_datetime_string(end_time)
        obj_lst.append({'图例号':'*', '机型编号':set_id, '风机编号':map_id, 
                        '开始日期':start_date+start_time[10:], '结束日期':end_date+end_time[10:]})
        df = pd.DataFrame(obj_lst, index=np.arange(len(obj_lst)))
        df.drop_duplicates(['机型编号','风机编号','开始日期','结束日期'], inplace=True)
        df['图例号'] = [f't_{i}' for i in np.arange(df.shape[0])]
        rev = [False, no_update, no_update, no_update, no_update, df.to_dict('records')]
    elif _id==f'{_PREFIX}_btn_cancel':
        rev =  [False, no_update, no_update, no_update, no_update, no_update]
    else:
        rev =  [no_update, no_update, no_update, no_update, no_update, no_update]
    return rev

@callback(
    Output(f'{_PREFIX}_end_date', 'error', allow_duplicate=True),
    Output(f'{_PREFIX}_end_time', 'error', allow_duplicate=True),
    Output(f'{_PREFIX}_btn_confirm', 'disabled'),
    Input(f'{_PREFIX}_start_date', 'value'),
    Input(f'{_PREFIX}_start_time', 'value'),    
    Input(f'{_PREFIX}_end_date', 'value'),
    Input(f'{_PREFIX}_end_time', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_date_range(start_date, start_time, end_date, end_time, set_id, map_id):
    if None in [set_id, map_id, start_date, end_date]:
        rev = [no_update, no_update, True]
    else:
        start_time = _make_sure_datetime_string(start_time)
        end_time = _make_sure_datetime_string(end_time)
        start_dt = end_date + start_time[10:]
        end_dt = start_date + end_time[10:]
        if start_dt <= end_dt:
            rev = [True, True, True]
        else:
            rev = [False, False, False]
    return rev


@callback(
    Output(f'{_PREFIX}_start_date', 'minDate'),
    Output(f'{_PREFIX}_start_date', 'maxDate'),
    Output(f'{_PREFIX}_start_date', 'disabledDates'),  
    Output(f'{_PREFIX}_start_date', 'value'),
    Output(f'{_PREFIX}_end_date', 'minDate'),
    Output(f'{_PREFIX}_end_date', 'maxDate'),
    Output(f'{_PREFIX}_end_date', 'disabledDates'),  
    Output(f'{_PREFIX}_end_date', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_dropdown_turbine_id(map_id, set_id): 
    turbine_id = mapid_to_tid(set_id, map_id=map_id)
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, 
        turbine_id=turbine_id,
        func_dct={'bin':['date']},
        unique=True,
        )
    dates = df['bin_date'].squeeze()
    min_date = dates.min()
    max_date = dates.max()
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    rev = [min_date, max_date, disabled_days, None]
    rev += [min_date, max_date, disabled_days, None]
    return rev
    
       
@callback(
    Output(f'{_PREFIX}_dropdown_timeseries_y', 'options'),
    Output(f'{_PREFIX}_dropdown_scatter_x', 'options'),
    Output(f'{_PREFIX}_dropdown_scatter_y', 'options'),
    Output(f'{_PREFIX}_dropdown_radar_theta', 'options'),
    Output(f'{_PREFIX}_dropdown_radar_r', 'options'),
    Output(f'{_PREFIX}_dropdown_spectrum_y', 'options'),
    Input(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_table(data_dct):
    if len(data_dct)>0:
        set_ids = pd.DataFrame(data_dct)['机型编号'].unique()
        # 选出所有机型表格中所有机型共有的变量
        cols = ['point_name', 'unit', 'set_id', 'datatype']
        model_point_df = RSDBInterface.read_turbine_model_point(set_id=set_ids, select=1, columns=cols)
        count = model_point_df.groupby('point_name')['set_id'].count()
        count = count[count==len(set_ids)]
        model_point_df.set_index('point_name', inplace=True)
        model_point_df=model_point_df.loc[count.index, ].reset_index()
        model_point_df.drop_duplicates(subset=['point_name'], inplace=True)
        
        timeseries_y = model_point_df['point_name']
        scatter_x = model_point_df['point_name']
        scatter_y = model_point_df['point_name']
        radar_theta = model_point_df['point_name'][
            (model_point_df['point_name'].str.find('角')>-1) & 
            (model_point_df['unit']=='°')
            ]
        radar_r = model_point_df[model_point_df['datatype']=='F']['point_name']
        spectrum_y = model_point_df[model_point_df['datatype']=='F']['point_name']
        return timeseries_y, scatter_x, scatter_y, radar_theta, radar_r, spectrum_y
    else:
        return [None]*6

@callback(
    Output(f'{_PREFIX}_plot', 'figure'),
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'color', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_accordion', 'active_item'),
    State(f'{_PREFIX}_dropdown_timeseries_y', 'value'),
    State(f'{_PREFIX}_dropdown_scatter_x', 'value'),
    State(f'{_PREFIX}_dropdown_scatter_y', 'value'),
    State(f'{_PREFIX}_dropdown_radar_theta', 'value'),
    State(f'{_PREFIX}_dropdown_radar_r', 'value'),
    State(f'{_PREFIX}_dropdown_spectrum_y', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_btn_refresh(n1, table_lst, item, ts_y, sct_x, sct_y, rad_th,
                            rad_r, spc_y):
    ''' 点击刷新按钮，绘制图形 '''
    if table_lst is None or len(table_lst)<1:
        return [no_update]*3
    plot_type = list(_ACCORDION_ITEMS.keys())[int(item.split('-')[1])]
    _type = 'scatter'
    rev_error = [no_update, '未指定绘图变量', True, 'danger']
    xtitle=''
    if plot_type=='时序图':
        if ts_y is None:
            return rev_error
        xcol = 'ts'
        ycol = ts_y
        mode = 'markers+lines'
        xtitle = '时间'
    elif plot_type=='散点图':
        if sct_x is None or sct_y is None:
            return rev_error
        xcol = sct_x
        ycol = sct_y
        mode = 'markers'
    elif plot_type=='雷达图':
        if rad_th is None or rad_r is None:
            return rev_error
        xcol = rad_th
        ycol = rad_r
        _type = 'polar'
        mode = 'markers'
    elif plot_type=='频谱图':
        if spc_y is None:
            return rev_error
        xcol = 'ts'
        ycol = spc_y
        _type = 'spectrum'
        mode = 'markers+lines'
        xtitle = '频率Hz'
    
    x_lst=[]    
    y_lst=[]
    name_lst=[]
    ref_freqs=[]
    ytitle=''
    point_name = pd.Series([xcol, ycol]).replace('ts', None).dropna()
    for dct in table_lst:
        df, desc_df = read_raw_data(
            set_id=dct['机型编号'], 
            map_id=dct['风机编号'], 
            point_name=point_name, 
            start_time=dct['开始日期'],
            end_time=dct['结束日期'],
            )
        name_lst.append(dct['图例号'])
        x = df[xcol].tolist() if xcol=='ts' else df[desc_df.loc[xcol, 'var_name']].tolist()
        y = df[desc_df.loc[ycol, 'var_name']].tolist()
        x_lst.append(x)
        y_lst.append(y)
        xtitle = desc_df.loc[xcol, 'column'] if xtitle=='' else xtitle
        if ytitle=='':
            if _type == 'spectrum':
                ytitle = ycol + f"_({desc_df.loc[ycol, 'unit']})^2"
            else:
                ytitle = desc_df.loc[ycol, 'column']
        
    fig = simple_plot(
        x_lst=x_lst, 
        y_lst=y_lst, 
        xtitle=xtitle, 
        ytitle=ytitle,
        name_lst=name_lst,
        mode=mode,
        _type=_type,
        ref_freqs=ref_freqs,
        )
    return fig, no_update, no_update, no_update

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