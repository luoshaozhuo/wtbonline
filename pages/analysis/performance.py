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

from wtbonline._db.rsdb_interface import RSDBInterface
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
            dcmpt.select_mapid(id=get_component_id('select_mapid')),
            dcmpt.date_picker(id=get_component_id('datepicker_start'), label="开始日期", description="可选日期取决于24小时统计数据"),
            dcmpt.time_input(id=get_component_id('time_start'), label="开始时间", value=cfg.TIME_START),
            dcmpt.date_picker(id=get_component_id('datepicker_end'), label="结束日期", description="可选日期大于等于开始日期"),
            dcmpt.time_input(id=get_component_id('time_end'), label="结束时间", value=cfg.TIME_END),
            dmc.Space(h='10px'),
            dmc.ActionIcon(
                DashIconify(icon="mdi:add-box", width=cfg.TOOLBAR_ICON_WIDTH),
                variant="subtle",
                id=get_component_id('icon_add'),
                ),
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"width": cfg.TOOLBAR_COMPONENT_WIDTH, "height": TABLE_HEIGHT, 'border':'1px solid silver'},
                children=dash_table.DataTable(
                    id=get_component_id('table'),
                    columns=[{"name": i, "id": i} for i in TABLE_COLUMNS],
                    row_deletable=True,
                    data=[],
                    style_cell={'fontSize':TABLE_FONT_SIZE}
                    ),
                ),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_refresh'),
                leftIcon=DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="刷新图像",
                ), 
            dmc.Space(h='100px'),
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
    Output(get_component_id('select_mapid'), 'data'),
    Output(get_component_id('select_mapid'), 'value'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_performance(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data, None

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_start'), 'disabledDates'),
    Output(get_component_id('datepicker_start'), 'minDate'),
    Output(get_component_id('datepicker_start'), 'maxDate'),
    Input(get_component_id('select_mapid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_start_performance(map_id):
    if map_id is None:
        return [no_update]*4
    turbine_id = utils.interchage_mapid_and_tid(map_id=map_id)
    df, note = utils.dash_try(
        note_title = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL, 
        func=RSDBInterface.read_statistics_daily, 
        turbine_id=turbine_id if turbine_id is not None else '', 
        columns=['date']
        )
    if df is None:
        return note, no_update, no_update, no_update
    if len(df)>0:
        availableDates = df['date'].squeeze()
        minDate = availableDates.min()
        maxDate = availableDates.max()
        disabledDates = pd.date_range(minDate, maxDate)
        disabledDates = disabledDates[~disabledDates.isin(availableDates)]
        disabledDates = [i.date().isoformat() for i in disabledDates]
    else:
        minDate = cfg.DATE
        maxDate = cfg.DATE
        disabledDates = [cfg.DATE]
    return no_update, disabledDates, minDate, maxDate

@callback(
    Output(get_component_id('datepicker_end'), 'disabledDates'),
    Output(get_component_id('datepicker_end'), 'minDate'),
    Output(get_component_id('datepicker_end'), 'maxDate'),
    Output(get_component_id('datepicker_end'), 'value'),
    Input(get_component_id('datepicker_start'), 'value'),
    State(get_component_id('datepicker_start'), 'maxDate'),
    State(get_component_id('datepicker_start'), 'minDate'),
    State(get_component_id('datepicker_start'), 'disabledDates'),
    State(get_component_id('datepicker_end'), 'value'),
    State(get_component_id('time_end'), 'value'),
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

@callback(
    Output(get_component_id('select_setid'), 'error'),
    Output(get_component_id('select_mapid'), 'error'),
    Output(get_component_id('datepicker_start'), 'error'),
    Output(get_component_id('datepicker_end'), 'error'),
    Output(get_component_id('time_end'), 'error'),
    Output(get_component_id('table'), 'data'),  
    Input(get_component_id('icon_add'), 'n_clicks'),
    State(get_component_id('select_setid'), 'value'),
    State(get_component_id('select_mapid'), 'value'),
    State(get_component_id('datepicker_start'), 'value'),
    State(get_component_id('datepicker_end'), 'value'),
    State(get_component_id('time_start'), 'value'),
    State(get_component_id('time_end'), 'value'),
    State(get_component_id('table'), 'data'),
    prevent_initial_call=True    
    )
def callback_on_icon_add_performance(n, set_id, map_id, date_start, date_end, time_start, time_end, tbl_lst):
    tbl_df = pd.DataFrame(tbl_lst, columns=TABLE_COLUMNS)
    errs = ['变量不能为空' if i is None else '' for i in [set_id, map_id, date_start, date_end, time_end]]
    data = no_update
    if time_start.split('T')[1] >= time_end.split('T')[1]:
        errs[-1] = '需要修改结束时间或开始时间'
    if (pd.Series(errs)=='').all():
        start_time=utils.dash_make_datetime(date_start, time_start)
        end_time=utils.dash_make_datetime(date_end, time_end)
        temp = pd.DataFrame([['new', map_id, start_time, end_time, set_id]], columns=TABLE_COLUMNS)
        data = pd.concat([tbl_df, temp], ignore_index=True).drop_duplicates(subset=['map_id', 'start_time', 'end_time'])
        data[TABLE_COLUMNS[0]] = [f'E{i}' for i in range(len(data))]
        data = data.to_dict('records')
    return *errs, data

@callback(
    Output(get_component_id('btn_refresh'), 'disabled'), 
    Input(get_component_id('table'), 'data'),  
    prevent_initial_call=True 
)
def callback_update_btn_resresh_performance(tbl_lst):
    return True if tbl_lst is None or len(tbl_lst)==0 else False

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('table'), 'data'),
    State(get_component_id('select_type'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_performance(n, tbl_lst, _type):
    target_df = pd.DataFrame(tbl_lst)
    graph = None
    note = None
    if len(target_df)>0:
        graph, note = utils.dash_try(
            note_title=cfg.NOTIFICATION_TITLE_GRAPH_FAIL,   
            func=GRAPH_CONF.loc[_type]['class'], 
            target_df = target_df,
            title = _type
            )
    figure = no_update if graph is None else graph.figs[0]
    return note, figure


#%% main
if __name__ == '__main__':  
    layout =  dmc.NotificationsProvider(children=layout)   
    app.layout = layout
    app.run_server(debug=True)