# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:28:04 2023

@author: luosz

探索页面
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

from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from _pages.tools.plot import line_plot, anormaly_plot, _power_spectrum
from _database import _mysql as msql
from _database import _tdengine as td
from _database import model
from _pages.tools._decorator import _on_error

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
    return dbc.Modal([dbc.ModalHeader(dbc.ModalTitle('添加分析对象', class_name='fs-4')),
                      dbc.ModalBody([
                          dbc.InputGroup(
                              [dbc.InputGroupText('机型编号', class_name='small'),
                               dbc.Select(
                                   id=f'{_PREFIX}_dropdown_set_id',
                                   class_name='small',
                                   )],
                              className='mb-4'
                              ),
                          dbc.InputGroup(
                              [dbc.InputGroupText('风机编号', class_name='small'),
                               dbc.Select(
                                   id=f'{_PREFIX}_dropdown_map_id',
                                   class_name='small',
                                   )],
                              className='mb-4'
                              ),
                          dbc.InputGroup(
                                 [dbc.InputGroupText('开始时间', class_name='small'),
                                  dmc.DatePicker(
                                        id=f'{_PREFIX}_start_date',
                                        size='md',
                                        clearable=False,
                                        inputFormat='YYYY-MM-DD',
                                        classNames={'input':'border rounded-0'}
                                    ),
                                  dbc.Input(type='time', id=f'{_PREFIX}_start_time')],
                                 className='mb-4'
                                 ),
                          dbc.InputGroup(
                                 [dbc.InputGroupText('结束时间', class_name='small'),
                                  dmc.DatePicker(
                                        id=f'{_PREFIX}_end_date',
                                        size='md',
                                        clearable=False,
                                        inputFormat='YYYY-MM-DD',
                                        classNames={'input':'border rounded-0'}
                                    ),
                                  dbc.Input(type='time', id=f'{_PREFIX}_end_time')],
                                 className='mb-4'
                                 ),
                          ]), 
                      dbc.ModalFooter([
                          dbc.Button(
                              '确定', 
                              id=f'{_PREFIX}_btn_confirm', 
                              className='btn-primary me-2', 
                              n_clicks=0,
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
                      ], id=f'{_PREFIX}_modal', is_open=False)

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
    Output(f'{_PREFIX}_alert', 'children'),
    Output(f'{_PREFIX}_alert', 'is_open'),
    Input(f'{_PREFIX}_btn_add', 'n_clicks'),
    Input(f'{_PREFIX}_btn_confirm', 'n_clicks'),
    Input(f'{_PREFIX}_btn_cancel', 'n_clicks'),
    Input(f'{_PREFIX}_dropdown_set_id', 'value'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),
    State(f'{_PREFIX}_end_date', 'value'),
    State(f'{_PREFIX}_end_time', 'value'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_explore_dialog(n1, n2, n3, set_id, start_date, start_time, end_date, end_time, map_id, obj_lst):
    ''' 显示/隐藏添加分析对象对话框，更新分析对象数据 '''
    _id = ctx.triggered_id
    # 点击增加，打开对话框，修改set_id及map_id的可选项以及默认值
    if _id==f'{_PREFIX}_btn_add':
        df = msql.read_windfarm_configuration()
        # set_id
        set_id_lst = msql.get_available_set_id()
        option_set_id = [{'label':i} for i in set_id_lst]
        set_id = set_id_lst[0]
        # map_id
        map_id_lst = msql.get_available_map_id(set_id)
        option_map_id = [{'label':i} for i in map_id_lst]
        map_id = map_id_lst[0]
        return True, option_set_id, set_id, option_map_id, map_id, *[no_update]*3
    # 选择新set_id后，变更map_id可选项以及默认值
    elif _id==f'{_PREFIX}_dropdown_set_id':
        map_id_lst = msql.get_available_map_id(set_id)
        option_map_id = [{'label':i} for i in map_id_lst]
        map_id = map_id_lst[0]
        return no_update, no_update, no_update, option_map_id, map_id, *[no_update]*3
    # 点击对话框里的确定按钮，关闭对话框，更新系列列表
    elif _id==f'{_PREFIX}_btn_confirm':
        turbine_id = msql.map_id_to_turbine_id(set_id, map_id)
        sr = msql.read_statistics_accumulattion(set_id=set_id,turbine_id=turbine_id)
        sr = sr.squeeze()
        # 组合时间日期
        start_time = '00:00:00' if start_time is None else start_time+':00'
        end_time = '00:00:00' if end_time is None else end_time+':00'
        start_date = '1997-07-01' if start_date is None else start_date
        start_date += f' {start_time}'
        end_date = '1997-07-01' if end_date is None else end_date
        end_date += f' {end_time}'
        if end_date <= start_date:
            return *[no_update]*6, '结束日期需要大于开始日期', True
        # 构造表格内容
        obj_lst = [] if obj_lst is None else obj_lst
        obj_lst.append({'图例号':'*', '机型编号':set_id, '风机编号':map_id, 
                        '开始日期':start_date, '结束日期':end_date})
        df = pd.DataFrame(obj_lst, index=np.arange(len(obj_lst)))
        df.drop_duplicates(['机型编号','风机编号','开始日期','结束日期'], inplace=True)
        df['图例号'] = [f't_{i}' for i in np.arange(df.shape[0])]
        return False, *[no_update]*4, df.to_dict('records'), *[no_update]*2
    return False, *[no_update]*7

@callback(
    Output(f'{_PREFIX}_start_date', 'minDate'),
    Output(f'{_PREFIX}_start_date', 'maxDate'),
    Output(f'{_PREFIX}_start_date', 'disabledDates'), 
    Output(f'{_PREFIX}_start_date', 'initialMonth'),
    Output(f'{_PREFIX}_end_date', 'minDate'),
    Output(f'{_PREFIX}_end_date', 'maxDate'), 
    Output(f'{_PREFIX}_end_date', 'disabledDates'),  
    Output(f'{_PREFIX}_end_date', 'initialMonth'),
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_explore_map_id(map_id, set_id):
    turbine_id = msql.map_id_to_turbine_id(set_id, map_id).squeeze()
    dates = msql.get_available_date(set_id=set_id, turbine_id=turbine_id)
    min_date = dates.min()
    max_date = dates.max()
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    return [min_date, max_date, disabled_days, max_date]*2

@callback(
    Output(f'{_PREFIX}_end_date', 'minDate', allow_duplicate=True),
    Output(f'{_PREFIX}_end_date', 'value', allow_duplicate=True),
    Input(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_end_date', 'value'),
    prevent_initial_call=True
    )
def on_change_start_date(start_date, end_date):
    min_date = start_date if start_date is not None else no_update
    end_date = None if (end_date is not None and end_date>start_date) else no_update
    return min_date, end_date
    
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
        model_point_df = msql.read_model_point(set_id=set_ids, select=1)
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
        radar_r = model_point_df['point_name']
        spectrum_y = model_point_df['point_name']
        return timeseries_y, scatter_x, scatter_y, radar_theta, radar_r, spectrum_y
    else:
        return [None]*6

def _scatter_plot(table_lst, xcol, ycol, mode='markers', _type='line'):
    fig = go.Figure()
    freqs = set()
    for dct in table_lst:
        point_name = [ycol] if xcol=='ts' else [xcol, ycol]
        set_id = dct['机型编号']
        turbine_id = msql.map_id_to_turbine_id(set_id, dct['风机编号']).squeeze()
        df,desc_df = td.read_scada(set_id=set_id, 
                                   turbine_id=turbine_id,
                                   start_time=dct['开始日期'],
                                   end_time=dct['结束日期'],
                                   point_name=point_name)
        df = df if df.shape[0]<20000 else df.sample(20000).sort_index()    
        if df.shape[0]<1:
            continue
        if _type=='polar':
            trace = go.Scatterpolar(theta=df[xcol], 
                               r=df[ycol],
                               name=dct['图例号'],
                               mode=mode,
                               showlegend=True,
                               marker=dict(size=3, opacity=0.5))
        elif _type=='line':
            trace = go.Scatter(x=df[xcol], 
                               y=df[ycol],
                               name=dct['图例号'],
                               mode=mode,
                               showlegend=True,
                               marker={'opacity':0.2})
        elif _type=='spectrum':
            temp = msql.read_turbine_charateristic_frequency(
                set_id=set_id, point_name=ycol)
            if temp.shape[0]>0:
                temp = temp['frequency'].iloc[-1]
                temp = pd.Series(temp.split(',')).astype(float)
                freqs.update(temp.tolist())
                
            y_t = df[ycol] - df[ycol].mean()
            x_fft, y_fft = _power_spectrum(y_t, sample_spacing=1)
            
            col_freq = 'frequency(Hz)'
            df = pd.DataFrame({col_freq:x_fft, ycol:y_fft})
            df = df[df[col_freq]>=0]    
            
            trace = go.Scatter(x=df[col_freq], 
                               y=df[ycol],
                               name=ycol,
                               mode='lines+markers',           
                               marker={'opacity':0.2})           
            
        fig.add_trace(trace)
    if _type=='spectrum':
        for i in freqs:
            fig.add_vline(x=i, annotation_text=f"特征频率{i}",
                          annotation_font_size=10, line_width=1, 
                          line_dash="dash", line_color="green")
    title_x = '时间' if xcol=='ts' else desc_df['column'].iloc[0]
    fig.update_xaxes(title_text=title_x)
    fig.update_yaxes(title_text=desc_df['column'].iloc[-1])
    return fig

@callback(
    Output(f'{_PREFIX}_plot', 'figure'),
    Output(f'{_PREFIX}_alert', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_alert', 'is_open', allow_duplicate=True),
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
    
    if plot_type=='时序图':
        if ts_y is None:
            return no_update, '未指定绘图变量', True
        fig = _scatter_plot(table_lst, 'ts', ts_y, 'lines+markers', 'line')
    elif plot_type=='散点图':
        if sct_x is None or sct_y is None:
            return no_update, '未指定绘图变量', True
        fig = _scatter_plot(table_lst, sct_x, sct_y, 'markers', 'line')
    elif plot_type=='雷达图':
        if rad_th is None or rad_r is None:
            return no_update, '未指定绘图变量', True
        fig = _scatter_plot(table_lst, rad_th, rad_r, 'markers', 'polar')
    elif plot_type=='频谱图':
        if spc_y is None:
            return no_update, '未指定绘图变量', True
        fig = _scatter_plot(table_lst, 'ts', spc_y, 'markers', 'spectrum')
    else:
        raise ValueError(f'unrecongized plot_type = {plot_type}')
        
    fig.update_layout(
        height=700,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation='h',
            font=dict(
                    size=10,
                    color='black'
                ),
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1),
        )
    return fig, no_update, no_update

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