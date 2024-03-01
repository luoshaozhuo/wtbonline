'''
作者：luosz
创建日期： 2024.02.18
描述：探索--二维图
    1、时序图
    2、散点图
    3、极坐标图
    4、频谱图
'''

#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html, Patch
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial
import traceback
from flask_login import current_user
import plotly.express as px

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._plot.functions import scatter_matrix_plot_anomaly
from wtbonline._common import dash_component as dcmpt
from wtbonline._plot.functions import simple_plot, get_simple_plot_parameters, get_simple_plot_selections

#%% constant
SECTION = '识别'
SECTION_ORDER = 1
ITEM='异常状态'
ITEM_ORDER = 1
PREFIX =  'recognize_anomaly'

SELECT_STATUS = [{'label':i, 'value':i} for i in ['异常', '正常']]
SCATTER_PLOT_SAMPLE_NUM = 10000
SCATTER_PLOT_VARIABLES = tuple([
    'var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean',
    'var_382_mean', 'var_383_mean'
    ])
#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[   
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select_mapid(id=get_component_id('select_mapid')),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_next'),
                rightIcon=DashIconify(icon="mdi:navigate-next", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                disabled=True,
                children="下一条异常样本",
                ), 
            dmc.Space(h='10px'),
            dmc.LoadingOverlay(dmc.List(
                size="xs",
                spacing="xs",
                children=[
                    dmc.ListItem(
                        id=get_component_id('listItem_id'),
                        icon=DashIconify(
                            icon="mdi:identification-card-outline",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_ts'),
                        icon=DashIconify(
                            icon="mdi:clock-time-four-outline",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_wspd'),
                        icon = DashIconify(
                            icon="mdi:windsock",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_rspd'),
                        icon = DashIconify(
                            icon="mdi:axis",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_power'),
                        icon = DashIconify(
                            icon="mdi:thunder-outline",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_pitchAngle'),
                        icon = DashIconify(
                            icon="mdi:angle-acute",
                            width=cfg.TOOLBAR_ICON_WIDTH,
                            color=cfg.TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    ],
                )),
            dmc.Space(h='10px'),
            dcmpt.select(id=get_component_id('select_label'), data=SELECT_STATUS, value=None, label='状态标注', description='标注当前十分钟数据样本状态'),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_update'),
                disabled=True,
                leftIcon=DashIconify(icon="mdi:file-document-edit-outline", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="更新样本标注",
                ), 
            dmc.Space(h='100px'),
            ]
        )

def creat_toolbar():
    return dmc.Aside(
        fixed=True,
        width={'base':cfg.TOOLBAR_SIZE},
        position={"right": 0, 'top':cfg.HEADER_HEIGHT},
        zIndex=2,
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=create_toolbar_content(),
                )
            ],
        )

def creat_content():
    return  dmc.Grid(
        gutter="xs",
        children=[
            dmc.Col(
                lg=8,
                md=12,
                children=dmc.LoadingOverlay(dcc.Graph(
                    id=get_component_id('graph_scatter'),
                    config={'displaylogo':False},
                    ))
                ),
            dmc.Col(
                lg=4,
                md=12,
                p=0,
                children=dmc.Stack(
                    spacing='xs',
                    children=[
                        dcmpt.select(id=get_component_id('select_type'), data=cfg.SIMPLE_PLOT_TYPE, value=cfg.SIMPLE_PLOT_TYPE[0], label='类型'),  
                        dcmpt.select(id=get_component_id('select_xaxis'), data=[], value=None, label='x坐标（θ坐标）', description='需要先选择类型以及机型编号'),
                        dcmpt.select(id=get_component_id('select_yaxis'), data=[], value=None, label='y坐标（r坐标）', description='需要先选择类型以及机型编号', disabled=True),
                        dcmpt.select(id=get_component_id('select_y2axis'), data=[], value=None, label='y2坐标', description='只适用于时序图', disabled=True, clearable=True),
                        dmc.LoadingOverlay(dcc.Graph(
                            id=get_component_id('graph_assist'),
                            config={'displaylogo':False},
                            style={'padding':0, 'margin':0}
                            )),
                        ]
                    ),  
                )
            ]
        )
    

#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout = [
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[creat_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )   
    ]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)


#%% callback
@callback(
    Output(get_component_id('select_mapid'), 'data'),
    Output(get_component_id('select_mapid'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_anomaly(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children'),
    Output(get_component_id('graph_scatter'), 'figure'),
    Output(get_component_id('listItem_id'), 'children'),
    Output(get_component_id('listItem_ts'), 'children'),
    Output(get_component_id('listItem_wspd'), 'children'),
    Output(get_component_id('listItem_rspd'), 'children'),
    Output(get_component_id('listItem_power'), 'children'),
    Output(get_component_id('listItem_pitchAngle'), 'children'),
    Output(get_component_id('btn_next'), 'disabled'),
    Input(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_mapid_anomaly(map_id, set_id):
    '''
    map_id改变时，切换散点图，清空辅助图及样本信息
    '''
    if None in [map_id, set_id]:
        return [no_update]*9
    graph_scatter = no_update
    df, note = utils.dash_try(
        note_title='读取异常数据失败',
        func=utils.read_scatter_matrix_anormaly,
        set_id=set_id,
        map_id=map_id,
        columns=SCATTER_PLOT_VARIABLES,
        sample_cnt=cfg.SIMPLE_PLOT_SAMPLE_NUM,
        )
    if note==no_update:
        graph_scatter, note = utils.dash_try(
        note_title='绘图失败',
        func=scatter_matrix_plot_anomaly,
        df=df,
        columns=SCATTER_PLOT_VARIABLES,
        set_id=set_id
        )
    if note==no_update:
        disabled = len(df[(df['is_suspector']==1) & (df['is_anomaly']==0)])<1
    else:
        disabled = True
    return note, graph_scatter, *['-']*6, disabled

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_id'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_ts'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_wspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_rspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_power'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_pitchAngle'), 'children', allow_duplicate=True),
    Input(get_component_id('graph_scatter'), 'selectedData'),
    Input(get_component_id('graph_scatter'), 'figure'),
    prevent_initial_call=True
    )
def callback_on_select_data_anomaly(selectedData, fig):
    '''
    点击next时，更新辅助图及样本信息
    '''
    columns=['var_94_mean', 'var_355_mean', 'var_246_mean', 'var_101_mean', 'bin']
    note = no_update
    id_ = ts = wspd = rspd = power = pitchAngle = '-'
    selected_points = fig['data'][0].get('selectedpoints', [])
    if len(selected_points)>0:
        sample_id = fig['data'][0]['customdata'][selected_points[0]]
        df, note = utils.dash_dbquery(
            func=RSDBInterface.read_statistics_sample,
            id_=sample_id,
            columns=columns
            )
        if note==no_update:
            sr = df.round(2).squeeze()
            id_ = sample_id    
            ts = sr['bin']
            wspd = f'{sr["var_355_mean"]} m/s'
            rspd = f'{sr["var_94_mean"]} rpm'
            power = f'{sr["var_246_mean"]} kWh'
            pitchAngle = f'{sr["var_101_mean"]} °'
    return note, id_, ts, wspd, rspd, power, pitchAngle

@callback(
    Output(get_component_id('graph_scatter'), 'figure', allow_duplicate=True),
    Input(get_component_id('btn_next'), 'n_clicks'),
    State(get_component_id('graph_scatter'), 'figure'),
    prevent_initial_call=True
    )
def callback_on_btn_next_anomaly(n, fig):
    '''
    点击next时，更新辅助图及样本信息
    '''
    patched_fig = no_update
    sr = pd.Series(fig['data'][0]['text'])
    sr = sr[sr=='离群，未标注']
    if len(sr)>0:
        idx = sr.sample(1).index[0]
        patched_fig = Patch()
        patched_fig['data'][0]['selectedpoints'] = [idx]
    return patched_fig

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_xaxis'), 'data'),
    Output(get_component_id('select_xaxis'), 'value'),
    Output(get_component_id('select_yaxis'), 'data'),
    Output(get_component_id('select_yaxis'), 'value'),
    Output(get_component_id('select_y2axis'), 'data'),
    Output(get_component_id('select_y2axis'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_graph_assist_selections_anomaly(plot_type, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [plot_type, set_id]:
        return [None]*7
    rs, note = utils.dash_try(
        note_title='获取候选变量失败',
        func=get_simple_plot_selections,
        set_id=set_id,
        plot_type=plot_type
        )
    if note != no_update:
        return note, *[no_update]*6
    x_data, x_value, y_data, y_value = rs
    return no_update, x_data, x_value, y_data, y_value, y_data, y_value

@callback(
    Output(get_component_id('select_yaxis'), 'disabled'),
    Input(get_component_id('select_xaxis'), 'value'),
    Input(get_component_id('listItem_ts'), 'children'), 
    prevent_initial_call=True
    )
def callback_disable_slect_yaxis_anomaly(v, ts):
    return True if None in [v, ts] or ts=='-' else False

@callback(
    Output(get_component_id('select_y2axis'), 'disabled'),
    Input(get_component_id('select_yaxis'), 'value'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_disable_slect_y2axis_anomaly(v, plot_type):
    return True if v is None or plot_type not in ['时序图'] else False

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_assist'), 'figure'),
    Input(get_component_id('listItem_ts'), 'children'),
    Input(get_component_id('select_xaxis'), 'value'),
    Input(get_component_id('select_yaxis'), 'value'),
    Input(get_component_id('select_y2axis'), 'value'),
    Input(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_update_graph_assist_anomaly(ts, sel_xcol, sel_ycol, sel_y2col, map_id, set_id, plot_type):
    if None in [ts,sel_xcol, sel_ycol] or ts=='-':
        return no_update, {}
    # 读取绘图数据
    note = no_update
    try:
        xcol, xtitle, ycol, ytitle, y2col, y2title, mode = get_simple_plot_parameters(sel_xcol, sel_ycol, sel_y2col, plot_type, set_id)
        point_name = tuple(pd.Series([sel_xcol, sel_ycol, sel_y2col]).replace(['时间', '频率'], None).dropna())
        start_time = pd.to_datetime(ts)
        df, _ = utils.read_raw_data(
            set_id=set_id, 
            map_id=map_id, 
            point_name=point_name, 
            start_time=start_time,
            end_time=start_time+pd.Timedelta('10m'),
            sample_cnt=cfg.SIMPLE_PLOT_SAMPLE_NUM,
            remote=True
            )
    except Exception as e:
        msg=f'{traceback.format_exc()}'
        note = dcmpt.notification(title=cfg.NOTIFICATION_TITLE_DBQUERY_FAIL, msg=msg, _type='error')
    else:
        if len(df)<1:
            note = dcmpt.notification(title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA, msg='查无数据', _type='warning')
    if note!=no_update:
        return note, {}
    fig, note = utils.dash_try(
        note_title='绘图失败',
        func=simple_plot,
        x_lst=[None] if xcol in [None, ''] else [df[xcol].tolist()], 
        y_lst=[None] if ycol in [None, ''] else [df[ycol].tolist()], 
        y2_lst=[None] if y2col in [None, ''] else [df[y2col].tolist()],
        xtitle=xtitle, 
        ytitle=ytitle,
        y2title=y2title,
        name_lst=[ts],
        mode=mode,
        _type=plot_type,
        ref_freqs=[],
        height=500
        )
    return note, fig

@callback(
    Output(get_component_id('test'), 'figure'),
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Input(get_component_id('select_xaxis'), 'value'),
    Input(get_component_id('select_yaxis'), 'value'),
    Input(get_component_id('select_y2axis'), 'value'),
    Input(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_type'), 'value'),
    State(get_component_id('listItem_ts'), 'children'),
    prevent_initial_call=True
    )
def callback_update_graph_assist_anomaly(sel_xcol, sel_ycol, sel_y2col, map_id, set_id, plot_type, ts):
    if None in [ts,sel_xcol, sel_ycol] or ts=='-':
        return no_update, None
    return px.bar(x=["a", "b", "c"], y=[1, 3, 2]), no_update

@callback(
    Output(get_component_id('btn_update'), 'disabled'),
    Input(get_component_id('listItem_ts'), 'children'),
    Input(get_component_id('select_label'), 'value'),
    prevent_initial_call=True
    )
def callback_disable_btn_update_anomaly(ts, label):
    return True if None in [ts, label] or ts=='-' else False


@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_scatter'), 'figure', allow_duplicate=True),
    Input(get_component_id('btn_update'), 'n_clicks'),
    State(get_component_id('graph_scatter'), 'selectedData'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_mapid'), 'value'),
    State(get_component_id('select_label'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_update_anomaly(n, selectedData, set_id, map_id, label):
    if selectedData is None or len(selectedData)==0 or label is None:
        return no_update, no_update
    _ = Patch()
    patched_fig = Patch()
    # 获取当前用户名
    username, note = utils.dash_get_username(current_user, __name__ == '__main__')
    if note!=no_update:
        return note, no_update
    # 构造新记录
    create_time = pd.Timestamp.now()
    sample_id = selectedData['points'][0]['customdata']
    new_record = dict(
        username=username, 
        set_id=set_id, 
        turbine_id=utils.interchage_mapid_and_tid(map_id=map_id),
        sample_id=sample_id, 
        create_time=create_time,
        is_anomaly=1 if label=='异常' else -1             
        )
    _, note = utils.dash_dbquery(
        RSDBInterface.insert,
        df = new_record,
        tbname = 'model_label'
        )
    if note!=no_update:
        return note, no_update
    idx = selectedData['points'][0]['pointNumber']
    patched_fig['data'][0]['text'][idx] = label
    patched_fig['data'][0]['marker']['color'][idx] = 'red' if label=='异常' else 'green'
    patched_fig['data'][0]['marker']['opacity'][idx] = 1
    return no_update, patched_fig


#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=False)