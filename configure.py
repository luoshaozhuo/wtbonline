import pandas as pd

import wtbonline._plot as plt

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
    columns=['section', 'item', 'class']
    ).set_index('item')

NOTIFICATION_TITLE_DBQUERY = '数据库操作失败'
NOTIFICATION_TITLE_GRAPH = '绘图失败'
