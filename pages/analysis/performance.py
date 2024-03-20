'''
作者：luosz
创建日期： 2024.02.18
描述：分析——性能
    1、功率曲线
    2、功率差异
'''

#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html, dash_table
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '分析'
SECTION_ORDER = 1
ITEM='性能'
ITEM_ORDER = 1
PREFIX =  'analysis_performance'

GRAPH_CONF = cfg.GRAPH_CONF[cfg.GRAPH_CONF['item']==ITEM].set_index('clause')

TABLE_COLUMNS = cfg.TOOLBAR_TABLE_COLUMNS
TABLE_FONT_SIZE = cfg.TOOLBAR_TABLE_FONT_SIZE
TABLE_HEIGHT = cfg.TOOLBAR_TABLE_HEIGHT

#%% function
get_component_id = partial(utils.dash_get_component_id, prefix=PREFIX)

#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_analysis_type(id=get_component_id('select_type'), data=list(GRAPH_CONF.index), label='分析类型'),
            dcmpt.select_setid(id=get_component_id('select_setid')),
            dcmpt.multiselect_device_name(id=get_component_id('multiselect_device_name')),
            dcmpt.date_picker(id=get_component_id('datepicker_end'), label="结束日期", description="此日期的零点为区间右端"),
            dcmpt.number_input(id=get_component_id('input_span'), label='时长', value=90, min=1, description='单位，天'),
            dmc.Space(h='10px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_refresh'),
                leftIcon=DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="刷新图像",
                ), 
            dmc.Space(h='200px'),
            ]
        )

def creat_toolbar():
    return dmc.Aside(
        fixed=True,
        width={'base': cfg.TOOLBAR_SIZE},
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
    return  dmc.LoadingOverlay(       
            dcc.Graph(
                id=get_component_id('graph'),
                config={'displaylogo':False},
                )
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
    dmc.Container(children=[creat_content()], size=cfg.CONTAINER_SIZE, pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=cfg.TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ]

#%% callback
@callback(
    Output(get_component_id('multiselect_device_name'), 'data'),
    Output(get_component_id('multiselect_device_name'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_multiselect_device_name_performance(set_id):
    df = cfg.WINDFARM_MODEL_DEVICE[cfg.WINDFARM_MODEL_DEVICE['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['device_name']]
    return data, None

@callback(
    Output(get_component_id('datepicker_end'), 'minDate'),
    Input(get_component_id('multiselect_device_name'), 'value'),
    State(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_start_performance(date_start, maxDate_start, minDate_start, disabledDates_start, date_end, tm):
    
    minDate = date_start if date_start is not None else minDate_start
    maxDate = maxDate_start
    disabledDates = disabledDates_start
    if (date_end is not None) and (date_start is not None) and (date_start<=date_end):
        value = no_update
    else:
        value = None
    return disabledDates, minDate, maxDate, value

# @callback(
#     Output(get_component_id('select_setid'), 'error'),
#     Output(get_component_id('multiselect_device_name'), 'error'),
#     Output(get_component_id('datepicker_start'), 'error'),
#     Output(get_component_id('datepicker_end'), 'error'),
#     Output(get_component_id('time_end'), 'error'),
#     Output(get_component_id('table'), 'data'),  
#     Input(get_component_id('icon_add'), 'n_clicks'),
#     State(get_component_id('select_setid'), 'value'),
#     State(get_component_id('multiselect_device_name'), 'value'),
#     State(get_component_id('datepicker_start'), 'value'),
#     State(get_component_id('datepicker_end'), 'value'),
#     State(get_component_id('time_start'), 'value'),
#     State(get_component_id('time_end'), 'value'),
#     State(get_component_id('table'), 'data'),
#     prevent_initial_call=True    
#     )
# def callback_on_icon_add_performance(n, set_id, map_id, date_start, date_end, time_start, time_end, tbl_lst):
#     tbl_df = pd.DataFrame(tbl_lst, columns=TABLE_COLUMNS)
#     errs = ['变量不能为空' if i is None else '' for i in [set_id, map_id, date_start, date_end, time_end]]
#     data = no_update
#     if time_start.split('T')[1] >= time_end.split('T')[1]:
#         errs[-1] = '需要修改结束时间或开始时间'
#     if (pd.Series(errs)=='').all():
#         start_time=utils.dash_make_datetime(date_start, time_start)
#         end_time=utils.dash_make_datetime(date_end, time_end)
#         temp = pd.DataFrame([['new', map_id, start_time, end_time, set_id]], columns=TABLE_COLUMNS)
#         data = pd.concat([tbl_df, temp], ignore_index=True).drop_duplicates(subset=['map_id', 'start_time', 'end_time'])
#         data[TABLE_COLUMNS[0]] = [f'E{i}' for i in range(len(data))]
#         data = data.to_dict('records')
#     return *errs, data

# @callback(
#     Output(get_component_id('btn_refresh'), 'disabled'), 
#     Input(get_component_id('table'), 'data'),  
#     prevent_initial_call=True 
# )
# def callback_update_btn_resresh_performance(tbl_lst):
#     return True if tbl_lst is None or len(tbl_lst)==0 else False

# @callback(
#     Output(get_component_id('notification'), 'children', allow_duplicate=True),
#     Output(get_component_id('graph'), 'figure'),
#     Input(get_component_id('btn_refresh'), 'n_clicks'),
#     State(get_component_id('table'), 'data'),
#     State(get_component_id('select_type'), 'value'),
#     prevent_initial_call=True
#     )
# def callback_on_btn_refresh_performance(n, tbl_lst, _type):
#     target_df = pd.DataFrame(tbl_lst)
#     graph = None
#     note = None
#     if len(target_df)>0:
#         graph, note = utils.dash_try(
#             note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,   
#             func=GRAPH_CONF.loc[_type]['class'], 
#             target_df = target_df,
#             title = _type
#             )
#     figure = no_update if graph is None else graph.figs[0]
#     return note, figure


#%% main
if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)   
    app.layout = layout
    app.run_server(debug=True)