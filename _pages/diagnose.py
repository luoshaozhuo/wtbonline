# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:49:18 2023

@author: luosz

诊断页面
"""
# =============================================================================
# import
# =============================================================================
from dash import html, dcc, Input, Output, no_update, callback, State, ctx, dash_table, ALL, MATCH
import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from flask_login import current_user
import pandas as pd
import dash_bootstrap_components as dbc

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._pages.tools.plot import scatter_matrix_anormaly
from wtbonline._pages.tools._decorator import _on_error
from wtbonline._pages.tools.plot import ts_plot_multiple_y, spc_plot_multiple_y
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._pages.tools.utils import mapid_to_tid, available_variable
from wtbonline._pages.tools.utils import var_name_to_point_name, read_sample_ts, read_scatter_matrix_anormaly
from wtbonline._pages.tools.utils import read_anormaly_without_label, read_sample_label
from wtbonline._pages import _SCATTER_PLOT_VARIABLES

# =============================================================================
# constant
# =============================================================================
_PREFIX = 'diagnose' 

# =============================================================================
# function
# =============================================================================
def _control_bar(idx, label='时序图'):
    return  dbc.InputGroup([
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem('频谱图', id={'type':f'{_PREFIX}_dropdown_menu_spc', 'index':idx}),
                        dbc.DropdownMenuItem('时序图', id={'type':f'{_PREFIX}_dropdown_menu_ts', 'index':idx}),
                    ],
                    id={'type':f'{_PREFIX}_dropdown_menu_type', 'index':idx},
                    label=label),
                dbc.InputGroupText('Y1'),
                dbc.Select(id={'type':f'{_PREFIX}_select_Y1', 'index':idx}),
                dbc.InputGroupText('Y2'),
                dbc.Select(id={'type':f'{_PREFIX}_select_Y2', 'index':idx}),
            ], size='sm')

_plot = dbc.Card(
    [
        dbc.CardHeader('可视化'),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(  
                    dmc.LoadingOverlay(
                        dcc.Graph(
                            figure=scatter_matrix_anormaly(),
                            id=f'{_PREFIX}_graph_anormaly',
                            hoverData={'points': [{'customdata': 'Japan'}]}
                            )
                        ),
                    width={"size": 6}
                ),
                dbc.Col([
                    _control_bar('top', '时序图'),
                    dmc.LoadingOverlay(dcc.Graph(figure=ts_plot_multiple_y(), id=f'{_PREFIX}_graph_top')),
                    html.Hr(),
                    _control_bar('btm', '频谱图'),
                    dmc.LoadingOverlay(dcc.Graph(figure=ts_plot_multiple_y(), id=f'{_PREFIX}_graph_btm'), exitTransitionDuration=1),
                ],width={"size": 6})
            ])
            ])
        ], 
    className='mt-2'
    )

_info = dbc.Card([
            dbc.CardHeader('数据概要'),
            dbc.CardBody(
                [
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('机型编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_set_id',
                            options=RSDBInterface.read_windfarm_infomation()['set_id'].tolist(),
                            class_name='small',
                            )
                        ],
                    className='mb-2',
                    ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('风机编号', class_name='small'),
                        dbc.Select(
                            id=f'{_PREFIX}_dropdown_map_id',
                            class_name='small',
                            )
                        ],
                    className='mb-2',
                    ),
                html.Hr(),
                html.Div(id=f'{_PREFIX}_profile_summary'),
                html.Hr(),
                html.Div(
                    [
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    '异常', 
                                    className='btn-light', 
                                    disabled=True,
                                    id=f'{_PREFIX}_profile_btn_abnormal'
                                    ),
                                dbc.Button(
                                    '正常', 
                                    className='btn-light', 
                                    disabled=True,
                                    id=f'{_PREFIX}_profile_btn_normal'
                                    ),
                                dbc.Button(
                                    '未标注', 
                                    className='btn-warning', 
                                    disabled=True,
                                    id=f'{_PREFIX}_profile_btn_not_labeled'
                                    )
                                ],
                            size="sm"),
                        dbc.Button(
                            [
                                '下一条',
                                dbc.Badge(
                                    id=f'{_PREFIX}_profile_bage', 
                                    color="light", 
                                    text_color="primary", 
                                    className="ms-1",
                                    )
                                ], 
                            id=f'{_PREFIX}_profile_btn_next',
                            disabled=True,
                            className='btn-info',
                            size="sm"
                            )
                     ], 
                    className = 'hstack d-flex justify-content-between align-items-center'),
                 ])
        ], className='mt-2')

def get_layout():
    return [
        dbc.Alert(id=f"{_PREFIX}_alert", color = 'danger', duration=3000, is_open=False),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(_info, width=2),
                    dbc.Col(_plot),
                    ], 
                className='g-2'),
                fluid=True,
            )
        ]

# =============================================================================
# callback    
# =============================================================================
@callback(
    Output(f'{_PREFIX}_dropdown_map_id', 'options'),
    Output({'type':f'{_PREFIX}_select_Y1', 'index':ALL}, 'options'),
    Output({'type':f'{_PREFIX}_select_Y2', 'index':ALL}, 'options'),
    Output({'type':f'{_PREFIX}_select_Y1', 'index':ALL}, 'value'),
    Output({'type':f'{_PREFIX}_select_Y2', 'index':ALL}, 'value'),
    Input(f'{_PREFIX}_dropdown_set_id', 'value'),
    State({'type':f'{_PREFIX}_dropdown_menu_type', 'index':ALL}, 'label'),
    prevent_initial_call=True
    )
@_on_error
def diagnose_on_change_analyse_dropdown_set_id(set_id, labels): 
    turbine_ids = RSDBInterface.read_windfarm_configuration(set_id=set_id, columns='map_id')
    turbine_ids = turbine_ids.squeeze().tolist()
    options_all, options_float = available_variable(set_id)
    options = []
    for i in labels:
        if i=='时序图':
            options.append(options_all)
        else:
            options.append(options_float) 
    return turbine_ids, options, options, ['']*2,  ['']*2

@callback(
    Output(f'{_PREFIX}_graph_anormaly', 'figure'),
    Output(f'{_PREFIX}_graph_top', 'figure'),
    Output(f'{_PREFIX}_graph_btm', 'figure'),
    Output(f'{_PREFIX}_profile_summary', 'children'),
    Output(f'{_PREFIX}_graph_anormaly', 'selectedData'),
    Output(f'{_PREFIX}_profile_bage', 'children', allow_duplicate=True),
    Output(f'{_PREFIX}_profile_btn_next', 'disabled', allow_duplicate=True),
    Input(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def diagnose_on_change_analyse_dropdown_map_id(map_id, set_id):
    if map_id=='' or map_id is None:
        return scatter_matrix_anormaly(), ts_plot_multiple_y(), ts_plot_multiple_y(), '', None, '', True
    anormaly_df = read_anormaly_without_label(set_id=set_id, map_id=map_id)
    count = len(anormaly_df)
    df = read_scatter_matrix_anormaly(set_id, map_id=map_id, columns=_SCATTER_PLOT_VARIABLES)
    graph_anormaly = scatter_matrix_anormaly(df, _SCATTER_PLOT_VARIABLES, set_id)
    return graph_anormaly, no_update, no_update, no_update, None, count, False

@callback(
    Output({'type':f'{_PREFIX}_dropdown_menu_type', 'index':MATCH}, 'label'),
    Output({'type':f'{_PREFIX}_select_Y1', 'index':MATCH}, 'options', allow_duplicate=True),
    Output({'type':f'{_PREFIX}_select_Y2', 'index':MATCH}, 'options', allow_duplicate=True),
    Output({'type':f'{_PREFIX}_select_Y1', 'index':MATCH}, 'value', allow_duplicate=True),
    Output({'type':f'{_PREFIX}_select_Y2', 'index':MATCH}, 'value',  allow_duplicate=True),
    Input({'type':f'{_PREFIX}_dropdown_menu_spc', 'index':MATCH}, 'n_clicks'),
    Input({'type':f'{_PREFIX}_dropdown_menu_ts', 'index':MATCH}, 'n_clicks'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
@_on_error
def diagnose_on_change_analyse_dropdown_menu_type(n1, n2, set_id):
    ctx = dash.callback_context
    type_ = eval(ctx.triggered[0]["prop_id"].split(".")[0])['type']
    if type_ == f'{_PREFIX}_dropdown_menu_spc':
        label = '频谱图'
    else:
        label = '时序图'
        
    turbine_ids = RSDBInterface.read_windfarm_configuration(set_id=set_id, columns='map_id')
    turbine_ids = turbine_ids.squeeze().tolist()
    options_all, options_float = available_variable(set_id)
    if label=='时序图':
        options = (options_all)
    else:
        options = (options_float) 
        
    return label, options, options, '', ''

@callback(
    Output(f'{_PREFIX}_profile_summary', 'children', allow_duplicate=True),
    Input(f'{_PREFIX}_graph_anormaly', 'selectedData'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
def diagnose_update_prfile_summary(selected_data, set_id):
    if selected_data is None or None in selected_data or len(selected_data['points'])>1:
        return ''
    sample_id = selected_data['points'][0]['customdata']
    if sample_id is None:
        return ''
    cols = ['bin'] + list(_SCATTER_PLOT_VARIABLES)
    sr = RSDBInterface.read_statistics_sample(id_=sample_id, columns=cols).round(3).squeeze()
    labels = var_name_to_point_name(
        set_id=set_id, 
        var_name=tuple(pd.Series(_SCATTER_PLOT_VARIABLES).str.replace('_mean', ''))
        )
    labels = ['bin'] + labels
    rev = [html.P(f"样本编号: {sample_id}")]
    for i in range(len(labels)):
        rev.append(html.P(f"{labels[i]}: {sr[cols[i]]}"))
    return rev


@callback(
    Output(f"{_PREFIX}_alert", 'is_open'),
    Output(f"{_PREFIX}_alert", 'children'),
    Output(f"{_PREFIX}_alert", 'color'),
    Output(f'{_PREFIX}_graph_top', 'figure', allow_duplicate=True),
    Output(f'{_PREFIX}_graph_btm', 'figure', allow_duplicate=True),
    Input(f'{_PREFIX}_graph_anormaly', 'selectedData'),
    Input({'type':f'{_PREFIX}_dropdown_menu_type', 'index':ALL}, 'label'),
    Input({'type':f'{_PREFIX}_select_Y1', 'index':ALL}, 'value'),
    Input({'type':f'{_PREFIX}_select_Y2', 'index':ALL}, 'value'),
    prevent_initial_call=True
    )
def diagnose_update_graphs(selected_data, type_lst, y1_lst, y2_lst):
    if selected_data is None or len(selected_data['points'])!=1:
        return no_update, no_update, no_update, ts_plot_multiple_y(), ts_plot_multiple_y()
    var_name=pd.Series(y1_lst+y2_lst).replace('', None).dropna().drop_duplicates().tolist()
    if len(var_name)==0:
        return no_update, no_update, no_update, ts_plot_multiple_y(), ts_plot_multiple_y()
    idx = selected_data['points'][0]['customdata']
    df, point_df = read_sample_ts(idx, tuple(var_name+['var_94']))
    point_df.set_index('var_name', inplace=True, drop=False)
    if len(df)==0:
        return True, f'无id={idx}, columns={var_name}数据', 'red', ts_plot_multiple_y(), ts_plot_multiple_y()
    
    func = {'时序图':ts_plot_multiple_y, '频谱图':spc_plot_multiple_y}
    top_cols = [y1_lst[0], y2_lst[0]]
    btm_cols = [y1_lst[1], y2_lst[1]]
    fig_top, fig_btm = no_update, no_update
    triggerd = dash.callback_context.triggered[0]
    if triggerd['prop_id']==f'{_PREFIX}_graph_anormaly.selectedData':
        fig_top = func[type_lst[0]](
            df, 
            top_cols, 
            ['' if i=='' else point_df.loc[i, 'unit'] for i in top_cols], 
            ['' if i=='' else point_df.loc[i, 'point_name'] for i in top_cols], 
            ref_col='var_94'
            )
        fig_btm = func[type_lst[1]](
            df, 
            btm_cols, 
            ['' if i=='' else point_df.loc[i, 'unit'] for i in btm_cols], 
            ['' if i=='' else point_df.loc[i, 'point_name'] for i in btm_cols],
            ref_col='var_94'
            )
    else:
        if triggerd['prop_id'].find('top')>-1:
            fig_top = func[type_lst[0]](
                df, 
                top_cols, 
                ['' if i=='' else point_df.loc[i, 'unit'] for i in top_cols], 
                ['' if i=='' else point_df.loc[i, 'point_name'] for i in top_cols], 
                ref_col='var_94'
                )
        else:
            fig_btm = func[type_lst[1]](
                df, 
                btm_cols, 
                ['' if i=='' else point_df.loc[i, 'unit'] for i in btm_cols], 
                ['' if i=='' else point_df.loc[i, 'point_name'] for i in btm_cols],
                ref_col='var_94'
                )
            
    return no_update, no_update, no_update, fig_top, fig_btm

@callback(
    Output(f'{_PREFIX}_graph_anormaly', 'figure', allow_duplicate=True),
    Output(f'{_PREFIX}_graph_anormaly', 'selectedData', allow_duplicate=True),
    Output(f'{_PREFIX}_profile_bage', 'children', allow_duplicate=True),
    Input(f'{_PREFIX}_profile_btn_next', 'n_clicks'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    prevent_initial_call=True
    )
def diagnose_on_click_btn_next(n, map_id, set_id):
    df = read_scatter_matrix_anormaly(set_id, map_id=map_id, columns=_SCATTER_PLOT_VARIABLES)
    anormaly_df = read_anormaly_without_label(set_id=set_id, map_id=map_id)
    selectedpoints = []
    count = len(anormaly_df)
    if len(anormaly_df)>0:
        sample_id = anormaly_df['sample_id'].sample(1).squeeze()
        selectedpoints = df[df['id']==sample_id].index.tolist()
    else:
        sample_id=None
    graph_anormaly = scatter_matrix_anormaly(df, _SCATTER_PLOT_VARIABLES, set_id, selectedpoints)
    return graph_anormaly, {'points':[{'customdata':sample_id}]}, count

@callback(
    Output(f'{_PREFIX}_profile_btn_abnormal', 'className', allow_duplicate=True),
    Output(f'{_PREFIX}_profile_btn_normal', 'className', allow_duplicate=True),
    Output(f'{_PREFIX}_profile_btn_not_labeled', 'className', allow_duplicate=True),
    Output(f'{_PREFIX}_profile_btn_abnormal', 'disabled'),
    Output(f'{_PREFIX}_profile_btn_normal', 'disabled'),
    Output(f'{_PREFIX}_profile_btn_not_labeled', 'disabled'),
    Input(f'{_PREFIX}_graph_anormaly', 'selectedData'),
    prevent_initial_call=True
    )
def diagnose_update_label_buttons(selected_data):
    if selected_data is None or len(selected_data['points'])!=1:
        rev = [no_update]*3 + [True]*3
    else:
        sample_id = selected_data['points'][0]['customdata']
        label = read_sample_label(sample_id)
        if label==1:
            rev = ['btn-danger', 'btn-light', 'btn-light']
        elif label==-1:
            rev = ['btn-light', 'btn-success', 'btn-light']
        else:
            rev = ['btn-light', 'btn-light', 'btn-warning']
        rev += [False]*3
    return rev

@callback(
    Output(f'{_PREFIX}_profile_btn_abnormal', 'className'),
    Output(f'{_PREFIX}_profile_btn_normal', 'className'),
    Output(f'{_PREFIX}_profile_btn_not_labeled', 'className'),
    Output(f'{_PREFIX}_profile_bage', 'children', allow_duplicate=True),
    Input(f'{_PREFIX}_profile_btn_abnormal', 'n_clicks'),
    Input(f'{_PREFIX}_profile_btn_normal', 'n_clicks'),
    Input(f'{_PREFIX}_profile_btn_not_labeled', 'n_clicks'),
    State(f'{_PREFIX}_dropdown_set_id', 'value'),
    State(f'{_PREFIX}_dropdown_map_id', 'value'),
    State(f'{_PREFIX}_graph_anormaly', 'selectedData'),
    prevent_initial_call=True
    )
def diagnose_on_click_label_buttons(n1, n2, n3, set_id, map_id, selected_data):
    try:
        username = current_user.username
    except:
        username = 'diagnose_test'
    create_time = pd.Timestamp.now()
    sample_id = selected_data['points'][0]['customdata']
    new_record = dict(
        username=username, set_id=set_id, turbine_id=mapid_to_tid(set_id, map_id),
        sample_id=sample_id, create_time=create_time              
        )
    
    triggerd = dash.callback_context.triggered[0]
    rev = [no_update]*3
    if triggerd['prop_id'].find('abnormal')>-1:
        new_record.update(dict(is_anormaly=1))
        RSDBInterface.insert(new_record, 'model_label')
        rev = ['btn-danger', 'btn-light', 'btn-light']
    elif triggerd['prop_id'].find('normal')>-1:
        new_record.update(dict(is_anormaly=-1))
        RSDBInterface.insert(new_record, 'model_label')
        rev = ['btn-light', 'btn-success', 'btn-light']
    elif triggerd['prop_id'].find('not_labeled')>-1:
        RSDB.delete('model_label', eq_clause=dict(sample_id=sample_id, username=username))
        rev = ['btn-light', 'btn-light', 'btn-warning'] 
        
    anormaly_df = read_anormaly_without_label(set_id=set_id, map_id=map_id)
    rev.append(len(anormaly_df))
    return rev

# =============================================================================
# for test
# =============================================================================
if __name__ == '__main__':     
    import dash
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)
    app.layout = html.Div(get_layout())
    app.run_server(debug=False, host='0.0.0.0', port=8050)
    