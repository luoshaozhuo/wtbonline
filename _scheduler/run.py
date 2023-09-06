# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:46:05 2023

@author: luosz

任务调度
curl -X GET  localhost:40000/scheduler/jobs
curl -X DELETE localhost:40000/scheduler/jobs/heart_beat
curl -X PATCH localhost:40000/scheduler/jobs/update_tsdb -d '{"next_run_time":"2023-08-15 07:58:00"}'
curl -X POST localhost:40000/scheduler/jobs/heart_beat/pause
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"heart_beat","func":"wtbonline._process.preprocess:heart_beat","trigger":"date", "start_date":"2023-09-06 17:25:00", "kwargs":{"task_id":1}}'
curl -X POST localhost:40000/scheduler/jobs/heart_beat/resume
curl -X DELETE localhost:40000/scheduler/jobs/heart_beat
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"update_tsdb","func":"wtbonline._process.preprocess:update_tsdb","next_run_time":"2023-08-15 03:16:00"}'
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"update_statistic_sample","func":"wtbonline._process.statistic:update_statistic_sample","next_run_time":"2023-08-15 02:53:00"}'
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"train_all","func":"wtbonline._process.modelling:train_all", "kwargs":{"start_time":"2023-05-01 00:00:00", "end_time":"2023-08-15 00:00:00","minimum":3000}, "next_run_time":"2023-08-15 14:43:00"}'
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"predict_all","func":"wtbonline._process.modelling:predict_all", "kwargs":{"start_time":"2023-05-01 00:00:00", "end_time":"2023-08-15 00:00:00","size":20}, "next_run_time":"2023-08-15 14:43:00"}'
curl -X POST localhost:40000/scheduler/jobs -d '{"id":"build_brief_report","func":"wtbonline._report.brief_report:main", "kwargs":{"end_time":"2023-08-01 00:00:00", "delta":60}, "next_run_time":"2023-08-16 08:51:00"}'
"""

#%% import
from flask import Flask
from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import json
from flask import request

from wtbonline._db.rsdb.dao import create_engine_
from wtbonline._logging import get_logger

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
