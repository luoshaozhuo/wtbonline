# -*- coding: utf-8 -*-
'''
Created on Mon May 15 12:24:50 2023

@author: luosz

分析页面
'''
# =============================================================================
# import
# =============================================================================
from pathlib import Path
import sys
if __name__ == '__main__':
    root = Path(__file__).parents[1]
    if root not in sys.path:
        sys.path.append(root.as_posix())

from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from _database import _mysql as msql
from _pages.tools.decorator import _on_error

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'analyse' 

SIDEBAR_DF = pd.DataFrame([['性能', '功率曲线', 'powercurve', 1, 1],
                           ['性能', '变桨控制', 'pitch_control', 1, 1],
                           ['安全', '叶片净空', 'clearance', 2, 1],
                           ['安全', '塔顶振动', 'vibration', 2, 2],
                           ['可靠性', '可靠性', 'safety', 3, 1]],
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
            temp.append(dbc.Button(row['name'], 
                                   id={'main':f'{_PREFIX}_sidebar', 'sub':row['id']}, 
                                   className=class_name))
        rev.append(dbc.AccordionItem(html.Div(temp, className='d-grid pad-0'),
                                     title=row['category']))
    rev = dbc.Accordion(rev, flush=True)
    return rev                    

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
                                [dbc.InputGroupText("日期范围", class_name='small'),
                                 dcc.DatePickerRange(id=f'{_PREFIX}_daterange',
                                                     minimum_nights=0,
                                                     clearable=True,
                                                     start_date_placeholder_text="Start Period",
                                                     end_date_placeholder_text="End Period",
                                                     style={'font-size':12})], 
                                className='w-100'
                                ),
                          ]), 
                      dbc.ModalFooter([
                          dbc.Button(
                              '确定', 
                              id='analyse_btn_confirm', 
                              className='btn-primary me-2', 
                              n_clicks=0,
                              size='sm'
                              ),
                          dbc.Button(
                              '取消', 
                              id='analyse_btn_cancel', 
                              className='btn-secondary', 
                              n_clicks=0,
                              size='sm'
                              )
                          ]), 
                      ], id='analyse_modal', is_open=False)

def _get_plots(triggered_id, value_lst):
    df = []
    for i in value_lst:
        turbine_id = msql.map_id_to_turbine_id(set_id=i['机型编号'], 
                                                map_id=i['风机编号'])
        temp = msql.read_statistics_sample(set_id=i['机型编号'], 
                                           turbine_id=turbine_id,
                                           start_time=i['开始日期'], 
                                           end_time=i['结束日期'])
        temp['图例号'] = i['图例号']
        df.append(temp)
    df = pd.concat(df, ignore_index=True)

    if triggered_id=='powercurve':
        fig = go.Figure()
        for i,grp in df.groupby('图例号'):
            fig.add_trace(
                go.Scatter(x=grp['mean_wind_speed'],
                           y=grp['mean_power'],
                           mode='markers',
                           name=i,
                           showlegend=True,
                           marker=dict(opacity=0.3),)
                ) 
        fig.update_layout(
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
        
        card = dbc.Card([
            dbc.CardHeader('功率曲线局部视图'),
            dbc.CardBody([
                  dcc.Graph(figure=fig,
                            id=f'{_PREFIX}_plot_powercurve_scatter',
                            config={'displaylogo':False}), 
                  # dcc.Graph(id=f'{_PREFIX}_plot_powercurve_time_series',
                  #           config={'displaylogo':False}),
                ])
            ])
        
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))

def get_layout():
    layout = [_get_modle_dialog(),
              dcc.Store(data='powercurve', 
                        id=f'{_PREFIX}_store_sidebar', 
                        storage_type='session'),
              dbc.Row(
                  [dbc.Col(_get_side_bar(), 
                           width=2, 
                           className='border-end h-100'),
                   dbc.Col(
                       [dbc.Container(_get_card_select(), 
                                      fluid=True,
                                      className='m-0'),
                        dbc.Container(id=f'{_PREFIX}_plot', 
                                      fluid=True,
                                      className='m-0'
                                      )
                       ],width=10,className='h-100')
                   ], 
                  className='g-0 h-100')
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
def on_analyse_btn_collapse(n, is_open):
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
    State(f'{_PREFIX}_daterange', 'start_date'),
    State(f'{_PREFIX}_daterange', 'end_date'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_datatable', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_anaylse_dialog(n1, n2, n3, set_id, start_date, end_date, map_id, obj_lst):
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
        return (True, option_set_id, set_id, option_map_id, map_id, no_update)
    # 选择新set_id后，变更map_id可选项以及默认值
    elif _id==f'{_PREFIX}_dropdown_set_id':
        map_id_lst = msql.get_available_map_id(set_id)
        option_map_id = [{'label':i} for i in map_id_lst]
        map_id = map_id_lst[0]
        return (no_update, no_update, no_update, option_map_id, map_id, no_update)
    # 点击对话框里的确定按钮，关闭对话框，更新系列列表
    elif _id==f'{_PREFIX}_btn_confirm':
        turbine_id = msql.map_id_to_turbine_id(set_id, map_id)
        sr = msql.read_statistics_accumulattion(set_id=set_id,turbine_id=turbine_id)
        sr = sr.squeeze()
        start_date = sr['start_date'].isoformat() if start_date is None else start_date
        end_date = sr['end_date'].isoformat() if end_date is None else end_date
        obj_lst = [] if obj_lst is None else obj_lst
        obj_lst.append({'图例号':'*', '机型编号':set_id, '风机编号':map_id, 
                        '开始日期':start_date, '结束日期':end_date})
        df = pd.DataFrame(obj_lst, index=np.arange(len(obj_lst)))
        df.drop_duplicates(['机型编号','风机编号','开始日期','结束日期'], inplace=True)
        df['图例号'] = [f't_{i}' for i in np.arange(df.shape[0])]
        return False, no_update, no_update, no_update, no_update, df.to_dict('records')
    return False, no_update, no_update, no_update, no_update, no_update


@callback(
    Output(f'{_PREFIX}_daterange', 'min_date_allowed'),
    Output(f'{_PREFIX}_daterange', 'max_date_allowed'),
    Output(f'{_PREFIX}_daterange', 'disabled_days'),  
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_change_analyse_dropdown_turbine_id(map_id, set_id):
    turbine_id = msql.map_id_to_turbine_id(set_id, map_id).squeeze()
    dates = msql.get_available_date(set_id=set_id, turbine_id=turbine_id)
    min_date = dates.min()
    max_date = dates.max()
    disabled_days = pd.date_range(min_date, max_date)
    disabled_days = disabled_days[~disabled_days.isin(dates)]
    disabled_days = [i.date().isoformat() for i in disabled_days]
    return min_date, max_date, disabled_days

@callback(
    Output(f'{_PREFIX}_plot', 'children'),
    Output(f'{_PREFIX}_store_sidebar', 'data'),
    Input({'main':f'{_PREFIX}_sidebar', 'sub': ALL}, 'n_clicks'),
    Input(f'{_PREFIX}_btn_refresh', 'n_clicks'),
    State(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_store_sidebar', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_update_analyse_graph(n1, n2, value_lst, sidebar):
    if value_lst is None or len(value_lst)==0:
        return no_update, no_update
    triggered_id = ctx.triggered_id
    if not triggered_id==f'{_PREFIX}_btn_refresh':
        sidebar = triggered_id['sub'] 
    return _get_plots(sidebar, value_lst), sidebar

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