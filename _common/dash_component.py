import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from dash_iconify import DashIconify
from dash import html
import traceback

import wtbonline.configure as cfg
from wtbonline._db.rsdb_facade import RSDBFacade

def select(id, data:list, value, label, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, 
           description='', disabled=False, clearable=False, withAsterisk=False) :
    if len(data)>1 and not isinstance(data[0], dict):
        data=[{'label':i, 'value':i} for i in data]
    return dmc.Select(
        id=id,
        label=label,
        size=size,
        placeholder="Select one",
        style={"width": width},
        value=value,
        data=data,
        disabled=disabled,
        description=description,
        dropdownPosition='bottom',
        searchable=True,
        clearable=clearable,
        withAsterisk=withAsterisk,
        )

def select_analysis_type(id, data:list, label:str, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
    return select(id=id, data=data, value=data[0], label=label, size=size, width=width, withAsterisk=withAsterisk)

def select_setid(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False): 
    data = cfg.WINDFARM_MODEL_DEVICE['set_id'].unique().tolist()
    return select(id=id, data=data, value=data[0], label='机型编号', size=size, width=width, withAsterisk=withAsterisk)

def select_device_name(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False, description=''):
    return select(id, label="风机编号", data=[], value=None, size=size, width=width, withAsterisk=withAsterisk, description=description)

def multiselect(id, label, description, maxSelectedValues, disabled):
    return dmc.MultiSelect(
        label=label,
        description=description,
        maxSelectedValues=maxSelectedValues,
        size=cfg.TOOLBAR_COMPONENT_SIZE,
        id=id,
        clearable=True,
        searchable=True,
        disabled=disabled,
        style={"width": cfg.TOOLBAR_COMPONENT_WIDTH, "marginBottom": 10},
        )

def multiselect_device_name(id):
    multiselect(id=id, label='风机编号', description='最多选择5台设备', maxSelectedValues=5)

def multiselecdt_var_name(id, disabled=False):
    return multiselect(id=id, label='选择变量名', description='最多选择10个变量', maxSelectedValues=10, disabled=disabled)

# def select_fault_type(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
#     data = cfg.WINDFARM_FAULT_TYPE['name'].unique()
#     return select(id=id, data=None, value=data[0], label='故障类型', size=size, width=width, withAsterisk=withAsterisk)

def select_job_type(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
    type_ = list(cfg.SCHEDULER_JOB_TYPE.keys())
    return select(id, label="任务类型", data=type_, value=type_[-1], size=size, width=width, withAsterisk=withAsterisk)

def date_picker(id, label, description, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
    disabledDates = [cfg.DATE] 
    return dmc.DatePicker(
        id=id,
        size=size,
        label=label,
        dropdownType='modal',
        description=description,
        disabledDates = disabledDates,
        amountOfMonths=1,
        style={"width": width},
        openDropdownOnClear =True,
        withAsterisk=withAsterisk
        )
    
def time_input(id, label, value, description='', size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
    return dmc.TimeInput(
        id=id,
        size=size,
        label=label,
        description=description,
        value=value,
        style={"width": width},
        withAsterisk=withAsterisk
        )
    
def number_input(id, label, value, min, step=1, description='', size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, withAsterisk=False):
    return dmc.NumberInput(
        id=id,
        label=label,
        description=description,
        value=value,
        min=min,
        step=step,
        size=size,
        style={"width": width},
        withAsterisk=withAsterisk
        )  

def notification(title, msg='', _type='info', autoClose=False):
    return dmc.Notification(
        id=f"simple_notify_{np.random.randint(0, 100)}",
        styles={'scroll-behavior':'auto'},
        title=title,
        action="show",
        autoClose=autoClose,
        message=dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=dmc.Text(f'{msg}', style={'maxHeight':'100px', 'white-space':'pre-line'}, size='xs'),
                ),
        color=cfg.NOTIFICATION[_type]['color'],
        icon=DashIconify(icon=cfg.NOTIFICATION[_type]['icon'], width=20),
        )
    
def dash_get_component_id(suffix, prefix=''):
    '''
    用于dash pages，将prefix及suffix拼接成控件ID
    '''
    return prefix + '_' + suffix

def dash_try(note_title, func, *args, **kwargs):
    '''
    用于dash pages，返回func的运行结果及dash-mantine-component的notification控件
    '''
    try:
        rs = func(*args, **kwargs)
        note = None
    except Exception as e:
        rs = None
        note = notification(
            title=note_title,
            msg=f'func={func.__name__}\nargs={args}\nkwargs={kwargs}\n======\n{traceback.format_exc()}',
            _type='error'
            )     
    return rs, note 

def dash_dbquery(func,  not_empty=True,  *args, **kwargs):
    df, note = dash_try(note_title=cfg.NOTIFICATION_TITLE_DBQUERY_FAIL, func=func, *args, **kwargs)
    if not_empty and df is not None and len(df)==0:
        note = notification(
            title=cfg.NOTIFICATION_TITLE_DBQUERY_NODATA,
            msg=f'func={func.__name__},args={args},{kwargs}',
            _type='warning'
            )
    return df, note