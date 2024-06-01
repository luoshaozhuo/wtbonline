'''
作者：luosz
创建日期： 2024.02.21
描述：后台任务管理
'''
#%% import
import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from dash import Output, Input, html, dcc, State, callback, no_update, dash_table, ctx
import pandas as pd
import numpy as np
from functools import partial
from flask_login import current_user
import requests
import time
from zlib import crc32

from wtbonline._db.rsdb_facade import RSDBFC
import wtbonline.configure as cfg
from wtbonline._common import dash_component as dcmpt

#%% constant
SECTION = '任务调度'
SECTION_ORDER = 4
ITEM = '后台任务'
ITEM_ORDER = 1
PREFIX = 'scheduler_job2'

TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TABLE_FONT_SIZE = '2px'
TABLE_HEIGHT = '200PX'

COLUMNS_DCT = {
    'task_id':'任务id', 
    'status':'状态', 
    'type':'类型', 
    'task_parameter':'参数', 
    'start_time':'开始时间', 
    'next_run_time':'下次运行时间',
    'func':'目标函数', 
    'function_parameter':'目标函数参数', 
    'username':'拥有者'
}
TABLE_COLUMNS = list(COLUMNS_DCT.keys())
TABLE_HEADERS = list(COLUMNS_DCT.values())

UNIT = [{'label':i, 'value':i} for i in cfg.SCHEDULER_JOB_INTER_UNIT]

JOB_DF = cfg.SCHEDULER_JOB_PARAMETER.set_index('name')

#%% function
get_component_id = partial(dcmpt.dash_get_component_id, prefix=PREFIX)

def func_read_task_table():
    apschduler_df, note = dcmpt.dash_dbquery(func=RSDBFC.read_apscheduler_jobs, not_empty=False)
    if note is not None:
        return no_update, note
    next_run_time  = apschduler_df['next_run_time'].fillna('0').astype(int).replace(0, np.nan)
    apschduler_df['next_run_time'] = pd.to_datetime(next_run_time, unit='s') + pd.Timedelta('8h')
    timed_task_df, note = dcmpt.dash_dbquery(func=RSDBFC.read_timed_task, not_empty=False)
    if note is not None:
        return no_update, note   
    df = pd.merge(timed_task_df, apschduler_df, how='left', left_on='task_id', right_on='id')
    return df[TABLE_COLUMNS], None

def func_render_table():
    data, note = func_read_task_table()
    if note is None:
        data.columns = TABLE_HEADERS
        data = data.to_dict('records')
    return data, note

def get_task_id(func, kwargs):
    # data = f'{func}{kwargs}'
    # id_ = crc32(data.encode(encoding='UTF-8'))
    # return str(id_)
    return(f'{np.random.randint(0, 10000000000):010d}')


#%% component
def create_toolbar_content():
    return dmc.Stack(
        spacing=0, 
        px=cfg.TOOLBAR_PADDING, 
        children=[
            dcmpt.select_job_type(id=get_component_id('select_type'),  withAsterisk=True),
            dmc.DatePicker(
                id=get_component_id('datepicker_start_date'),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                label="开始日期",
                dropdownType='modal',
                description="任务开始执行日期",
                minDate = pd.Timestamp.now().date(),
                style={"width": cfg.TOOLBAR_COMPONENT_WIDTH},
                openDropdownOnClear =True,
                withAsterisk=True
                ),
            dcmpt.time_input(
                id=get_component_id('input_start_time'), 
                label="开始时间", 
                value=cfg.TIME_START, 
                description="任务开始执行时间",  
                withAsterisk=True
                ),
            dcmpt.number_input(
                id=get_component_id('input_interval'), 
                label='执行周期', 
                min=1, 
                value=1
                ),
            dcmpt.select(
                id=get_component_id('select_interval_unit'), 
                data=UNIT, 
                value=cfg.SCHEDULER_JOB_INTER_UNIT[0], 
                label='周期单位'
                ),
            dmc.Divider(mt='20px'),
            dcmpt.select(
                id=get_component_id('select_func'), 
                data=list(JOB_DF.index), 
                value=list(JOB_DF.index)[0], 
                label='任务函数',  
                withAsterisk=True
                ),
            dmc.DatePicker(
                id=get_component_id('datepicker_end_date'),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                label="目标函数数据结束日期",
                dropdownType='modal',
                maxDate = pd.Timestamp.now().date(),
                style={"width": cfg.TOOLBAR_COMPONENT_WIDTH},
                openDropdownOnClear =True
                ),
            dcmpt.number_input(
                id=get_component_id('input_delta'), 
                label='目标函数数据范围（天）', 
                min=1, 
                value=20, 
                description="从结束日期往前数"
                ),
            dcmpt.number_input(
                id=get_component_id('input_minimun_sample'), 
                label='最少记录数', 
                min=1, 
                value=3000, 
                description="少于此数函数停止执行"
                ),
            dcmpt.number_input(id=get_component_id('input_num_output'), label='输出记录数', min=1, value=20),
            dmc.Space(h='20px'),
            dmc.Button(
                fullWidth=True,
                disabled=True,
                id=get_component_id('btn_add'),
                leftIcon=DashIconify(icon="mdi:add_circle_outline", width=cfg.TOOLBAR_ICON_WIDTH),
                size=cfg.TOOLBAR_COMPONENT_SIZE,
                children="添加任务",
                ), 
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
    return dmc.Stack(
        children=[
            dmc.Space(h='20px'),
            dmc.Group(
                children = [
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:play-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='teal'),
                        variant="subtle",
                        id=get_component_id('acticon_start'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:pause-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='orange'),
                        variant="subtle",
                        id=get_component_id('acticon_pause'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:refresh", width=cfg.TOOLBAR_ICON_WIDTH, color='blue'),
                        variant="subtle",
                        id=get_component_id('acticon_refresh'),
                        ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:remove-circle-outline", width=cfg.TOOLBAR_ICON_WIDTH, color='red'),
                        variant="subtle",
                        id=get_component_id('acticon_delete'),
                        )
                    ]
                ),
            dmc.LoadingOverlay(
                    dash_table.DataTable(
                        id=get_component_id('datatable_job'),
                        columns=[{'name': i, 'id': i} for i in TABLE_HEADERS],                           
                        row_deletable=False,
                        row_selectable="single",
                        page_action='native',
                        page_current= 0,
                        page_size= 20,
                        style_header = {'font-weight':'bold'},
                        style_table = {'font-size':'small', 'overflowX': 'auto'},
                        style_data={
                            'height': 'auto',
                            'lineHeight': '15px'
                            },                
                    )  
                )
            ]
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
    dmc.Container(children=[creat_content()], size='lg',pt=cfg.HEADER_HEIGHT),
    dmc.MediaQuery(
        smallerThan="lg",
        styles={"display": "none"},
        children=creat_toolbar()
        )
    ]

#%% callback
@callback(
    Output(get_component_id('datepicker_start_date'), 'minDate'),
    Output(get_component_id('datepicker_start_date'), 'click'),
)
def callback_update_datepicker_start_date(n):
    return pd.Timestamp.now().date()

@callback(
    Output(get_component_id('acticon_start'), 'disabled'), 
    Output(get_component_id('acticon_pause'), 'disabled'), 
    Output(get_component_id('acticon_delete'), 'disabled'), 
    Input(get_component_id('datatable_job'), 'selected_rows'),
    State(get_component_id('datatable_job'), 'data'),
    )
def callback_disable_actionicons_job(rows, data):
    rev = [True]*3
    if (data is not None) and len(data)>0 and (rows is not None) and len(rows)>0:
        row = pd.DataFrame(data).iloc[rows[0]].squeeze()
        status = row['状态']
        if status=='JOB_ADDED':
            rev = [True, False, False]
        elif row['类型']=='定时任务' and status in ('JOB_EXECUTED', 'JOB_ERROR', 'JOB_EXECUTED', 'STARTED'):
            rev = [True, False, False]
        elif status=='JOB_PAUSE':
            rev = [False, True, False]
        elif status=='CREATED':
            rev = [False, True, True]
    return rev

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'data', allow_duplicate=True),
    Input(get_component_id('acticon_refresh'), 'n_clicks'),
    prevent_initial_call=True,
    )
def callback_on_refresh_job(n):
    data, note = func_render_table()
    return note, data

@callback(
    Output(get_component_id('input_interval'), 'disabled'),
    Output(get_component_id('select_interval_unit'), 'disabled'),
    Output(get_component_id('input_start_time'), 'value'),
    Output(get_component_id('input_interval'), 'withAsterisk'),
    Output(get_component_id('select_interval_unit'), 'withAsterisk'),
    Output(get_component_id('datepicker_end_date'), 'maxDate'),
    Input(get_component_id('select_type'), 'value'),
    )
def callback_on_select_type_job(type_):
    disabled = False if type_=='定时任务' else True
    withAsterisk = not disabled
    start_time = '2022-02-02T00:00:00' if type_=='定时任务' else pd.Timestamp.now()
    return disabled, disabled, start_time, withAsterisk, withAsterisk, pd.Timestamp.now().date()

@callback(
    Output(get_component_id('datepicker_end_date'), 'value'),
    Input(get_component_id('select_func'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    )
def callback_update_datepicker_end_date_job(func, type_):
    return None

@callback(
    Output(get_component_id('btn_add'), 'disabled'),
    Output(get_component_id('datepicker_end_date'), 'disabled'),
    Output(get_component_id('input_delta'), 'disabled'),
    Output(get_component_id('input_minimun_sample'), 'disabled'),
    Output(get_component_id('input_num_output'), 'disabled'),
    Output(get_component_id('datepicker_end_date'), 'withAsterisk'),
    Output(get_component_id('input_delta'), 'withAsterisk'),
    Output(get_component_id('input_minimun_sample'), 'withAsterisk'),
    Output(get_component_id('input_num_output'), 'withAsterisk'),
    Input(get_component_id('select_func'), 'value'),
    Input(get_component_id('datepicker_end_date'), 'value'),
    Input(get_component_id('input_delta'), 'value'),
    Input(get_component_id('input_minimun_sample'), 'value'),
    Input(get_component_id('input_num_output'), 'value'),
    Input(get_component_id('select_type'), 'value'),
    )
def callback_check_input_components_job(func, v_end_date, v_delta, v_minimun_sample, v_num_output, type_):
    if func in (None, ''):
        return True, *[True]*4, *[False]*4
    end_date = JOB_DF.loc[func, 'end_date']
    if type_=='定时任务' and func=='数据统计报告': 
        end_date = False
    delta = JOB_DF.loc[func, 'delta']
    minimun_sample = JOB_DF.loc[func, 'minimun_sample']
    num_output = JOB_DF.loc[func, 'num_output']
    withAsterisk = [end_date, delta, minimun_sample, num_output]
    disabled = [not i for i in withAsterisk]
    # 必须字段不可以为空
    btn_add = pd.Series([v_end_date, v_delta, v_minimun_sample, v_num_output])
    btn_add = btn_add.isin([None, '']) | btn_add.isna()
    btn_add = btn_add[withAsterisk].any()
    return btn_add, *disabled, *withAsterisk

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('acticon_refresh'), 'n_clicks'),
    Output(get_component_id('datepicker_start_date'), 'error'),
    Input(get_component_id('btn_add'), 'n_clicks'),
    State(get_component_id('select_type'), 'value'),
    State(get_component_id('datepicker_start_date'), 'value'),
    State(get_component_id('input_start_time'), 'value'), 
    State(get_component_id('input_interval'), 'value'),
    State(get_component_id('select_interval_unit'), 'value'),
    State(get_component_id('select_func'), 'value'),
    State(get_component_id('datepicker_end_date'), 'value'),
    State(get_component_id('input_delta'), 'value'), 
    State(get_component_id('input_minimun_sample'), 'value'), 
    State(get_component_id('input_num_output'), 'value'),  
    State(get_component_id('acticon_refresh'), 'n_clicks'),  
    prevent_initial_call=True,
    )
def callback_on_btn_add_job(
    n, type_, start_date, start_time, interval, unit, func, end_date, delta, 
    minimum_sample, num_output, n2
    ):
    # 检查输入
    if start_date in [None, '']:
        return no_update, no_update, '选择一个日期'     
    esisted_job, note = dcmpt.dash_dbquery(RSDBFC.read_timed_task)
    if esisted_job is None:
        return note, no_update, ''
   # 获取任务发布者
    username, note = dcmpt.dash_get_username(current_user, __name__=='__main__')
    if note is not None:
        return note, no_update, ''
    job_start_time = ' '.join([start_date, start_time.split('T')[1]])
    task_parameter = {'misfire_grace_time':cfg.MISFIRE_GRACE_TIME}
    if type_=='定时任务':
        task_parameter.update({unit:interval})
    # 构造任务参数
    end_time = end_date+' 00:00:00' if (end_date is not None and end_date!='') else ''
    function_parameter = dict(
        end_time = end_time,
        delta = delta,
        minimum = minimum_sample,
        nsample = num_output,
        )
    task_id = get_task_id(func, function_parameter)
    function_parameter.update({'task_id':task_id})
    # # 检查是否有重复任务
    # df, note = dcmpt.dash_dbquery(func=RSDBFC.read_timed_task, not_empty=False)
    # if note is not None:
    #     return note, no_update, ''
    # if (df['id']==task_id).any():
    #    return dcmpt(title='重复任务', msg=f'请先删除重复任务, task_id={task_id}', _type='error'), no_update, ''
    # 构造timed_job记录
    dct = dict(
        task_id=task_id,
        status='CREATED',
        func=func,
        type=type_,
        start_time=job_start_time,
        task_parameter=f'{task_parameter}',
        function_parameter=f'{function_parameter}',
        username=username,
        update_time=pd.Timestamp.now()
        )
    # 更新数据库
    _, note = dcmpt.dash_dbquery(
        func=RSDBFC.insert,
        df=dct,
        tbname = 'timed_task'
        )
    if note is not None:
        return note, no_update, ''
    # 更新页面表格
    n2 = 0 if n2 is None else n2+1
    note = dcmpt.notification(
        title='已添加任务',
        msg=f'{type_} {func}',
        _type='success',
        autoClose=2000
        )
    return note, n2, ''

@callback(
    Output(get_component_id('notification'), 'children', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'data', allow_duplicate=True),
    Output(get_component_id('datatable_job'), 'selected_rows', allow_duplicate=True),   
    Input(get_component_id('acticon_start'), 'n_clicks'),
    Input(get_component_id('acticon_pause'), 'n_clicks'),
    Input(get_component_id('acticon_delete'), 'n_clicks'),
    State(get_component_id('datatable_job'), 'data'),
    State(get_component_id('datatable_job'), 'selected_rows'),
    prevent_initial_call=True,
    )
def timed_task_on_btn_start_pause_delete(n1, n2, n3, data, rows):  
    # 只有单行，因为datatable不能多选
    row = pd.DataFrame(data).iloc[rows[0], :]
    _id = ctx.triggered_id
    url = cfg.SCHEDULER_URL
    timeout = cfg.SCHEDULER_TIMEOUT
    data = no_update
    now = pd.Timestamp.now()
    status = row['状态']
    for _ in range(3):
        try:
            if _id==get_component_id('acticon_start'):
                RSDBFC.update('timed_task', {'status':'STARTED', 'update_time':now}, eq_clause={'task_id':row['任务id']})
                if status == 'CREATED':
                    task_parameter = eval(row['参数'])
                    funtion_parameter = eval(row['目标函数参数'])
                    funtion_parameter.update({"task_id":row['任务id']})
                    key_ = 'run_date' if row['类型']=='一次性任务' else 'start_date'
                    kwargs = {
                        'id':f"{row['任务id']}", 
                        'func':JOB_DF.loc[row['目标函数'], 'func'],
                        'trigger':cfg.SCHEDULER_JOB_TYPE[row['类型']],
                        key_:row['开始时间'],
                        'kwargs':funtion_parameter,
                        }
                    kwargs.update(task_parameter)
                    response = requests.post(url, json=kwargs, timeout=timeout)
                else:
                    response = requests.post(url+f"/{row['任务id']}/resume", timeout=timeout)
            elif _id==get_component_id('acticon_pause'):
                RSDBFC.update('timed_task', {'status':'JOB_PAUSE', 'update_time':now}, eq_clause={'task_id':row['任务id']})
                response = requests.post(url+f"/{row['任务id']}/pause", timeout=timeout)
            elif _id==get_component_id('acticon_delete'):
                RSDBFC.update('timed_task', {'status':'DELETE', 'update_time':now}, eq_clause={'task_id':row['任务id']})
                response = requests.delete(url+f"/{row['任务id']}", timeout=timeout)        
        except Exception as e:
            note = dcmpt.notification(
                title=cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL, 
                msg=f'{row["任务id"]} {row["目标函数"]} 错误信息 {e}',
                _type='error'
                ) 
            break
        if response.ok == True:
            data, note = func_render_table()
            if note is None:
                note = dcmpt.notification(
                    title=cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_SUCCESS, 
                    msg=f'{row["任务id"]} {row["目标函数"]}', 
                    _type='success',
                    autoClose=2000
                    )
            break
        time.sleep(1)
    else:
        # 尝试三次失败后输出错误提示
        RSDBFC.update('timed_task', {'status':status, 'update_time':now}, eq_clause={'task_id':row['任务id']})
        note = dcmpt.notification(
            title=cfg.NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL, 
            msg=f'{row["任务id"]} {row["目标函数"]} 提交超时 {response.text}', 
            _type='error'
            )       
    return note, data, []


#%% main
if __name__ == '__main__':     
    layout =  dmc.NotificationsProvider(children=layout)
    app.layout = layout
    app.run_server(debug=False)