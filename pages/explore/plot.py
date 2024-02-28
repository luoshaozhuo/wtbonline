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
from dash import dcc, html, dash_table
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update
import pandas as pd
from functools import partial

from wtbonline._db.rsdb_interface import RSDBInterface
import wtbonline.configure as cfg
from wtbonline._common import utils 
from wtbonline._plot.functions import simple_plot
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '探索'
SECTION_ORDER = 1
ITEM='图形'
ITEM_ORDER = 1
PREFIX =  'explore_plot'

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

CONTAINER_SIZE = cfg.CONTAINER_SIZE

NOW = cfg.NOW
DATE = cfg.DATE
TIME_START = cfg.TIME_START
TIME_END = cfg.TIME_END

GRAPH_TYPE = ['时序图', '散点图', '极坐标图', '频谱图']
GRAPH_PADDING_TOP = cfg.GRAPH_PADDING_TOP
DBQUERY_FAIL = cfg.NOTIFICATION_TITLE_DBQUERY_FAIL
DBQUERY_NODATA = cfg.NOTIFICATION_TITLE_DBQUERY_NODATA
NOTIFICATION_TITLE_GRAPH = cfg.NOTIFICATION_TITLE_GRAPH_FAIL

TABLE_COLUMNS = cfg.TOOLBAR_TABLE_COLUMNS
TABLE_FONT_SIZE = cfg.TOOLBAR_TABLE_FONT_SIZE
TABLE_HEIGHT = cfg.TOOLBAR_TABLE_HEIGHT

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
            dcmpt.date_picker(id=get_component_id('datepicker_start'), label="开始日期", description="可选日期取决于24小时统计数据"),
            dcmpt.time_input(id=get_component_id('time_start'), label="开始时间", value=TIME_START),
            dcmpt.date_picker(id=get_component_id('datepicker_end'), label="结束日期", description="可选日期大于等于开始日期"),
            dcmpt.time_input(id=get_component_id('time_end'), label="结束时间", value=TIME_END),
            dmc.Space(h='10px'),
            dmc.ActionIcon(
                DashIconify(icon="mdi:add-box", width=TOOLBAR_ICON_WIDTH),
                variant="subtle",
                id=get_component_id('icon_add'),
                ),
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"width": TOOLBAR_COMPONENT_WIDTH, "height": TABLE_HEIGHT, 'border':'1px solid silver'},
                children=dash_table.DataTable(
                    id=get_component_id('table'),
                    columns=[{"name": i, "id": i} for i in TABLE_COLUMNS],
                    row_deletable=True,
                    data=[],
                    style_cell={'fontSize':TABLE_FONT_SIZE}
                    ),
                ),
            dmc.Space(h='10px'),
            dcmpt.select(id=get_component_id('select_type'), data=GRAPH_TYPE, value=None, label='类型'),  
            dcmpt.select(id=get_component_id('select_xaxis'), data=[], value=None, label='x坐标（θ坐标）', description='需要先选择类型以及机型编号'),
            dcmpt.select(id=get_component_id('select_yaxis'), data=[], value=None, label='y坐标（r坐标）', description='需要先选择类型以及机型编号'),
            dcmpt.select(id=get_component_id('select_yaxis2'), data=[], value=None, label='y2坐标', description='只适用于时序图'),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                id=get_component_id('btn_refresh'),
                leftIcon=DashIconify(icon="mdi:refresh", width=TOOLBAR_ICON_WIDTH),
                size=TOOLBAR_COMPONENT_SIZE,
                children="刷新图像",
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
    app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
else:
    first_noticifation_output = Output('notficiation_container', 'children', allow_duplicate=True)

dash.register_page(
    __name__,
    section=SECTION,
    section_order=SECTION_ORDER,
    item=ITEM,
    item_order=ITEM_ORDER,
    )

layout =  dmc.NotificationsProvider(children=[
    html.Div(id=get_component_id('notification')),
    dmc.Container(children=[creat_content()], size=CONTAINER_SIZE, pt=HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan=TOOLBAR_HIDE_SMALLER_THAN,
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ])

#%% callback
@callback(
    Output(get_component_id('select_mapid'), 'data'),
    Input(get_component_id('select_setid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_select_mapid_plot(set_id):
    df = cfg.WINDFARM_CONFIGURATION[cfg.WINDFARM_CONFIGURATION['set_id']==set_id]
    data = [] if df is None else [{'value':i, 'label':i} for i in df['map_id']]
    return data

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datepicker_start'), 'disabledDates'),
    Output(get_component_id('datepicker_start'), 'minDate'),
    Output(get_component_id('datepicker_start'), 'maxDate'),
    Output(get_component_id('datepicker_start'), 'value'),
    Input(get_component_id('select_mapid'), 'value'),
    prevent_initial_call=True
    )
def callback_update_datepicker_start_plot(map_id):
    turbine_id = utils.interchage_mapid_and_tid(map_id=map_id)
    df, note = utils.dash_try(
        note_title = DBQUERY_FAIL, 
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
        minDate = DATE
        maxDate = DATE
        disabledDates = [DATE]
    return no_update, disabledDates, minDate, maxDate, None

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
def callback_update_datepicker_start_plot(date_start, maxDate_start, minDate_start, disabledDates_start, date_end, tm):
    minDate = date_start if date_start is not None else minDate_start
    maxDate = maxDate_start
    disabledDates = disabledDates_start
    if (date_end is not None) and (date_start is not None) and (date_start<=date_end):
        value = no_update
    else:
        value = None
    return disabledDates, minDate, maxDate, value

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
def callback_on_slect_type_plot(_type, set_id):
    # 选出所有机型表格中所有机型共有的变量
    if None in [_type, set_id]:
        return [no_update]*7
    cols = ['point_name', 'unit', 'set_id', 'datatype']
    model_point_df, note = utils.dash_dbquery(
        func=RSDBInterface.read_turbine_model_point,
        set_id=set_id, 
        columns=cols, 
        select=[0, 1]
        )
    if note!=no_update:
        return note, *[no_update]*6
    if _type=='时序图':
        x_data = ['时间']
        x_value = '时间'
        y_data = model_point_df['point_name']
        y_value = None
    elif _type=='散点图':
        x_data = model_point_df['point_name']
        x_value = None
        y_data = model_point_df['point_name']
        y_value = None
    elif _type=='极坐标图':
        x_data = model_point_df['point_name'][
                    (model_point_df['point_name'].str.find('角')>-1) & 
                    (model_point_df['unit']=='°')
                    ]
        x_value = None
        y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
        y_value = None    
    elif _type=='频谱图':
        x_data = ['频率']
        x_value = '频率'
        y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
        y_value = None
    x_data = [{'value':i, 'label':i} for i in x_data]
    y_data = [{'value':i, 'label':i} for i in y_data]
    return no_update, x_data, x_value, y_data, y_value, y_data, y_value


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
def callback_on_icon_add_plot(n, set_id, map_id, date_start, date_end, time_start, time_end, tbl_lst):
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
def callback_update_btn_resresh_plot(tbl_lst):
    return True if tbl_lst is None or len(tbl_lst)==0 else False

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('graph'), 'figure'),
    Output(get_component_id('select_xaxis'), 'error'),
    Output(get_component_id('select_yaxis'), 'error'),
    Input(get_component_id('btn_refresh'), 'n_clicks'),
    State(get_component_id('select_type'), 'value'),
    State(get_component_id('table'), 'data'),
    State(get_component_id('select_xaxis'), 'value'),
    State(get_component_id('select_yaxis'), 'value'),
    State(get_component_id('select_yaxis2'), 'value'),
    prevent_initial_call=True
    )
def callback_on_btn_refresh_plot(n, plot_type, table_lst, xcol, ycol, y2col):
    msg = '未选中任何数据'
    error = ['未选中任何数据' if i is None else '' for i in [xcol, ycol]]
    if msg in error:
        return no_update, no_update, *error
    # 设置绘图参数
    xtitle=''
    if plot_type=='时序图':
        xcol = 'ts'
        mode = 'markers+lines'
        _type = 'line'
        xtitle = '时间'
    elif plot_type=='散点图':
        _type = 'scatter'
        mode = 'markers'
    elif plot_type=='极坐标图':
        _type = 'polar'
        mode = 'markers'
    elif plot_type=='频谱图':
        xcol = 'ts'
        _type = 'spectrum'
        mode = 'markers+lines'
        xtitle = '频率Hz'
    
    # 读取绘图数据
    x_lst=[]    
    y_lst=[]
    y2_lst=[]
    name_lst=[]
    ref_freqs=[]
    ytitle=''
    y2title=''
    point_name = tuple(pd.Series([xcol, ycol, y2col]).replace('ts', None).dropna())
    sample_cnt = int(10000/len(table_lst))
    for dct in table_lst:
        try:
            df, desc_df = utils.read_raw_data(
                set_id=dct['set_id'], 
                map_id=dct['map_id'], 
                point_name=point_name, 
                start_time=dct['start_time'],
                end_time=dct['end_time'],
                sample_cnt=sample_cnt,
                remote=True
                )
        except Exception as e:
            note = dcmpt.notification(title=DBQUERY_FAIL, msg=e, _type='error')
            break
        else:
            if len(df)<1:
                note = dcmpt.notification(title=DBQUERY_NODATA, msg='查无数据', _type='warning')
                break
        note = no_update
        name_lst.append(dct['图例号'])
        xtitle = desc_df.loc[xcol, 'column'] if xtitle=='' else xtitle
        x = df[xcol].tolist() if xcol=='ts' else df[desc_df.loc[xcol, 'var_name']].tolist()
        x_lst.append(x)
        if ycol is not None:
            y = df[desc_df.loc[ycol, 'var_name']].tolist()
            y_lst.append(y)
            if ytitle=='':
                if _type == 'spectrum':
                    ytitle = ycol + f"_({desc_df.loc[ycol, 'unit']})^2"
                else:
                    ytitle = desc_df.loc[ycol, 'column']
        if y2col is not None:
            y2 = df[desc_df.loc[y2col, 'var_name']].tolist()
            y2_lst.append(y2)
            if y2title=='':
                if _type == 'spectrum':
                    y2title = ycol + f"_({desc_df.loc[y2col, 'unit']})^2"
                else:
                    y2title = desc_df.loc[y2col, 'column']
        else:
            y2_lst.append(None)
        
    if note!=no_update:
        return note, no_update, *error     
    fig, note = utils.dash_try(
        note_title='绘图失败',
        func=simple_plot,
        x_lst=x_lst, 
        y_lst=y_lst, 
        y2_lst=y2_lst,
        xtitle=xtitle, 
        ytitle=ytitle,
        y2title=y2title,
        name_lst=name_lst,
        mode=mode,
        _type=_type,
        ref_freqs=ref_freqs,    
        )
    return note, fig, *error 

#%% main
if __name__ == '__main__':     
    app.layout = layout
    app.run_server(debug=True)