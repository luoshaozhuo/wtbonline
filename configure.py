import pandas as pd

import wtbonline._plot as plt
from wtbonline._db.rsdb_interface import RSDBInterface

HEADER_HEIGHT = '40px'

TOOLBAR_SIZE = '205px'
TOOLBAR_PADDING = '10px'
TOOLBAR_TOGGLE_SIZE = 'sm'
TOOLBAR_TOGGLE_ICON_WIDTH = 20
TOOLBAR_TOGGLE_POS_TOP = 70
TOOLBAR_TOGGLE_POS_RIGHT = 20
TOOLBAR_COMPONENT_SIZE = 'xs'
TOOLBAR_ICON_WIDTH = 20
TOOLBAR_COMPONENT_WIDTH = '170px'
TOOLBAR_FONT_SIZE = 'sm'

NOW = pd.Timestamp.now()
DATE = NOW.date()
TIME_START = '2024-02-19T00:00:00'
TIME_END = '2024-02-19T23:59:00'

GRAPH_PADDING_TOP = '30px'
GRAPH_CONF = pd.DataFrame(
    [
        ['性能', '功率曲线', plt.PowerCurve],
        ['性能', '功率差异', plt.PowerCompare],
        ['故障', '齿轮箱关键参数超限', plt.Gearbox],
        ['故障', '发电机关键参数超限', plt.GeneratorOverloaded],
        ['故障', '变流器关键参数超限', plt.Convertor],
        ['故障', '风轮方位角异常', plt.HubAzimuth],
        ['故障', '叶片桨距角不同步', plt.BladeAsynchronous],
        ['故障', '叶根摆振弯矩超限', plt.BladeOverloaded],
        ['故障', '叶根挥舞弯矩超限', plt.BladeOverloaded],
        ['故障', '叶根载荷不平衡', plt.BladeUnblacedLoad],
        ['故障', '叶片pitchkick', plt.BladePitchkick],
        ['安全', '叶片净空', None],
        ['安全', '塔顶振动', None],
        ['通用质量特性', '可靠性', None],
        ['通用质量特性', '可维修性', None],
        ['通用质量特性', '保障性', None]
        ],
    columns=['item', 'clause', 'class']
    )

NOTIFICATION_TITLE_DBQUERY_FAIL = '数据库操作失败'
NOTIFICATION_TITLE_DBQUERY_NODATA = '查无数据'
NOTIFICATION_TITLE_GRAPH_FAIL = '绘图失败'
NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL = '后台任务提交失败'
NOTIFICATION_TITLE_SCHEDULER_JOB_SUCCESS = '后台任务提交成功'

WINDFARM_CONFIGURATION =  RSDBInterface.read_windfarm_configuration()
WINDFARM_INFORMATION =  RSDBInterface.read_windfarm_infomation()
WINDFARM_FAULT_TYPE = RSDBInterface.read_turbine_fault_type()

NOTIFICATION = {
    'error':{'color':'red', 'icon':'mdi:close-circle-outline"e'},
    'info':{'color':'indigo', 'icon':'mdi:information-variant-circle-outline'},
    'success':{'color':'green', 'icon':'mdi:success-circle-outline'},
    'warning':{'color':'yellow', 'icon':'mdi:error-outline'},
    }

SCHEDULER_JOB_TYPE = ['定时任务', '一次性任务']
SCHEDULER_JOB_FUNC = { 
    "初始化数据库":"wtbonline._process.preprocess.init_tsdb:init_tdengine",
    "拉取原始数据":"wtbonline._process.preprocess.load_tsdb:update_tsdb",
    "拉取PLC数据":"wtbonline._process.preprocess.load_ibox_files:update_ibox_files",
    "统计10分钟样本":"wtbonline._process.statistics.sample:update_statistic_sample",
    "统计24小时样本":"wtbonline._process.statistics.daily:udpate_statistic_daily",
    "检测故障":"wtbonline._process.statistics.fault:udpate_statistic_fault",
    "训练离群值识别模型":"wtbonline._process.model.anormlay.train:train_all",
    "离群值识别":"wtbonline._process.model.anormlay.predict:predict_all",
    "数据统计报告":"wtbonline._report.brief_report:build_brief_report_all",
    "清理缓存":"wtbonline._pages.tools.utils:clear_cache"
    }
MISFIRE_GRACE_TIME = 600 # 600s
SCHEDULER_JOB_INTER_UNIT = ['weeks', 'days', 'hours', 'miniues', 'seconds']
SCHEDULER_URL='http://scheduler:40000/scheduler/jobs'
SCHEDULER_TIMEOUT = 10