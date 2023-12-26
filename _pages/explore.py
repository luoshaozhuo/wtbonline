# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:28:04 2023

@author: luosz

探索页面
"""
# =============================================================================
# import
# ============================================================================
from distutils.sysconfig import PREFIX
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from dash_iconify import DashIconify

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools.plot import simple_plot
from wtbonline._pages.tools._decorator import _on_error
from wtbonline._pages.tools.utils import mapid_to_tid, read_raw_data
from wtbonline._pages.common.notification import SUCCESS, FAILED, get_notification

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'explore' 
_ACCORDION_ITEMS = {
    '时序图':{'y轴坐标':f'{_PREFIX}_dropdown_timeseries_y',
           'y2轴坐标':f'{_PREFIX}_dropdown_timeseries_y2'},
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
            dmc.Select(
                id=item_dct[i],
                label=i,
                searchable=True,
                style={"width": '100%'},
                icon=DashIconify(icon="radix-icons:magnifying-glass"),
                rightSection=DashIconify(icon="radix-icons:chevron-down"),
                )
            )
    rev = dmc.Group(content)
    return dbc.AccordionItem(rev, title=title)

def _get_side_bar():
    content = []
    for i in _ACCORDION_ITEMS:
        content.append(_get_accordion_item(_ACCORDION_ITEMS[i], i))
    return dbc.Accordion(content, id=f'{_PREFIX}_accordion', flush=True)

def _get_card_plot():
    card = dbc.Card([dbc.CardHeader('绘图区'),
                     dbc.CardBody([
                        dbc.Button(html.I(className='bi bi-arrow-repeat'), 
                            id=f'{_PREFIX}_btn_refresh',
                            disabled=True, 
                            size='sm',
                            className='btn-primary'),
                         dmc.LoadingOverlay(
                            dcc.Graph(id=f'{_PREFIX}_plot',
                                    config={'displaylogo':False})
                            )                        
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
                             ], className='mb-2'),
                         dbc.Collapse(
                             dash_table.DataTable(
                                 id=f'{_PREFIX}_datatable',
                                 columns=[{'name': i, 'id': i} for i in 
                                          ['图例号', '机型编号', '风机编号', '开始日期时间', '结束日期时间']],                           
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
            dbc.ModalHeader(dbc.ModalTitle('添加分析对象', class_name='fs-5')),
            dbc.ModalBody([
                dmc.Select(
                    label="机型编号",
                    placeholder="Select one",
                    searchable=True,
                    id=f'{_PREFIX}_dropdown_set_id',
                    size='sm',
                    style={"width": '100%', "marginBottom": 10},
                    ),
                dmc.Select(
                    label="机组编号",
                    placeholder="Select one",
                    searchable=True,
                    id=f'{_PREFIX}_dropdown_map_id',
                    size='sm',
                    style={"width": '100%', "marginBottom": 10},
                    ),
                dmc.DatePicker(
                    id=f'{_PREFIX}_start_date',
                    placeholder = 'Select one',
                    label="起始日期",
                    size='sm',
                    style={"width": '100%'},
                    ),
                dmc.TimeInput(
                    id=f'{_PREFIX}_start_time',
                    label="起始时间",
                    size='sm',
                    style={"width": '100%'},
                    ),
                dmc.NumberInput(
                    id=f'{_PREFIX}_hours',
                    label="数据长度（小时）",
                    size='sm',
                    description="整数，最小值1，最大值5。",
                    value=5,
                    min=1,
                    style={"width": '100%'},
                    )
                ]), 
            dbc.ModalFooter([
                dmc.Button(
                    '确定', 
                    id=f'{_PREFIX}_btn_confirm', 
                    className='btn-primary me-2', 
                    n_clicks=0,
                    disabled=True,
                    size='xs'
                    ),
                dmc.Button(
                    '取消', 
                    id=f'{_PREFIX}_btn_cancel', 
                    className='btn-secondary', 
                    n_clicks=0,
                    size='xs'
                    )
                ]), 
            ], 
    id=f'{_PREFIX}_modal', 
    size="sm",
    is_open=False
    )

def get_layout():
    layout = [
        _get_modle_dialog(),
        dmc.NotificationsProvider(html.Div(id=f'{_PREFIX}_notification_container')), 
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
def on_explore_show_table(n, is_open):
    ''' 显示选定分析对象表格 '''
    return not is_open 

@callback(
    Output(f'{_PREFIX}_modal', 'is_open', allow_duplicate=True),
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    prevent_initial_call=True    
)
@_on_error
def on_explore_open_dialog(n):
    return True

@callback(
    Output(f'{_PREFIX}_modal', 'is_open'),
    Input(f'{_PREFIX}_btn_confirm', 'n_clicks'),
    Input(f'{_PREFIX}_btn_cancel', 'n_clicks'),
    prevent_initial_call=True    
)
@_on_error
def on_explore_close_dialog(n1, n2):
    return False

@callback(
    Output(f'{_PREFIX}_dropdown_set_id', 'data'),
    Output(f'{_PREFIX}_dropdown_set_id', 'value'), 
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_update_set_id(n):
    df = RSDBInterface.read_windfarm_configuration()
    set_id_lst = df['set_id'].unique().tolist()
    data=value=no_update
    if len(set_id_lst)>0:
        data = [{'value':i, 'label':i} for i in set_id_lst]
        value = set_id_lst[0]
    return data, value

@callback(
    Output(f'{_PREFIX}_dropdown_map_id', 'data'),
    Output(f'{_PREFIX}_dropdown_map_id', 'value'), 
    Input(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_update_map_id(set_id):
    df = RSDBInterface.read_windfarm_configuration()
    data=value=no_update
    if set_id is not None:
        map_id_lst = df['map_id'].unique().tolist()
        if len(map_id_lst)>0:
            data = [{'value':i, 'label':i} for i in map_id_lst]
            value = map_id_lst[0]
    return data, value


@callback(
    Output(f'{_PREFIX}_datatable', 'data'),
    Input(f'{_PREFIX}_btn_confirm', 'n_clicks'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),   
    State(f'{_PREFIX}_hours', 'value'),   
    prevent_initial_call=True
    )
@_on_error
def on_explore_update_table(n, set_id, map_id, obj_lst, start_date, start_time, hours):
    obj_lst = [] if obj_lst is None else obj_lst
    start_time = _make_sure_datetime_string(start_time)
    start_time = start_date+start_time[10:]
    end_time = pd.to_datetime(start_time)+pd.Timedelta(f'{hours}h')
    end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    obj_lst.append({'图例号':'*', '机型编号':set_id, '风机编号':map_id, 
                    '开始日期时间':start_time, '结束日期时间':end_time})
    df = pd.DataFrame(obj_lst, index=np.arange(len(obj_lst)))
    df.drop_duplicates(['机型编号','风机编号','开始日期时间','结束日期时间'], inplace=True)
    df['图例号'] = [f't_{i}' for i in np.arange(df.shape[0])]
    return df.to_dict('records')

@callback(
    Output(f'{_PREFIX}_btn_confirm', 'disabled'),
    Input(f'{_PREFIX}_start_date', 'value'),
    Input(f'{_PREFIX}_start_time', 'value'),    
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_date_range(start_date, start_time, set_id, map_id):
    return  None in (start_date, start_time, set_id, map_id)


@callback(
    Output(f'{_PREFIX}_start_date', 'minDate'),
    Output(f'{_PREFIX}_start_date', 'maxDate'),
    Output(f'{_PREFIX}_start_date', 'disabledDates'),  
    Output(f'{_PREFIX}_start_date', 'value'),
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_dropdown_map_id(map_id, set_id): 
    turbine_id = mapid_to_tid(set_id, map_id=map_id)
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
    return min_date, max_date, disabled_days, None
    
    
@callback(
    Output(f'{_PREFIX}_dropdown_timeseries_y', 'data'),
    Output(f'{_PREFIX}_dropdown_timeseries_y2', 'data'),
    Output(f'{_PREFIX}_dropdown_scatter_x', 'data'),
    Output(f'{_PREFIX}_dropdown_scatter_y', 'data'),
    Output(f'{_PREFIX}_dropdown_radar_theta', 'data'),
    Output(f'{_PREFIX}_dropdown_radar_r', 'data'),
    Output(f'{_PREFIX}_dropdown_spectrum_y', 'data'),
    Output(f'{_PREFIX}_dropdown_timeseries_y', 'value'),
    Output(f'{_PREFIX}_dropdown_timeseries_y2', 'value'),
    Output(f'{_PREFIX}_dropdown_scatter_x', 'value'),
    Output(f'{_PREFIX}_dropdown_scatter_y', 'value'),
    Output(f'{_PREFIX}_dropdown_radar_theta', 'value'),
    Output(f'{_PREFIX}_dropdown_radar_r', 'value'),
    Output(f'{_PREFIX}_dropdown_spectrum_y', 'value'),
    Input(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True
    )
@_on_error
def explore_update_dropdown_selection_variables(data_dct):
    if len(data_dct)>0:
        set_ids = pd.DataFrame(data_dct)['机型编号'].unique()
        # 选出所有机型表格中所有机型共有的变量
        cols = ['point_name', 'unit', 'set_id', 'datatype']
        model_point_df = RSDBInterface.read_turbine_model_point(set_id=set_ids, columns=cols, select=[0, 1])
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
        return [timeseries_y, timeseries_y, scatter_x, scatter_y, radar_theta, radar_r, spectrum_y]+[None]*7
    else:
        return [[]]*7+[None]*7
       

@callback(
    Output(f'{_PREFIX}_btn_refresh', 'disabled'),
    Input(f'{_PREFIX}_datatable', 'data'),
    Input(f'{_PREFIX}_accordion', 'active_item'),
    Input(f'{_PREFIX}_dropdown_timeseries_y', 'value'),
    Input(f'{_PREFIX}_dropdown_scatter_x', 'value'),
    Input(f'{_PREFIX}_dropdown_scatter_y', 'value'),
    Input(f'{_PREFIX}_dropdown_radar_theta', 'value'),
    Input(f'{_PREFIX}_dropdown_radar_r', 'value'),
    Input(f'{_PREFIX}_dropdown_spectrum_y', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_enable_btn_refresh(table_lst, item, ts_y, sct_x, sct_y, rad_th, rad_r, spc_y):
    empty_table = not (isinstance(table_lst, (list, tuple)) and len(table_lst)>0)
    plot_type = list(_ACCORDION_ITEMS.keys())[int(item.split('-')[1])]
    if plot_type=='时序图':
        # 必须指定ts_y，可以不指定ts_y2
        vars = [ts_y]
    elif plot_type=='散点图':
        vars = [sct_x, sct_y]
    elif plot_type=='雷达图':
        vars = [rad_th, rad_r]
    elif plot_type=='频谱图':
        vars = [spc_y]
    not_enough_var = None in vars
    return empty_table or not_enough_var


@callback(
    Output(f'{_PREFIX}_plot', 'figure'),
    Output(f'{_PREFIX}_notification_container', "children", allow_duplicate=True),  
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_accordion', 'active_item'),
    State(f'{_PREFIX}_dropdown_timeseries_y', 'value'),
    State(f'{_PREFIX}_dropdown_timeseries_y2', 'value'),
    State(f'{_PREFIX}_dropdown_scatter_x', 'value'),
    State(f'{_PREFIX}_dropdown_scatter_y', 'value'),
    State(f'{_PREFIX}_dropdown_radar_theta', 'value'),
    State(f'{_PREFIX}_dropdown_radar_r', 'value'),
    State(f'{_PREFIX}_dropdown_spectrum_y', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_btn_refresh(n1, table_lst, item, ts_y, ts_y2, sct_x, sct_y, rad_th,
                            rad_r, spc_y):
    ''' 点击刷新按钮，绘制图形 '''
    plot_type = list(_ACCORDION_ITEMS.keys())[int(item.split('-')[1])]
    message = ''

    # 设置绘图参数
    xtitle=''
    y2col=None
    if plot_type=='时序图':
        xcol = 'ts'
        ycol = ts_y
        y2col = ts_y2
        mode = 'markers+lines'
        _type = 'line'
        xtitle = '时间'
    elif plot_type=='散点图':
        xcol = sct_x
        ycol = sct_y
        _type = 'scatter'
        mode = 'markers'
    elif plot_type=='雷达图':
        xcol = rad_th
        ycol = rad_r
        _type = 'polar'
        mode = 'markers'
    elif plot_type=='频谱图':
        xcol = 'ts'
        ycol = spc_y
        _type = 'spectrum'
        mode = 'markers+lines'
        xtitle = '频率Hz'
    
    # 读取绘图数据
    x_lst=[]    
    y_lst=[]
    y2_lst=[]
    name_lst=[]
    ref_freqs=[]
    ytitle=''
    y2title=''
    point_name = tuple(pd.Series([xcol, ycol, y2col]).replace('ts', None).dropna())
    sample_cnt = int(50000/len(table_lst))
    for dct in table_lst:
        try:
            df, desc_df = read_raw_data(
                set_id=dct['机型编号'], 
                map_id=dct['风机编号'], 
                point_name=point_name, 
                start_time=dct['开始日期时间'],
                end_time=dct['结束日期时间'],
                sample_cnt=sample_cnt,
                remote=True
                )
        except:
            message = f"查询数据失败 {dct['机型编号']} {dct['风机编号']} {dct['开始日期时间']} {point_name}"
            break
        if len(df)<1:
            message = f"数据集为空 {dct['机型编号']} {dct['风机编号']} {dct['开始日期时间']} {point_name}"
            break
        name_lst.append(dct['图例号'])
        x = df[xcol].tolist() if xcol=='ts' else df[desc_df.loc[xcol, 'var_name']].tolist()
        x_lst.append(x)
        if ycol is not None:
            y = df[desc_df.loc[ycol, 'var_name']].tolist()
            y_lst.append(y)
            xtitle = desc_df.loc[xcol, 'column'] if xtitle=='' else xtitle
            if ytitle=='':
                if _type == 'spectrum':
                    ytitle = ycol + f"_({desc_df.loc[ycol, 'unit']})^2"
                else:
                    ytitle = desc_df.loc[ycol, 'column']
        if y2col is not None:
            y2 = df[desc_df.loc[y2col, 'var_name']].tolist()
            y2_lst.append(y2)
            if y2title=='':
                if _type == 'spectrum':
                    y2title = ycol + f"_({desc_df.loc[y2col, 'unit']})^2"
                else:
                    y2title = desc_df.loc[y2col, 'column']
        else:
            y2_lst.append(None)
                    
    fig = simple_plot(
        x_lst=x_lst, 
        y_lst=y_lst, 
        y2_lst=y2_lst,
        xtitle=xtitle, 
        ytitle=ytitle,
        y2title=y2title,
        name_lst=name_lst,
        mode=mode,
        _type=_type,
        ref_freqs=ref_freqs,
        )
    if message == '':
        notify = no_update
    else:
        notify = get_notification(_PREFIX, FAILED, message)
    return fig, notify

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