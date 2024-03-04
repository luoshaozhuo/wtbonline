import pandas as pd
import dash_mantine_components as dmc

import wtbonline._plot as plt
from wtbonline._db.rsdb_interface import RSDBInterface

THEME_PRIMARY_COLOR = 'indigo'
THEME_PRIMARY_SHADE = {'light': 5, 'dark':7}

HEADER_HEIGHT = '40px'
HEADER_PADDING_TOP = '8px'
HEADER_ICON_WIDTH = 20
HEADER_ICON_HORIZONTAL_SPACE = '5px'
HEADER_SWITCH_ICON_WIDTH = 10
HEADER_SWITCH_SIZE = 'xs'
HEADER_FONTSIZE = 'sm'
HEADER_BAGE_SIZE = 'lg'
HEADER_LABEL = '风电数据助理'
HEADER_LABEL_ABBREATION =  'WDAS'
HEADER_MENU_FONTSIZE = '10px'
HEADER_MENU_ICON_WIDTH = 15
WINDFARM_NAME = RSDBInterface.read_windfarm_infomation(limit=1).squeeze()['farm_name']

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
TOOLBAR_HIDE_SMALLER_THAN =  'lg'
TOOLBAR_TABLE_COLUMNS = ['图例号', 'map_id', 'start_time', 'end_time', 'set_id']
TOOLBAR_TABLE_FONT_SIZE = '10px'
TOOLBAR_TABLE_HEIGHT = '200PX'
TOOLBAR_ICON_COLOR = dmc.theme.DEFAULT_COLORS['indigo'][4]

CONTAINER_SIZE = 'lg'

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
NOTIFICATION_TITLE_SCHEDULER_JOB_FAIL = '后台操作失败'
NOTIFICATION_TITLE_SCHEDULER_JOB_SUCCESS = '后台操作成功'

WINDFARM_CONFIGURATION =  RSDBInterface.read_windfarm_configuration()
WINDFARM_INFORMATION =  RSDBInterface.read_windfarm_infomation()
WINDFARM_FAULT_TYPE = RSDBInterface.read_turbine_fault_type()

NOTIFICATION = {
    'error':{'color':'red', 'icon':'mdi:close-circle-outline'},
    'info':{'color':'indigo', 'icon':'mdi:information-variant-circle-outline'},
    'success':{'color':'green', 'icon':'mdi:success-circle-outline'},
    'warning':{'color':'yellow', 'icon':'mdi:error-outline'},
    }

SCHEDULER_JOB_TYPE ={
    '定时任务':'interval',
    '一次性任务':'date',
    }
SCHEDULER_JOB_PARAMETER = pd.DataFrame( 
    [
        ['初始化数据库', 'wtbonline._process.preprocess.init_tsdb:init_tdengine', False, False, False, False],
        ['拉取原始数据', 'wtbonline._process.preprocess.load_tsdb:update_tsdb', False, False, False, False],
        ['拉取PLC数据', 'wtbonline._process.preprocess.load_ibox_files:update_ibox_files', False, False, False, False],
        ['统计10分钟样本', 'wtbonline._process.statistics.sample:update_statistic_sample', False, False, False, False],
        ['统计24小时样本', 'wtbonline._process.statistics.daily:udpate_statistic_daily', False, False, False, False],
        ['检测故障', 'wtbonline._process.statistics.fault:udpate_statistic_fault', False, False, False, False],
        ['训练离群值识别模型', 'wtbonline._process.model.anormlay.train:train_all', True, True, True, False],
        ['离群值识别', 'wtbonline._process.model.anormlay.predict:predict_all',  True, True, False, True],
        ['数据统计报告', 'wtbonline._report.brief_report:build_brief_report_all',  True, True, False, False],
        ],
    columns=['name', 'func', 'end_date', 'delta', 'minimun_sample', 'num_output']
    )
MISFIRE_GRACE_TIME = 600 # 600s
SCHEDULER_JOB_INTER_UNIT = ['weeks', 'days', 'hours', 'miniues', 'seconds']
SCHEDULER_URL='http://scheduler:40000/scheduler/jobs'
SCHEDULER_TIMEOUT = 10

SIMPLE_PLOT_TYPE = ['时序图', '散点图', '极坐标图', '频谱图']
SIMPLE_PLOT_SAMPLE_NUM = 5000

ANOMALY_MATRIX_PLOT_COLOR = {
    '非离群':'gray',
    '正常':'#2ca02c',
    '异常':'red',
    '离群，未标注':'blue',
    }