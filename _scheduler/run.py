# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:46:05 2023

@author: luosz
"""

#%% import
from flask import Flask
from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import json
from flask import request
import pandas as pd
from apscheduler.events import (
    EVENT_SCHEDULER_STARTED ,  EVENT_SCHEDULER_SHUTDOWN ,  EVENT_SCHEDULER_PAUSED , 
    EVENT_SCHEDULER_RESUMED ,  EVENT_EXECUTOR_ADDED ,  EVENT_EXECUTOR_REMOVED , 
    EVENT_JOBSTORE_ADDED ,  EVENT_JOBSTORE_REMOVED ,  EVENT_ALL_JOBS_REMOVED , 
    EVENT_JOB_ADDED ,  EVENT_JOB_REMOVED ,  EVENT_JOB_MODIFIED ,  EVENT_JOB_EXECUTED , 
    EVENT_JOB_ERROR ,  EVENT_JOB_MISSED ,  EVENT_JOB_SUBMITTED ,  EVENT_JOB_MAX_INSTANCES)

from wtbonline._db.rsdb.dao import create_engine_
from wtbonline._logging import get_logger
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._common.code import MYSQL_QUERY_FAILED
# 这里不导入，发布任务时会提示找不到相关函数
from wtbonline._report.brief_report import build_brief_report_all

#%% config
class Config():
    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(engine=create_engine_(), engine_options={'pool_pre_ping':True})}
    SCHEDULER_EXECUTORS = {"default": {"type": "processpool", "max_workers": 5}}
    SCHEDULER_JOB_DEFAULTS = {"coalesce": True, "max_instances": 1}
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'

app = Flask(__name__)
app.config.from_object(Config())

logger = get_logger('apscheduler')
scheduler = APScheduler(BackgroundScheduler(timezone='Asia/Shanghai'))

JOB_STATUS = {
    # EVENT_SCHEDULER_START与EVENT_SCHEDULER_STARTED一致
    EVENT_SCHEDULER_STARTED : 'SCHEDULER_STARTED',
    EVENT_SCHEDULER_SHUTDOWN : 'SCHEDULER_SHUTDOWN',
    EVENT_SCHEDULER_PAUSED : 'SCHEDULER_PAUSED',
    EVENT_SCHEDULER_RESUMED : 'SCHEDULER_RESUMED',
    EVENT_EXECUTOR_ADDED : 'EXECUTOR_ADDED',
    EVENT_EXECUTOR_REMOVED : 'EXECUTOR_REMOVED',
    EVENT_JOBSTORE_ADDED : 'JOBSTORE_ADDED',
    EVENT_JOBSTORE_REMOVED : 'JOBSTORE_REMOVED',
    EVENT_ALL_JOBS_REMOVED : 'ALL_JOBS_REMOVED',
    EVENT_JOB_ADDED : 'JOB_ADDED',
    EVENT_JOB_REMOVED : 'JOB_REMOVED',
    EVENT_JOB_MODIFIED : 'JOB_MODIFIED',    # 没有stop的事件，修改与停止共用modified
    EVENT_JOB_EXECUTED : 'JOB_EXECUTED',
    EVENT_JOB_ERROR : 'JOB_ERROR',
    EVENT_JOB_MISSED : 'JOB_MISSED',
    EVENT_JOB_SUBMITTED : 'JOB_SUBMITTED',
    EVENT_JOB_MAX_INSTANCES : 'JOB_MAX_INSTANCES',
    }

SELECTED_EVENT = (
    EVENT_SCHEDULER_RESUMED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_MISSED, 
    EVENT_JOB_ERROR, 
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ADDED,
    # 从源代码看，pause_job最后发送的是MODIFEIED，而不是PAUSED，后者是调用pause函数触发的，含义是停止scheduler
    EVENT_JOB_MODIFIED
    )

FINISH_EVENT = [EVENT_JOB_MISSED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR]
FINISH_STATUS = [JOB_STATUS[i] for i in FINISH_EVENT]

MASK = 0
for i in JOB_STATUS:
    MASK |= i

def listen(event):
    status = JOB_STATUS[event.code]
    job_id = getattr(event, 'job_id', 'NA')
    logger.info(f'event job_id={job_id} event={status}')
    if job_id == 'NA':
        return
    try:
        now = pd.Timestamp.now()
        record = {'task_id':job_id, 'status':status, 'update_time':now}
        RSDBFacade.insert(record, 'timed_task_log')
        if status in FINISH_STATUS:
            RSDBFacade.update('timed_task', {'status':status, 'update_time':now}, eq_clause={'task_id':job_id})
    except Exception as e:
        logger.error(f'{MYSQL_QUERY_FAILED} job_id={job_id} status={status}, msg={e}')

scheduler.add_listener(listen, MASK)
scheduler.init_app(app)
scheduler.start()

@app.after_request
def log_each_request(response):
    try:
       #收到的前端数据
        request_data = json.loads(request.get_data())
    except Exception as e:
        request_data = {}
    logger.info(f'{request.remote_addr} {request.method} {request.url} {request_data} {response.status}')
    return response

#%% main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000)
