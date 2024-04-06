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
from flask_login import current_user

from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
from wtbonline._common import dash_component as dcmpt
from wtbonline._plot import graph_factory
from wtbonline._plot.classes.anomaly import ANOMALY_MATRIX_PLOT_COLOR

#%% constant
SECTION = '识别'
SECTION_ORDER = 3
ITEM='异常状态'
ITEM_ORDER = 1
PREFIX = 'recognize_anomaly'

SELECT_STATUS = [{'label':i, 'value':i} for i in ['异常', '正常']]
SCATTER_PLOT_SAMPLE_NUM = 10000
#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[   
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.select(id=get_component_id('select_device_id'), data=[], value=None, label='风机编号'),
            dmc.Space(h='20px'),
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
            dcmpt.multiselect(
                id=get_component_id('multiselect_yaxis'), 
                label='y坐标', 
                description='时序图y坐标，最多四个', 
                clearable=True, 
                maxSelectedValues=4
                ),
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

def create_toolbar():
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

def create_tab_tools():
    return dmc.Grid(
        gutter="xl",
        children=[
            dmc.Col(
                lg=3,
                md=12,
                children=dmc.Stack(
                    children=[
                        dcmpt.select_general_graph_type(id=get_component_id('select_type_tools')),
                        dcmpt.select(id=get_component_id('select_xaxis_tools'), data=[], value=None, label='x坐标（θ坐标）', ),
                        dcmpt.multiselect(id=get_component_id('multiselect_yaxis_tools'), label='y坐标（r坐标）', clearable=True),
                        ]
                    )
                ),
            dmc.Col(
                lg=8,
                md=12,
                children=dmc.LoadingOverlay(dcc.Graph(id=get_component_id('graph_tools'),config={'displaylogo':False},))
                )
            ]
        ) 

def create_tab_mattrix():
    return dmc.Grid(
        gutter="lg",
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
                children=dmc.LoadingOverlay(dcc.Graph(
                    id=get_component_id('graph_line'),
                    config={'displaylogo':False},
                    ))
                )
            ]
        )        

def create_content():
    return dmc.Tabs(
            children=[
                dmc.TabsList(
                    [
                        dmc.Tab("Mattrix", icon=DashIconify(icon="mdi:dots-grid"), value="mattrix"),
                        dmc.Tab("Tools", icon=DashIconify(icon="mdi:tools"), value="tools"),
                    ]
                ),
                dmc.TabsPanel(create_tab_mattrix(), value="mattrix"),
                dmc.TabsPanel(create_tab_tools(), value="tools"),
            ],
            color="red",
            value="mattrix",
        )

#%% layout
if __name__ == '__main__':     
    import dash
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)
    
dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout = [
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[create_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=create_toolbar()
        )   
    ]

#%% callback
@callback(
    Output(get_component_id('select_device_id'), 'data'),
    Output(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    )
def callback_update_select_device_name_fault(set_id):
    df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['set_id']==set_id]
    data = [] if df is None else [{'label':row['device_name'], 'value':row['device_id']} for _,row in df.iterrows()]
    return data, None

@callback(
    Output(get_component_id('multiselect_yaxis'), 'data'),
    Output(get_component_id('multiselect_yaxis'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    )
def callback_on_slect_type_plot(set_id):
    # 选出所有机型表格中所有机型共有的变量
    if set_id in ['', None]:
        return [], []
    x_data, x_value, y_data, y_values, maxSelectedValues = dcmpt.get_general_plot_selections(set_id, 'Base')
    return y_data, ['powact', 'winspd', 'var_94', 'var_101']

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_scatter'), 'figure'),
    Output(get_component_id('listItem_id'), 'children'),
    Output(get_component_id('listItem_ts'), 'children'),
    Output(get_component_id('listItem_wspd'), 'children'),
    Output(get_component_id('listItem_rspd'), 'children'),
    Output(get_component_id('listItem_power'), 'children'),
    Output(get_component_id('listItem_pitchAngle'), 'children'),
    Output(get_component_id('btn_next'), 'disabled'),
    Input(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_mapid_anomaly(device_id, set_id):
    '''
    map_id改变时，切换散点图，清空辅助图及样本信息
    '''
    if device_id in [None, '']:
        return no_update, {},  *(['-']*6), True
    end_time = pd.Timestamp.now()
    figure, note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,
        func = graph_factory.get('Anomaly')().plot,
        set_id=set_id,
        device_ids=device_id,
        start_time=end_time-pd.Timedelta('365d'),
        end_time=end_time
        )
    figure = {} if figure is None else figure
    return note, figure,  *(['-']*6), True

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_id'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_ts'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_wspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_rspd'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_power'), 'children', allow_duplicate=True),
    Output(get_component_id('listItem_pitchAngle'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_line'), 'figure'),
    Input(get_component_id('graph_scatter'), 'selectedData'),
    Input(get_component_id('graph_scatter'), 'figure'),
    Input(get_component_id('multiselect_yaxis'), 'value'),
    prevent_initial_call=True
    )
def callback_on_select_data_anomaly(selectedData, fig, ycols):
    if pd.Series([selectedData, fig, ycols]).isin([[], None, '']).any():
        return None, *(['-']*6), {}
    columns=['var_94_mean', 'winspd_mean', 'var_246_mean', 'var_101_mean', 'bin', 'set_id', 'device_id']
    note = None
    id_ = ts = wspd = rspd = power = pitchAngle = '-'
    selected_points = fig['data'][0].get('selectedpoints', [])
    if len(selected_points)<1:
        return None, *(['-']*6), {}
    sample_id = fig['data'][0]['customdata'][selected_points[0]]
    # 查询数据样本
    df, note = dcmpt.dash_dbquery(
        func=RSDBFacade.read_statistics_sample,
        id_=sample_id,
        columns=columns
        )
    if note is not None:
        return note, *(['-']*6), {}
    # 绘制曲线图
    sr = df.round(2).squeeze()
    start_time = sr['bin']
    obj = graph_factory.get('Base')(row_height=200, width=400, showlegend=False)
    obj.init(var_names=ycols)
    figure, note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,
        func = obj.plot,
        set_id=sr['set_id'],
        device_ids=sr['device_id'],
        start_time=start_time,
        end_time=start_time+pd.Timedelta('10m'),
        title=' '
        )
    if note is not None:
        return note, *(['-']*6), {}        
    # 更新样本信息
    id_ = sample_id    
    ts = sr['bin']
    wspd = f'{sr["winspd_mean"]} m/s'
    rspd = f'{sr["var_94_mean"]} rpm'
    power = f'{sr["var_246_mean"]} kWh'
    pitchAngle = f'{sr["var_101_mean"]} °'
    return note, id_, ts, wspd, rspd, power, pitchAngle, figure

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
    State(get_component_id('select_device_id'), 'value'),
    State(get_component_id('select_label'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_update_anomaly(n, selectedData, set_id, device_id, label):
    if selectedData is None or len(selectedData)==0 or label is None:
        return None, no_update
    _ = Patch()
    patched_fig = Patch()
    # 获取当前用户名
    username, note = dcmpt.dash_get_username(current_user, __name__ == '__main__')
    if note is not None:
        return note, no_update
    # 构造新记录
    create_time = pd.Timestamp.now()
    sample_id = selectedData['points'][0]['customdata']
    new_record = dict(
        username=username, 
        set_id=set_id, 
        device_id=device_id,
        sample_id=sample_id, 
        create_time=create_time,
        is_anomaly=1 if label=='异常' else -1             
        )
    _, note = dcmpt.dash_dbquery(
        RSDBFacade.insert,
        df = new_record,
        tbname = 'model_label'
        )
    if note is not None:
        return note, no_update
    idx = selectedData['points'][0]['pointNumber']
    patched_fig['data'][0]['text'][idx] = label
    patched_fig['data'][0]['marker']['color'][idx] = ANOMALY_MATRIX_PLOT_COLOR[label]
    patched_fig['data'][0]['marker']['opacity'][idx] = 1
    return no_update, patched_fig

@callback(
    Output(get_component_id('select_xaxis_tools'), 'data'),
    Output(get_component_id('select_xaxis_tools'), 'value'),
    Output(get_component_id('multiselect_yaxis_tools'), 'data'),
    Output(get_component_id('multiselect_yaxis_tools'), 'value'),
    Output(get_component_id('multiselect_yaxis_tools'), 'maxSelectedValues'),
    Input(get_component_id('select_type_tools'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_on_slect_type_anomaly(type_, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [type_, set_id]:
        return [], None, [], [], 1
    x_data, x_value, y_data, y_values, maxSelectedValues = dcmpt.get_general_plot_selections(set_id, type_)
    return x_data, x_value, y_data, y_values, maxSelectedValues


@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph_tools'), 'figure'), 
    Input(get_component_id('select_device_id'), 'value'),
    Input(get_component_id('select_xaxis_tools'), 'value'),
    Input(get_component_id('multiselect_yaxis_tools'), 'value'),
    Input(get_component_id('listItem_ts'), 'children'),
    Input(get_component_id('select_type_tools'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True 
)
def callback_update_graph_tools_anomaly(device_id, xcol, ycols, start_time, plot_type, set_id):
    if pd.Series([device_id, xcol, ycols, start_time, plot_type]).isin([[],None,'','-']).any():
        return None, {}
    var_names = pd.Series([xcol] + ycols).replace('ts', None).dropna()
    start_time = pd.to_datetime(start_time)
    end_time = start_time  + pd.Timedelta('10m')
    obj = graph_factory.get(plot_type)()
    obj.init(var_names=var_names)
    fig,note = dcmpt.dash_try(
        note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,
        func=obj.plot,
        set_id=set_id,
        device_ids=device_id,
        start_time=start_time,
        end_time=end_time
        )
    fig = {} if fig is None else fig
    return note, fig

#%% main
if __name__ == '__main__':     
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=True)