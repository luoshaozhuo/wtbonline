# -*- coding: utf-8 -*-
'''
Created on Mon May 15 12:24:50 2023

@author: luosz

分析页面
'''
# =============================================================================
# import
# =============================================================================)
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table, ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px 

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools._decorator import _on_error

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

# funcion
def mapid_to_tid(set_id, map_id):
    df = RSDBInterface.read_windfarm_configuration(
        set_id=set_id, 
        map_id=map_id,
        )
    assert df.shape[0]>0, '{map_id}找不到对应的turbine_id'
    return df['turbine_id'].iloc[0]

def tid_to_map(set_id, turbine_id):
    df = RSDBInterface.read_windfarm_configuration(
        set_id=set_id, 
        turbine_id=turbine_id
        )
    assert df.shape[0]>0, '{turbine_id}找不到对应的map_id'
    return df['map_id'].iloc[0]


def read_power_curve(set_id, turbine_id, start_date, end_date):
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_date,
        end_time=end_date,
        columns = ['turbine_id', 'var_355_mean', 'var_246_mean', 'totalfaultbool_mode',
                   'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique',
                   'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean']
        )
    # 正常发电数据
    df = df[
        (df['totalfaultbool_mode']=='False') &
        (df['totalfaultbool_nunique']==1) &
        (df['ongrid_mode']=='True') & 
        (df['ongrid_nunique']==1) & 
        (df['limitpowbool_mode']=='False') &
        (df['limitpowbool_nunique']==1)
        ]
    df.rename(columns={'var_355_mean':'mean_wind_speed', 
                       'var_246_mean':'mean_power'}, 
                       inplace=True)
    # 15°空气密度
    df['mean_wind_speed'] = df['mean_wind_speed']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
    return df

def plot_power_curve(value_lst):
    fig= go.Figure()
    for i, j in enumerate(value_lst):
        color = px.colors.qualitative.Plotly[i]
        turbine_id = mapid_to_tid(j['机型编号'], j['风机编号'])
        df = read_power_curve(j['机型编号'], turbine_id, j['开始日期'], j['结束日期'])
        wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        power_curve = df.groupby(['wspd', 'turbine_id'])['mean_power'].median().reset_index()
        mean_df = power_curve.groupby('wspd')['mean_power'].median().reset_index()
        fig.add_trace(
            go.Scatter(
                x=mean_df['wspd'],
                y=mean_df['mean_power'],
                line=dict(color=color),
                mode='lines',
                name=j['图例号']
                )
            )
        fig.add_trace(
            go.Scatter(
                x=df['mean_wind_speed'],
                y=df['mean_power'],
                mode='markers',
                name=j['图例号'],
                marker=dict(opacity=0.1, color=color)
                )
            ) 
    fig.layout.xaxis.update({'title': '风速 m/s'})
    fig.layout.yaxis.update({'title': '功率 kW'})
    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                    size=10,
                    color="black"
                ),
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1)
        )
    return fig

def _make_sure_datetime_string(x):
    if x is None:
        x = '0000000000T00:00:00'
    return x
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

def _get_plots(triggered_id, value_lst):
    header = ['Not implemented']
    graph = {}
    if triggered_id=='powercurve':
        header = '功率曲线'
        graph = dcc.Graph(figure=plot_power_curve(value_lst),
            id=f'{_PREFIX}_plot_powercurve_scatter',
            config={'displaylogo':False})
    
    card = dbc.Card([
        dbc.CardHeader(header),
        dbc.CardBody(dmc.loLoadingOverlay(graph))
        ])
    return dbc.Row(dbc.Col(card, class_name='m-0 px-1 pt-1'))

def get_layout():
    layout = [_get_modle_dialog(),
              dbc.Alert(id=f"{_PREFIX}_alert", color = 'danger', duration=3000, is_open=False),
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
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    Input(f'{_PREFIX}_datatable', 'data'),
    State(f'{_PREFIX}_start_date', 'value'),
    State(f'{_PREFIX}_start_time', 'value'),    
    State(f'{_PREFIX}_end_date', 'value'),
    State(f'{_PREFIX}_end_time', 'value'),
    prevent_initial_call=True
    )
@_on_error
def on_analyse_dialog(n1, n2, n3, set_id, map_id, obj_lst, start_date, start_time, end_date, end_time):
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
def on_change_analyse_date_range(start_date, start_time, end_date, end_time, set_id, map_id):
    if None in [set_id, map_id, start_date, end_date]:
        rev = [no_update, no_update, True]
    else:
        start_time = _make_sure_datetime_string(start_time)
        end_time = _make_sure_datetime_string(end_time)
        start_dt = pd.to_datetime(start_date + start_time[10:])
        end_dt = pd.to_datetime(end_date + end_time[10:])
        if start_dt >= end_dt:
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
def on_change_analyse_dropdown_map_id(map_id, set_id): 
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
    rev = [min_date, max_date, disabled_days, None]
    rev += [min_date, max_date, disabled_days, None]
    return rev

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
    app.run_server(debug=False)