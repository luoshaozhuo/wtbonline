# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:49:18 2023

@author: luosz

诊断页面
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
from flask_login import current_user
import time
import pandas as pd


from _pages.tools.plot import line_plot, anormaly_plot, spectrum_plot
from _database import _mysql as msql
from _database import _tdengine as td
from _database import model
from _pages.tools.decorator import _on_error
    
# =============================================================================
# constant
# =============================================================================
_PREFIX = 'diagnose' 

sr = msql.read_model_anormaly(limit=1, columns=['sample_id', 'turbine_id', 'set_id']).squeeze()
_STATISTIC_CONFIGURATION = msql.read_statistics_configuration()
if len(sr)<1:
    _INITTIAL_SAMPLE_ID, _INITTIAL_TURBINE_ID, _INITTIAL_SET_ID  = [None]*3
    _POINT_NAME = []
else:
    _INITTIAL_SAMPLE_ID, _INITTIAL_TURBINE_ID, _INITTIAL_SET_ID  = sr.squeeze()
    _POINT_NAME = msql.read_model_point(_INITTIAL_SET_ID, select=1)['point_name']

del sr
# =============================================================================
# function
# =============================================================================
def _plot_fatory(sample_id, cols, _type):
    try:
        sr = msql.read_statistics_sample(_id=sample_id).squeeze()
        if _type=='anormaly':
            data_df = msql.read_statistics_sample(set_id=sr['set_id'], 
                                                  turbine_id=sr['turbine_id'])
            fig = None if data_df.shape[0]<1 else anormaly_plot(data_df, cols[0], cols[1])
        else:
            df, descr = td.read_scada(set_id=sr['set_id'],
                                      turbine_id=sr['turbine_id'], 
                                      start_time=sr['start_time'], 
                                      point_name=cols)
            if df.shape[0]<1:
                fig = None
            else:
                units = descr.loc[cols,'unit']
                if _type=='line':
                    fig = line_plot(df, cols, units)
                elif _type=='spectrum':
                    freqs = msql.read_turbine_charateristic_frequency(
                        set_id = sr['set_id'], point_name=cols
                        )
                    if len(freqs)>0:
                        freqs = freqs['frequency'].squeeze()
                        freqs = pd.Series(freqs.split(',')).astype(float)
                    else:
                        freqs = []
                    fig = spectrum_plot(df, cols, units, freqs)
    except:
        raise ValueError((sample_id, cols, _type))
    return fig

def _get_anormaly_plot(sample_id, projection):
    setting = msql.read_page_setting(page='diagnose', card='anormaly')
    setting = setting[setting['component_id']==projection].squeeze()
    return _plot_fatory(sample_id, eval(setting['value']), 'anormaly')

# =============================================================================
# layout
# =============================================================================
def _get_profile_summary(sr):
    unit = _STATISTIC_CONFIGURATION[_STATISTIC_CONFIGURATION['table_name']=='statistic_sample']
    unit = {r['name']:r['unit'].replace('-','') for _,r in unit.iterrows()}
    setting_df = msql.read_page_setting('diagnose', 'profile')   
    ret = []
    for _,row in setting_df.iterrows():
        value = unit.get(row['component_id'], None)
        value = eval(row['value'])+' '+value if value else eval(row['value'])
        ret.append(html.P(value, className='small m-0'))
    return ret

def _get_modal_diaglog():
    return dbc.Modal(
                [dbc.ModalHeader(dbc.ModalTitle("选择样本")),
                 dbc.ModalBody([
                     dcc.RadioItems(['全部异常', '已标注'],
                                    value='全部异常',
                                    id='diagnose_profile_radio',
                                    labelClassName ='px-2 small',
                                    inline=True),
                     html.Div(
                         dash_table.DataTable(
                            id=f'{_PREFIX}_profile_datatable',
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            row_selectable="single",
                            selected_rows=[],
                            page_action="native",
                            page_current= 0,
                            page_size= 20,
                            style_header = {'font-weight':'bold'},
                            style_table ={
                                'overflowX': 'auto',
                                'font-size':'small'
                            },
                            ),
                         className='py-2'
                        )
                     ]),
                 dbc.ModalFooter(dbc.Button("确定", 
                                            id=f'{_PREFIX}_profile_btn_confirm', 
                                            className="btn-primary", 
                                            n_clicks=0,
                                            size="sm"
                                            ))],
                id="diagnose_profile_modal_query",
                size="lg",
                is_open=False,
                )

_info = dbc.Card([
            dbc.CardHeader('数据概要'),
            dbc.CardBody(
                [
                html.Div([html.H4(id='diagnose_profile_turbine'),
                          dbc.ButtonGroup([
                              dbc.Button('查询', id=f'{_PREFIX}_profile_btn_query', 
                                         className='btn-secondary'),
                              dbc.Button('导出', id=f'{_PREFIX}_profile_btn_export', 
                                         className='btn-primary'),
                              dcc.Download(id=f'{_PREFIX}_proifle_download'),
                              ],
                              size="sm",
                              className='mb-2'),
                          _get_modal_diaglog()
                          ],
                         className = 'hstack d-flex justify-content-between align-items-center'
                         ),
                 html.Div(id=f'{_PREFIX}_profile_summary'),
                 html.Br(),
                 html.Div(
                     [dbc.ButtonGroup([dbc.Button('异常', 
                                                  className='btn-light', 
                                                  id=f'{_PREFIX}_profile_btn_abnormal'),
                                       dbc.Button('正常', 
                                                  className='btn-light', 
                                                  id=f'{_PREFIX}_profile_btn_normal'),
                                       dbc.Button('未标注', 
                                                  className='btn-warning', 
                                                  id=f'{_PREFIX}_profile_btn_not_labeled')],
                                      size="sm"),
                      dbc.Button(['下一条',dbc.Badge(id=f'{_PREFIX}_profile_bage', 
                                                  color="light", 
                                                  text_color="primary", 
                                                  className="ms-1")], 
                                 id=f'{_PREFIX}_profile_btn_next',
                                 className='btn-info',
                                 size="sm")
                     ], 
                     className = 'hstack d-flex justify-content-between align-items-center')
                 ])
        ], className='mt-2')

def _get_view_anormaly_card_body():
    setting_df = msql.read_page_setting(page='diagnose', card='anormaly')
    setting_df = setting_df.sort_values('order')
    return  [dcc.RadioItems(setting_df['component_id'],
                            value=setting_df['component_id'].iloc[0],
                            labelClassName ='px-2 small',
                            id=f'{_PREFIX}_anormaly_radio',
                            inline=True),
             dcc.Graph(id=f'{_PREFIX}_anormaly_plot',
                       style={'height':400}, 
                       config={'displaylogo':False})
             ]

_anormaly = dbc.Card([
                dbc.CardHeader('离群数据投影'),
                dbc.CardBody(_get_view_anormaly_card_body())
                ], className='mt-2')


_time_sereis = dbc.Card([
    dbc.CardHeader('时序'),
    dbc.CardBody([
        dcc.Dropdown(
            _POINT_NAME,
            ['10s平均风速', '电网有功功率', '风轮转速', '10s平均风向', '1#叶片实际角度', '工作模式'],
            id=f'{_PREFIX}_time_sereies_dropdown',
            multi=True,
            className='small'
            ),
        dcc.Graph(id=f'{_PREFIX}_time_series_plot',config={'displaylogo':False})
        ]),
    ],className='mt-2')

_spectrum_1 = dbc.Card([
    dbc.CardHeader('功率谱'),
    dbc.CardBody([
        dcc.Dropdown(
            _POINT_NAME,
            '10s平均风速',
            id=f'{_PREFIX}_spectrum_dropdown_1', 
            className='small'),
        dcc.Graph(id=f'{_PREFIX}_spectrum_plot_1',
                  style={'height':330}, 
                  config={'displaylogo':False}),
        ]),
    ],className='mt-2')

_spectrum_2 = dbc.Card([
    dbc.CardHeader('功率谱'),
    dbc.CardBody([
        dcc.Dropdown(
            _POINT_NAME,
            '电网有功功率',
            id=f'{_PREFIX}_spectrum_dropdown_2', 
            className='small'),
        dcc.Graph(id=f'{_PREFIX}_spectrum_plot_2',
                  style={'height':330}, 
                  config={'displaylogo':False}),
        ]),
    ],className='mt-2')


def get_layout():
    return [
        dcc.Store(data=_INITTIAL_SAMPLE_ID, 
                  id=f'{_PREFIX}_store_sample_id', 
                  storage_type='session'),
        dbc.Container(
            dbc.Row([
                    dbc.Col([_info, _anormaly], width=3),
                    dbc.Col(_time_sereis, width=6),
                    dbc.Col([_spectrum_1, _spectrum_2], width=3),
                ], className='g-2'),
                fluid=True,
            )
        ]

# =============================================================================
# callback    
# =============================================================================
@callback(
    Output(f'{_PREFIX}_profile_turbine', 'children'),
    Output(f'{_PREFIX}_profile_summary', 'children'),
    Output(f'{_PREFIX}_anormaly_plot', 'figure'),
    Output(f'{_PREFIX}_time_series_plot', 'figure'),
    Output(f'{_PREFIX}_spectrum_plot_1', 'figure'),
    Output(f'{_PREFIX}_spectrum_plot_2', 'figure'),
    Output(f'{_PREFIX}_profile_bage', 'children'),
    Output(f'{_PREFIX}_profile_btn_next', 'disabled'),
    Output(f'{_PREFIX}_profile_btn_abnormal', 'className'),
    Output(f'{_PREFIX}_profile_btn_normal', 'className'),
    Output(f'{_PREFIX}_profile_btn_not_labeled', 'className'),
    Output(f'{_PREFIX}_time_sereies_dropdown', 'options'),
    Output(f'{_PREFIX}_spectrum_dropdown_1', 'options'),
    Output(f'{_PREFIX}_spectrum_dropdown_2', 'options'),
    Output(f'{_PREFIX}_store_sample_id', 'data'),
    Input(f'{_PREFIX}_store_sample_id', 'data'),
    State(f'{_PREFIX}_profile_turbine', 'children'),
    State(f'{_PREFIX}_time_sereies_dropdown', 'value'),
    State(f'{_PREFIX}_spectrum_dropdown_1', 'value'),
    State(f'{_PREFIX}_spectrum_dropdown_2', 'value'),
    State(f'{_PREFIX}_anormaly_radio', 'value')
    )
@_on_error
def on_change_diagnose_sample_id(sample_id, turbine_id, col_ts, col_spc1, col_spc2, projection):
    ''' sample_id变更后，更新所有相关图形 '''
    if sample_id is not None:
        sr = msql.read_statistics_sample(_id=sample_id).squeeze()
        new_sample_id = no_update
    else:
        sr = msql.read_statistics_sample(limit=1).squeeze()
        sample_id = sr['id']
        new_sample_id = sample_id
    set_id = sr['set_id']
    turbine_id = sr['turbine_id']
    map_id = msql.read_windfarm_configuration(set_id, turbine_id)['map_id'].squeeze()
    options = msql.read_model_point(set_id=sr['set_id'], select=1)['point_name']
    

    scatter_plot = _get_anormaly_plot(sample_id, projection)   
    ts_plot = _plot_fatory(sample_id, col_ts, 'line')
    spc_plot_1 = _plot_fatory(sample_id, col_spc1, 'spectrum')
    spc_plot_2 = _plot_fatory(sample_id, col_spc2, 'spectrum')
    profile_summary =  _get_profile_summary(sr)
    
    sql = f'''
          select count(*) as 'count' from {model.ModelAnormaly.__tablename__} a  
          left join 
          (select is_anormaly, sample_id from {model.ModelLabel.__tablename__}) b 
          on a.sample_id=b.sample_id
          where is_anormaly is NULL 
          '''
    count = msql.read_sql(sql=sql)['count'].squeeze()
    disabled = False if count>2 else True
    
    sr = msql.read_model_label(sample_id=sample_id).squeeze()
    normal = sr['is_anormaly']==0 if len(sr)>0 else None
    btn_classname=[
        'btn-danger' if normal==0 else 'btn-light',
        'btn-success' if normal==1 else 'btn-light',
        'btn-warning' if normal is None else 'btn-light',
        ]
    
    return (f"{set_id} | {map_id}", profile_summary, scatter_plot, 
            ts_plot, spc_plot_1, spc_plot_2, count, disabled, *btn_classname,
            options, options, options, new_sample_id)

@callback(
    Output('diagnose_anormaly_plot', 'figure', allow_duplicate=True),
    Input('diagnose_anormaly_radio', 'value'),
    State('diagnose_store_sample_id', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_change_diagnose_anormaly_radio(projection, sample_id):
    return _get_anormaly_plot(sample_id, projection)

@callback(
    Output('diagnose_time_series_plot', 'figure', allow_duplicate=True),
    Input('diagnose_time_sereies_dropdown', 'value'),
    State('diagnose_store_sample_id', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_change_diagnose_time_sereies_dropdown(cols, sample_id):
    ''' 时序y坐标变量变更后，更新时序图 '''
    return _plot_fatory(sample_id, cols, 'line')

@callback(
    Output('diagnose_spectrum_plot_1', 'figure', allow_duplicate=True),
    Input('diagnose_spectrum_dropdown_1', 'value'),
    State('diagnose_store_sample_id', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_change_diagnose_spectrum_1_dropdown(col, sample_id):
    ''' 频谱1应变量变更 '''  
    return _plot_fatory(sample_id, col, 'spectrum')

@callback(
    Output('diagnose_spectrum_plot_2', 'figure', allow_duplicate=True),
    Input('diagnose_spectrum_dropdown_2', 'value'),
    State('diagnose_store_sample_id', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_change_diagnose_spectrum_2_dropdown(col, sample_id):
    ''' 频谱2应变量变更后，更新时序图 '''
    return _plot_fatory(sample_id, col, 'spectrum')

@callback(
    Output('diagnose_store_sample_id', 'data', allow_duplicate=True),
    Input('diganose_profile_btn_abnormal', 'n_clicks'), # 点击“异常”按钮
    Input('diganose_profile_btn_normal', 'n_clicks'), # 点击“正常”按钮
    Input('diganose_profile_btn_not_labeled', 'n_clicks'), # 点击“未标注”按钮
    Input('diagnose_profile_btn_confirm', 'n_clicks'), # 点击模态对话框“确定”按钮
    Input('diagnose_profile_btn_next', 'n_clicks'), # 点击“下一条”按钮
    Input('diagnose_anormaly_plot', 'clickData'), # 散点图点击数据点
    State('diagnose_store_sample_id', 'data'),
    State('diagnose_profile_datatable', 'selected_row_ids'),
    prevent_initial_call=True
    )
@_on_error
def on_diagnose_profile_change_sample_id(n1, n2, n3, n4, n5, sel_point, sample_id, row_ids):
    ''' 变更sample_id '''
    try:
        username = current_user.username
    except:
        username = 'diagnose_test'
    _id = ctx.triggered_id
    if _id == 'diagnose_profile_btn_confirm':
        if row_ids is not None and len(row_ids)>0:
            rev = row_ids[0]
        else:
            rev = no_update
    elif _id == 'diagnose_profile_btn_next':
        # 选取未标注过的样本
        sql = f'''
              select a.* from {model.ModelAnormaly.__tablename__} a  
              left join 
              (select is_anormaly, sample_id from {model.ModelLabel.__tablename__}) b 
              on a.sample_id=b.sample_id
              where is_anormaly is NULL and a.sample_id!={sample_id} 
              order By Rand() 
              limit 1
              '''
        sr = msql._read_sql(sql=sql).squeeze()
        if len(sr)==0:
            rev = no_update           
        rev = sr['sample_id']
    elif _id =='diagnose_anormaly_plot':
        rev = sel_point['points'][0]['customdata']
    elif _id == 'diganose_profile_btn_not_labeled':
        df = pd.DataFrame({'sample_id':[sample_id], 'username':[username]})
        msql.delete(df, model.ModelLabel)
        rev = sample_id
    else:
        is_anormaly = True if _id == 'diganose_profile_btn_abnormal' else False
        cols = ['id', 'set_id', 'turbine_id']
        df = msql.read_statistics_sample(_id=sample_id, columns=cols)
        df['username'] = username
        df['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        df['is_anormaly'] = is_anormaly
        df.rename(columns={'id':'sample_id'}, inplace=True)
        msql.insert(df, model.ModelLabel)
        rev = sample_id
    return rev

@callback(
    Output(f'{_PREFIX}_profile_modal_query', 'is_open'),
    Input(f'{_PREFIX}_profile_btn_query', 'n_clicks'), # 点击“查询”按钮
    Input(f'{_PREFIX}_profile_btn_confirm', 'n_clicks'), # 点击“确定”按钮
    prevent_initial_call=True
    )
@_on_error
def on_diagnose_profile_modal_state(n1, n2):
    ''' 打开/关闭模态对话框 '''
    _id = ctx.triggered_id
    if _id == f'{_PREFIX}_profile_btn_query':
        return True
    return False

@callback(
    Output('diagnose_proifle_download', 'data'),
    Input('diagnose_profile_btn_export', 'n_clicks'),
    State('diagnose_store_sample_id', 'data'),
    prevent_initial_call=True
    )
@_on_error
def on_diagnose_profile_btn_export(n, sample_id):
    ''' 导出数据 '''
    sr = msql.read_statistic_sample(sample_id=sample_id).squeeze()
    df,_ = td.read_scada(set_id=sr['set_id'], 
                          turbine_id=sr['turbine_id'],
                          start_time=sr['start_time'])
    return dcc.send_data_frame(df.to_csv, 'data.csv')

@callback(
    Output(f'{_PREFIX}_profile_datatable', 'columns'),
    Output(f'{_PREFIX}_profile_datatable', 'data'),
    Input(f'{_PREFIX}_profile_radio', 'value'),
    Input(f'{_PREFIX}_profile_btn_query', 'n_clicks'), # 点击“查询”按钮
    )
@_on_error
def on_change_diagnose_profile_radio(value, n):
    ''' 导出数据 '''
    if value=='全部异常':
        sample_id = msql.read_model_anormaly()['sample_id']
    elif value=='已标注':
        sample_id = msql.read_model_label()['sample_id']
    if len(sample_id)>0:
        df = msql.read_statistics_sample(_id=sample_id).round(2)
    else:
        df = msql.read_statistics_sample(limit=1).drop(index=0)

    columns=[{"name": i, "id": i} for i in df.columns]
    data=df.to_dict('records')
    return columns, data

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
    