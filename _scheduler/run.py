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
    JobExecutionEvent, EVENT_JOB_MISSED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_REMOVED, EVENT_SCHEDULER_PAUSED, 
    EVENT_SCHEDULER_RESUMED, EVENT_JOB_SUBMITTED,
    )

from wtbonline._db.rsdb.dao import create_engine_
from wtbonline._logging import get_logger
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._common.code import MYSQL_QUERY_FAILED

#%% config
class Config():
    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(engine=create_engine_(), engine_options={'pool_pre_ping':True})}
    SCHEDULER_EXECUTORS = {"default": {"type": "processpool", "max_workers": 3}}
    SCHEDULER_JOB_DEFAULTS = {"coalesce": True, "max_instances": 1}
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

logger = get_logger('apscheduler')
scheduler = APScheduler(BackgroundScheduler(timezone='Asia/Shanghai'))

JOB_STATUS = {
    EVENT_SCHEDULER_PAUSED:'PAUSED',
    EVENT_SCHEDULER_RESUMED:'START',
    EVENT_JOB_REMOVED:'REMOVED',
    EVENT_JOB_SUBMITTED:'SUBMIITED',
    EVENT_JOB_MISSED:'MISSED', 
    EVENT_JOB_ERROR:'ERROR', 
    EVENT_JOB_EXECUTED:'EXECUTED',
    }

MASK = 0
for i in JOB_STATUS:
    MASK |= i

import time

RECORD = {}

def listen(event):
    status = JOB_STATUS[event.code]
    job_id = event.job_id
    try:
        last = RECORD.get(job_id, None)
        now = time.time()
        if last is not None and (now - last[1])<1 and last[0]=='MISSED':
            return
        RECORD.update({job_id:[status, now]})
        RSDBInterface.update('timed_task', {'status':status, 'update_time':pd.Timestamp.now()}, eq_clause={'task_id':job_id})
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

# #%% main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000)
