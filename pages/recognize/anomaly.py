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
from tkinter import N
import dash
import dash_mantine_components as dmc
from dash import dcc, html, dash_table, Patch
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update, ctx
import pandas as pd
from functools import partial

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

HEADER_HEIGHT = cfg.HEADER_HEIGHT

TOOLBAR_SIZE = cfg.TOOLBAR_SIZE
TOOLBAR_PADDING = cfg.TOOLBAR_PADDING
TOOLBAR_TOGGLE_SIZE = cfg.TOOLBAR_TOGGLE_SIZE
TOOLBAR_TOGGLE_ICON_WIDTH = cfg.TOOLBAR_TOGGLE_ICON_WIDTH
TOOLBAR_TOGGLE_POS_TOP = cfg.TOOLBAR_TOGGLE_POS_TOP
TOOLBAR_TOGGLE_POS_RIGHT = cfg.TOOLBAR_TOGGLE_POS_RIGHT
TOOLBAR_COMPONENT_SIZE = cfg.TOOLBAR_COMPONENT_SIZE
TOOLBAR_ICON_WIDTH = cfg.TOOLBAR_ICON_WIDTH
TOOLBAR_COMPONENT_WIDTH = cfg.TOOLBAR_COMPONENT_WIDTH
TOOLBAR_FONT_SIZE = cfg.TOOLBAR_FONT_SIZE
TOOLBAR_HIDE_SMALLER_THAN =  cfg.TOOLBAR_HIDE_SMALLER_THAN
TOOLBAR_ICON_COLOR = cfg.TOOLBAR_ICON_COLOR

CONTAINER_SIZE = cfg.CONTAINER_SIZE

NOW = cfg.NOW
DATE = cfg.DATE
TIME_START = cfg.TIME_START
TIME_END = cfg.TIME_END

GRAPH_PADDING_TOP = cfg.GRAPH_PADDING_TOP
DBQUERY_FAIL = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL
DBQUERY_NODATA = cfg.NOTIFICATION_TITLE_DBQUERY_NODATA
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH_FAIL

TABLE_COLUMNS = cfg.TOOLBAR_TABLE_COLUMNS
TABLE_FONT_SIZE = cfg.TOOLBAR_TABLE_FONT_SIZE
TABLE_HEIGHT = cfg.TOOLBAR_TABLE_HEIGHT

SELECT_STATUS = [{'label':i, 'value':i} for i in ['未标注', '异常', '正常']]
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
        px=TOOLBAR_PADDING, 
        children=[   
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select_mapid(id=get_component_id('select_mapid')),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_next'),
                rightIcon=DashIconify(icon="mdi:navigate-next", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
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
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_ts'),
                        icon=DashIconify(
                            icon="mdi:clock-time-four-outline",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_wspd'),
                        icon = DashIconify(
                            icon="mdi:windsock",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_rspd'),
                        icon = DashIconify(
                            icon="mdi:axis",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_power'),
                        icon = DashIconify(
                            icon="mdi:thunder-outline",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    dmc.ListItem(
                        id=get_component_id('listItem_pitchAngle'),
                        icon = DashIconify(
                            icon="mdi:angle-acute",
                            width=TOOLBAR_ICON_WIDTH,
                            color=TOOLBAR_ICON_COLOR,
                            ),
                        children="-",
                        ),
                    ],
                )),
            dmc.Space(h='10px'),
            dcmpt.select(id=get_component_id('select_status'), data=SELECT_STATUS, value=None, label='状态标注', description='标注当前十分钟数据样本状态'),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_update'),
                leftIcon=DashIconify(icon="mdi:file-document-edit-outline", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="更新样本标注",
                ), 
            dmc.Space(h='100px'),
            ]
        )

def creat_toolbar():
    return dmc.Aside(
        fixed=True,
        width={'base': TOOLBAR_SIZE},
        position={"right": 0, 'top':HEADER_HEIGHT},
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
                        dcmpt.select(id=get_component_id('select_yaxis2'), data=[], value=None, label='y2坐标', description='只适用于时序图及频谱图', disabled=True, clearable=True),
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
    dmc.Container(children=[creat_content()], size=CONTAINER_SIZE, pt=HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )   
    ]

if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)


#%% callback
@callback(
    Output(get_component_id('select_mapid'), 'data'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_anomaly(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data

@callback(
    Output(get_component_id('notification'), 'children'),
    Output(get_component_id('graph_scatter'), 'figure'),
    Output(get_component_id('graph_assist'), 'figure'),
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
    return note, graph_scatter, None, *['-']*6, False

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
def callback_on_select_data_on_graph_scatter_anomaly(selectedData, fig):
    '''
    点击next时，更新辅助图及样本信息
    '''
    selected_points = fig['data'][0]['selectedpoints']
    columns=['var_94_mean', 'var_355_mean', 'var_246_mean', 'var_101_mean', 'bin']
    note = no_update
    id_ = ts = wspd = rspd = power = pitchAngle = '-'
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
    selectedData = no_update
    patched_fig = no_update
    sr = pd.Series(fig['data'][0]['text'])
    # sr = sr[sr=='离群，未标注']
    if len(sr)>0:
        idx = sr.sample(1).index[0]
        patched_fig = Patch()
        patched_fig['data'][0]['selectedpoints'] = [idx]
    return patched_fig


@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_scatter'), 'figure', allow_duplicate=True),
    Input(get_component_id('select_mapid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_mapid_anomaly(n):
    '''
    点击update时，更新散点图及后台数据
    '''
    fig = no_update
    return no_update, fig

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('select_xaxis'), 'data'),
    Output(get_component_id('select_xaxis'), 'value'),
    Output(get_component_id('select_yaxis'), 'data'),
    Output(get_component_id('select_yaxis'), 'value'),
    Output(get_component_id('select_yaxis2'), 'data'),
    Output(get_component_id('select_yaxis2'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_slect_type_anomaly(plot_type, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [plot_type, set_id]:
        return [no_update]*7
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
    prevent_initial_call=True
    )
def callback_disable_slect_yaxis_anomaly(v):
    return True if v is None else False

@callback(
    Output(get_component_id('select_yaxis2'), 'disabled'),
    Input(get_component_id('select_yaxis'), 'value'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_disable_slect_y2axis_anomaly(v, plot_type):
    return True if v is None or plot_type not in ['时序图', '频谱图'] else False

# @callback(
#     Output(get_component_id('notification'), 'children', allow_duplicate=True),
#     Output(get_component_id('graph'), 'figure'),
#     Input(get_component_id('listItem_ts'), 'value'),
#     Input(get_component_id('select_yaxis'), 'value'),
#     Input(get_component_id('select_yaxis2'), 'value'),
#     State(get_component_id('select_type'), 'value'),
#     State(get_component_id('select_xaxis'), 'value'),
#     State(get_component_id('select_setid'), 'value'),
#     State(get_component_id('select_mapid'), 'value'),
#     prevent_initial_call=True
#     )
# def callback_on_btn_refresh_plot(n, ts, ycol, y2col, plot_type, xcol, set_id, map_id):
#     if None in [ycol, ts]:
#         return no_update, no_update
#     # 设置绘图参数
#     xtitle, xcol, mode = get_simple_plot_parameters(plot_type)
#     name_lst = [None]
#     # 读取绘图数据
#     point_name = tuple(pd.Series([xcol, ycol, y2col]).replace('ts', None).dropna())
#     start_time = pd.to_datetime(ts)
#     try:
#         df, desc_df = utils.read_raw_data(
#             set_id=set_id, 
#             map_id=map_id, 
#             point_name=point_name, 
#             start_time=start_time,
#             end_time=start_time+pd.Timedelta('10m'),
#             sample_cnt=cfg.SIMPLE_PLOT_SAMPLE_NUM,
#             remote=True
#             )
#     except Exception as e:
#         note = dcmpt.notification(title=DBQUERY_FAIL, msg=e, _type='error')
#     else:
#         if len(df)<1:
#             note = dcmpt.notification(title=DBQUERY_NODATA, msg='查无数据', _type='warning')
#     if note!=no_update:
#         return note, no_update         
            
    
#     xtitle = desc_df.loc[xcol, 'column'] if xtitle=='' else xtitle
#     x = df[xcol].tolist() if xcol=='ts' else df[desc_df.loc[xcol, 'var_name']].tolist()
#     x_lst = [x]
#     if ycol is not None:
#         y = df[desc_df.loc[ycol, 'var_name']].tolist()
#         y_lst = [y]
#         if ytitle=='':
#             if plot_type == '频谱图':
#                 ytitle = ycol + f"_({desc_df.loc[ycol, 'unit']})^2"
#             else:
#                 ytitle = desc_df.loc[ycol, 'column']
#     if y2col is not None:
#         y2 = df[desc_df.loc[y2col, 'var_name']].tolist()
#         y2_lst = [y2]
#         if y2title=='':
#             if plot_type == '频谱图':
#                 y2title = ycol + f"_({desc_df.loc[y2col, 'unit']})^2"
#             else:
#                 y2title = desc_df.loc[y2col, 'column']
#     else:
#         y2_lst = [None]
            
#     fig, note = utils.dash_try(
#         note_title='绘图失败',
#         func=simple_plot,
#         x_lst=x_lst, 
#         y_lst=y_lst, 
#         y2_lst=y2_lst,
#         xtitle=xtitle, 
#         ytitle=ytitle,
#         y2title=y2title,
#         name_lst=name_lst,
#         mode=mode,
#         _type=plot_type,
#         ref_freqs=[],    
#         )
#     return note, fig


#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)