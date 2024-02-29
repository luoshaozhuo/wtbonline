import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from dash_iconify import DashIconify
from dash import html

import wtbonline.configure as cfg
from wtbonline._db.rsdb_interface import RSDBInterface

def select(id, data:list, value, label, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH, description='', disabled=False, clearable=False):
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
        searchable=True,
        clearable=clearable
        )

def select_analysis_type(id, data:list, label:str, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    return select(id=id, data=data, value=data[0], label=label, size=size, width=width)

def select_setid(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH): 
    data = cfg.WINDFARM_INFORMATION['set_id']
    return select(id=id, data=data, value=None, label='机型编号', size=size, width=width)

def select_mapid(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    return select(id, label="风机编号", data=[], value=None, size=size, width=width)

def select_job_type(id, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    return select(id, label="任务类型", data=cfg.SCHEDULER_JOB_TYPE, value=cfg.SCHEDULER_JOB_TYPE[0], size=size, width=width)

def date_picker(id, label, description, size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    minDate = cfg.DATE
    maxDate = cfg.DATE
    disabledDates = [cfg.DATE] 
    return dmc.DatePicker(
        id=id,
        size=size,
        label=label,
        dropdownType='modal',
        description=description,
        minDate = minDate,
        maxDate = maxDate,
        disabledDates = disabledDates,
        amountOfMonths=1,
        style={"width": width},
        initialLevel='year',
        openDropdownOnClear =True
        )
    
def time_input(id, label, value, description='', size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    return dmc.TimeInput(
        id=id,
        size=size,
        label=label,
        description=description,
        value=value,
        style={"width": width},
        )
    
def number_input(id, label, value, min, step=1, description='', size=cfg.TOOLBAR_COMPONENT_SIZE, width=cfg.TOOLBAR_COMPONENT_WIDTH):
    return dmc.NumberInput(
        id=id,
        label=label,
        description=description,
        value=value,
        min=min,
        step=step,
        size=size,
        style={"width": width},
        )  

def notification(title, msg='', _type='info'):
    return dmc.Notification(
        id=f"simple_notify_{np.random.randint(0, 100)}",
        styles={'scroll-behavior':'auto'},
        title=title,
        action="show",
        autoClose=False,
        message=dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=dmc.Text(f'{msg}', style={'maxHeight':'100px', 'white-space':'pre-line'}, size='xs'),
                ),
        color=cfg.NOTIFICATION[_type]['color'],
        icon=DashIconify(icon=cfg.NOTIFICATION[_type]['icon'], width=20),
        )