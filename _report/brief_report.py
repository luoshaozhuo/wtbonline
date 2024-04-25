# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """
#%% import
from pathlib import Path
from telnetlib import PRAGMA_HEARTBEAT
import pandas as pd
import numpy as np
from platform import platform
from typing import List, Union
from datetime import date
from tempfile import TemporaryDirectory
import plotly.express as px

from reportlab.lib import utils, colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (BaseDocTemplate, Paragraph, PageBreak, Image,
                                Frame, PageTemplate, Spacer)
from reportlab.platypus.doctemplate import _doNothing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import plotly.express as px
from zmq import device

plt.rcParams['font.family']='sans-serif'        
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._common.utils import make_sure_dataframe, make_sure_list, make_sure_datetime
from wtbonline._logging import get_logger
from wtbonline._plot import graph_factory
import wtbonline._plot as plt
from wtbonline._process.tools.filter import normal_production

#%% constant
pdfmetrics.registerFont(TTFont('Simsun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('Simfang', 'simfang.ttf'))
pdfmetrics.registerFont(TTFont('Simhei', 'simhei.ttf'))

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_TOP = 2.54*cm
MARGIN_BOTTOM = MARGIN_TOP
MARGIN_LEFT = 3.18*cm
MARGIN_RIGHT = MARGIN_LEFT
FRAME_WIDTH_FIRST = PAGE_WIDTH-MARGIN_LEFT-MARGIN_RIGHT
FRAME_HEIGHT_FIRST = 19.2*cm
FRAME_WIDTH_LATER = FRAME_WIDTH_FIRST
FRAME_HEIGHT_LATER = PAGE_HEIGHT-MARGIN_TOP-MARGIN_BOTTOM

TITLE = '重点工作快报'
DEPARTMENT = '研究院'

PS_HEADING_1 = ParagraphStyle('heading_1', 
                                fontSize=18, 
                                fontName='Simhei',
                                leading=36,
                                spaceBefore=18)
PS_HEADING_2 = ParagraphStyle('heading_2', 
                                fontSize=12, 
                                fontName='Simhei',
                                leading=24,
                            spaceBefore=12)
PS_BODY = ParagraphStyle('body', 
                          fontSize=10, 
                          fontName='Simsun',
                          leading=16)
PS_TITLE = ParagraphStyle('table', 
                          fontSize=8, 
                          fontName='Simhei',
                          spaceBefore=8,
                          spaceAfter=8,
                          leading=8)
PS_TABLE = ParagraphStyle('table', 
                          fontSize=6, 
                          fontName='Simhei',
                          leading=6)

PLOT_ENGINE = 'orca' if platform().startswith('Windows') else 'kaleido'

TEMP_DIR = Path(RSDBFacade.read_app_configuration(key_='tempdir')['value'].squeeze())
TEMP_DIR.mkdir(exist_ok=True)

REPORT_OUT_DIR = Path(RSDBFacade.read_app_configuration(key_='report_outpath')['value'].squeeze())
REPORT_OUT_DIR.mkdir(parents=True, exist_ok=True)

_LOGGER = get_logger('brief_report')

DBNAME = RSDBFacade.read_app_server(name='tdengine', remote=1)['database'].iloc[0]


POINT_DF = PGFacade.read_model_point()
DEVICE_DF = PGFacade.read_model_device()
FAULT_TYPE_DF = RSDBFacade.read_turbine_fault_type()

#%% class
class BRDocTemplate(BaseDocTemplate):
    def handle_pageBegin(self):
        self._handle_pageBegin()
        
    def build(self,flowables,onFirstPage=_doNothing, onLaterPages=_doNothing, canvasmaker=canvas.Canvas):
        BaseDocTemplate.build(self,flowables, canvasmaker=canvasmaker)

class FirtPageTemplate(PageTemplate):
    def beforeDrawPage(self,canv,doc):
        dt = f'{pd.Timestamp.now().date()}'
        draw_header(canv, TITLE, dt, DEPARTMENT)
        darw_footer(canv)

class LaterPageTemplate(PageTemplate):
    def beforeDrawPage(self,canv,doc):
        darw_footer(canv)

# helper function
def draw_header(canv, title:str, dt:Union[str, date], department:str):
    style = ParagraphStyle('title')
    style.fontName = 'Simfang'
    style.fontSize = 48
    style.alignment = TA_CENTER
    style.textColor = colors.red
    p = Paragraph(title, style)
    p.wrapOn(canv, FRAME_WIDTH_LATER, FRAME_HEIGHT_LATER)
    p.drawOn(canv, MARGIN_LEFT, PAGE_HEIGHT-MARGIN_TOP-12)

    style = ParagraphStyle('title', fontName='Simfang', fontSize=15)
    p = Paragraph(f'{dt}', style)
    p.wrapOn(canv, FRAME_WIDTH_LATER, FRAME_HEIGHT_LATER)
    p.drawOn(canv, MARGIN_LEFT, FRAME_HEIGHT_FIRST+MARGIN_BOTTOM+10)
    
    style = ParagraphStyle('title', fontName='Simfang', fontSize=15)
    style.alignment =TA_RIGHT
    p = Paragraph(department, style)
    p.wrapOn(canv, FRAME_WIDTH_LATER, FRAME_HEIGHT_LATER)
    p.drawOn(canv, MARGIN_LEFT, FRAME_HEIGHT_FIRST+MARGIN_BOTTOM+10)   
    
    canv.saveState()
    canv.setStrokeColorRGB(1, 0, 0)
    canv.setLineWidth(2)
    y = FRAME_HEIGHT_FIRST+MARGIN_BOTTOM
    canv.line(MARGIN_LEFT, y, PAGE_WIDTH-MARGIN_RIGHT, y)
    canv.restoreState()

def darw_footer(canv):    
    canv.saveState()
    canv.setStrokeColorRGB(1, 0, 0)
    canv.setLineWidth(2)
    canv.line(MARGIN_LEFT, MARGIN_BOTTOM, PAGE_WIDTH-MARGIN_RIGHT, MARGIN_BOTTOM)
    canv.restoreState()
    
def add_page_templates(doc):
    lst = []
    lst.append(
        FirtPageTemplate(id='first',
                         autoNextPageTemplate='later',
                         frames=Frame(MARGIN_LEFT, 
                                      MARGIN_BOTTOM, 
                                      FRAME_WIDTH_FIRST, 
                                      FRAME_HEIGHT_FIRST, 
                                      0, 0, 0, 0, id='normal'),
                         pagesize=A4)
        )
    lst.append(
        LaterPageTemplate(id='later',
                          autoNextPageTemplate='later',
                          frames=Frame(MARGIN_LEFT, 
                                       MARGIN_BOTTOM, 
                                       FRAME_WIDTH_LATER, 
                                       FRAME_HEIGHT_LATER, 
                                       0, 0, 0, 0, id='normal'),
                          pagesize=A4)
               )
    doc.addPageTemplates(lst)

def build_graph(fig, title, fiename, *, width=1000, height=None, temp_dir=TEMP_DIR):
    fig.layout.update({'title': title})
    fig.layout.margin.update({'l':10, 't':50 ,'r':10, 'b':20})
    fig.layout.update({'width':1000})
    if height is not None:
        fig.layout.update({'height':height})
    pathname = Path(temp_dir)/fiename
    if pathname.exists():
        pathname.unlink()
    fig.write_image(pathname, engine=PLOT_ENGINE, scale=2)
    img = utils.ImageReader(pathname)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
    return Image(pathname, 
                 width=FRAME_WIDTH_LATER,
                 height=(FRAME_WIDTH_LATER * aspect))


def _standard(set_id, df):
    ''' 按需增加device_id、测点名称、设备编号 '''
    rev = df.copy()
    if 'device_id' in rev.columns and ('device_name' not in rev.columns):
        rev = pd.merge(rev, DEVICE_DF[['device_name', 'device_id']], how='left')  
    return rev

# report function
def chapter_1(set_id:str, 
              start_time:Union[str, date], 
              end_time:Union[str, date],
              min_date,
              max_date,
              ):
    '''
    >>> set_id = '20835'
    >>> start_time = '2023-01-01 00:00:00'
    >>> end_time = '2023-10-01 00:00:00'
    >>> df, _ = TDFC.read(
    ...     set_id=set_id, turbine_id=None, start_time=start_time, end_time=end_time, 
    ...     func_dct={'ts':['first', 'last']}, groupby='device', remote=True
    ...     )
    >>> min_date = df['ts_first'].min().date()
    >>> max_date = df['ts_last'].max().date()
    >>> n = df.shape[0]
    >>> _ = chapter_1(set_id, start_time, end_time, min_date, max_date, n)
    '''
    _LOGGER.info('chapter 1')
    farm_df = PGFacade.read_model_device(set_id=set_id)
    n = len(TDFC.get_deviceID(set_id=set_id, remote=True))
    text = f'''机组型号：{set_id}<br/>
               机组总数：{farm_df.shape[0]} 台<br/>
               可统计机组：{n} 台<br/>
               统计开始时间：{start_time}<br/>
               统计结束时间：{end_time}<br/>
               可统计开始时间：{min_date}<br/>
               可统计结束时间：{max_date}<br/>
            '''
    rev = []
    rev.append(Spacer(FRAME_WIDTH_LATER, 1))
    rev.append(Paragraph('1 概况', PS_HEADING_1))
    rev.append(Paragraph(text, PS_BODY))
    return rev

def chapter_2(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01 00:00:00'
    >>> max_date='2023-10-01 00:00:00'
    >>> _ = chapter_2(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 2')
    df = TDFC.read(
        set_id=set_id, 
        device_id=None, 
        start_time=min_date, 
        end_time=max_date,
        groupby='device', 
        columns={'totalenergy':['first', 'last']},
        remote=True)

    df['发电量（kWh）'] = df['totalenergy_last'] - df['totalenergy_first']
    df = df.sort_values('发电量（kWh）', ascending=False)
    df = _standard(set_id, df)

    cols = ['device_name', '发电量（kWh）']
    graphs = {}
    for i in range(int(np.ceil(df.shape[0]/10))):
        sub_df = df.iloc[i*10:(i+1)*10, :]
        fig = ff.create_table(sub_df[cols], height_constant=50)
        fig.add_traces([go.Bar(x=sub_df['device_name'], 
                            y=sub_df['发电量（kWh）'].astype(int), 
                            xaxis='x2',
                            yaxis='y2',
                            marker_color='#0099ff')
                        ])
        fig['layout']['xaxis2'] = {}
        fig['layout']['yaxis2'] = {}
        fig.layout.yaxis2.update({'anchor': 'x2'})
        fig.layout.xaxis2.update({'anchor': 'y2'})
        fig.layout.xaxis.update({'domain': [0, .3]})
        fig.layout.xaxis2.update({'domain': [0.4, 1.]})
        fig.layout.yaxis2.update({'title': '发电量 kWh'})
        fig.layout.xaxis2.update({'title': 'device_name'})
        fig.layout.update({'title': f'{min_date}至{max_date}累积发电量'})
        graphs.update({f'排名{i*10+1}至{i*10+10}':fig})

    rev = []
    rev.append(Paragraph('2 发电情况', PS_HEADING_1))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir=temp_dir))
    return rev

def _conclude(record_df):
    n = len(record_df['device_id'].unique())
    conclution = '无发生此类故障。' if len(record_df)<1 else f'{n}台机组发生此类故障。'
    return conclution

def _build_tables(record_df, temp_dir, title):
    df = record_df.groupby(['device_name', 'fault_id']).agg({'device_id':[len], 'start_time':['max']})
    df = df.reset_index().droplevel(level=1, axis=1).rename(columns={'fault_id':'id'})
    df = pd.merge(df, FAULT_TYPE_DF[['id', 'cause']], how='left').drop('id', axis=1)
    df = df.sort_values(['device_name', 'cause'], ascending=True).reset_index(drop=True).reset_index()
    df = df[['index', 'device_name', 'cause', 'device_id', 'start_time']]
    df.columns = ['序号', '设备名', '故障原因', '发生次数', '最近一次发生时间']
    rev = []
    count = 30
    for i in range(int(np.ceil(df.shape[0]/count))):
        sub_df = df.iloc[i*count:(i+1)*count, :]
        fig_tbl = ff.create_table(sub_df.iloc[0:], height_constant=50)
        sub_title = f'{title}_{i+1}'
        rev.append(build_graph(fig_tbl, sub_title, f'{sub_title}.jpg', temp_dir=temp_dir))
    return rev

def _plot_ts(ftype_df, record_df):
    ftype_sr = ftype_df.iloc[0,:]
    graphs = []
    for _,row in record_df.head(1).iterrows():
        var_names = ftype_sr['var_names']
        delta = pd.Timedelta(f"{max(int(ftype_sr['time_span']), 1)}m")
        obj = graph_factory.get(ftype_sr['graph'])()
        obj.init(var_names=var_names)
        fig = obj.plot(
            set_id=row['set_id'], 
            device_ids=row['device_id'], 
            start_time=row['start_time']-delta, 
            end_time=row['end_time']+delta
            )
        graphs.append([row['device_name'], fig])
    return graphs

def _plot_stat(ftype_df, record_df):
    cols = ['device_id', 'fault_id', 'device_name', 'start_time']
    df = pd.merge(record_df[cols], ftype_df[['id', 'cause']].rename(columns={'id':'fault_id'}), how='left')
    if len(df)<1:
        return []
    df['date'] = df['start_time'].dt.date
    
    graphs = []
    plot_df = df.groupby(['date', 'cause']).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
    fig = px.bar(plot_df, x="date", y="count", color="cause", width=900, height=500)
    graphs.append(['故障发生趋势', fig])
    
    plot_df = df.groupby(['cause', 'device_name']).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
    fig = px.sunburst(
        plot_df, path=['cause', 'device_name'], values='count',
        color='count', 
        color_continuous_scale='RdBu',
        color_continuous_midpoint=plot_df['count'].mean()
        )
    graphs.append(['故障占比', fig])
    return graphs

def _build_section(ftype_df:pd.DataFrame, **params):
    _LOGGER.info(f"chapter {params['chapter']} section {params['section']} {ftype_df['name'].iloc[0]}")
    # 按发生时间排序是为了下面展示时选出最近一条记录
    record_df = RSDBFacade.read_statistics_fault(
        fault_id=ftype_df['id'],
        start_time=params['min_date'],
        end_time=params['max_date']
        ).sort_values(['start_time'], ascending=False)
    record_df = _standard(params['set_id'], record_df)
    
    func = _plot_ts if len(ftype_df)<2 else _plot_stat
    graphs = func(ftype_df, record_df)
        
    rev = []
    rev.append(Paragraph(f"{params['chapter']}.{params['section']} {ftype_df['name'].iloc[0]}", PS_HEADING_2))
    rev.append(Paragraph(_conclude(record_df), PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    code = f"{params['chapter']}.{params['section']}"
    if len(record_df)>0:
        rev += _build_tables(record_df, temp_dir=params['temp_dir'], title=f'表 {code}.{1} 故障发生次数统计结果')
    i = 0
    for name, figure in graphs:
        i = i+1
        title = f"图 {code}.{i} {name}"
        rev.append(build_graph(figure, title, title+'.jpg', temp_dir=params['temp_dir']))
    return rev

def chapter_3(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    _LOGGER.info('chapter 3')
    params = dict(set_id=set_id, min_date=min_date, max_date=max_date, temp_dir=temp_dir, chapter=3)
    rev = [Paragraph('3 运行一致性', PS_HEADING_1)]
    i=0
    for _, grp in FAULT_TYPE_DF.groupby('name'):
        i+=1
        params.update({'section':i}) 
        rev += _build_section(grp, **params)
    return rev

def chapter_4(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date=None
    >>> _ = chapter_4(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 4')
    anormaly_df = RSDBFacade.read_model_anormaly(
        set_id=set_id, start_time=min_date, end_time=max_date
        ).drop_duplicates('sample_id')
    if len(anormaly_df)<1:
        rev = []
        rev.append(Paragraph('4 离群数据', PS_HEADING_2))
        rev.append(Paragraph('指定时间范围内无离群值识别记录', PS_BODY))
        return rev
    
    label_df = RSDBFacade.read_model_label(set_id=set_id).drop_duplicates('sample_id')
    total = anormaly_df.shape[0]
    left = total - label_df.shape[0]

    # 取最后一个样本点
    device_id= anormaly_df.sort_values('create_time').tail(1).squeeze()[['device_id']].iloc[0]
    device_name = DEVICE_DF[DEVICE_DF['device_id']==device_id]['device_name'].iloc[0]
    fig = graph_factory.get('Anomaly')().plot(
        set_id=set_id,
        device_ids=device_id,
        start_time=min_date,
        end_time=max_date,
        )

    rev = []
    rev.append(Paragraph('4 离群数据', PS_HEADING_1))
    rev.append(Paragraph(f'本期报告时段内共有离群数据：{total}条, 待鉴别{left}条。下图展示其中一台机组的离群样本分布。', PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(build_graph(fig, f'{device_name}离群值散点矩阵', '4_anormaly.jpg', height=1000, temp_dir=temp_dir))
    return rev


# def appendix(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
#     '''
#     >>> set_id='20835'
#     >>> min_date='2023-01-01'
#     >>> max_date=None
#     >>> _ = appendix(set_id, min_date, max_date)
#     '''
#     _LOGGER.info('appendix')
#     conf_df =  RSDBInterface.read_windfarm_configuration(set_id=set_id)
#     df = _read_power_curve(set_id, None, min_date, max_date)
#     wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
#     df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
#     power_curve = df.groupby(['wspd', 'turbine_id'])['mean_power'].median().reset_index()
#     power_curve = _standard(set_id, power_curve)
#     graphs = {}
#     for map_id, grp in power_curve.groupby('map_id'):
#         model_name = conf_df[conf_df['map_id']==map_id]['model_name'].iloc[0]
#         ref_df = RSDBInterface.read_windfarm_power_curve(model_name=model_name)
#         ref_df.rename(columns={'mean_speed':'wspd'}, inplace=True)
#         graphs.update({
#             f'{map_id}':line_plot(
#                 df=grp, 
#                 ycols='mean_power', 
#                 units='kW', 
#                 xcol='wspd', 
#                 xtitle='风速 m/s',
#                 refx = ref_df['wspd'],
#                 refy = ref_df['mean_power'],
#                 height = 200
#                 )
#             })          
#     rev = []
#     rev.append(Paragraph('附录 A', PS_HEADING_1))
#     rev.append(Paragraph('A.1 功率曲线', PS_HEADING_2))
#     for key_ in graphs:
#         rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir=temp_dir))
#     return rev

def build_brief_report(
        *, 
        pathname:str, 
        set_id:str, 
        start_time:Union[str, date], 
        end_time:Union[str, date]
        ):
    df = TDFC.read(
        set_id=set_id, 
        device_id=None, 
        start_time=start_time,
        end_time=end_time, 
        columns={'ts':['first', 'last']}, 
        remote=True)
    if len(df)<1:
        raise ValueError(f'无法出具报告，规定时段没有数据：{start_time}至{end_time}')
    sr = df.squeeze()
    min_date = sr['ts_first']
    max_date = sr['ts_last']
    start_time = pd.to_datetime(start_time).date()
    end_time = pd.to_datetime(end_time).date()

    doc = BRDocTemplate(pathname)
    add_page_templates(doc)
    with TemporaryDirectory(dir=TEMP_DIR.as_posix()) as temp_dir:
        _LOGGER.info(f'temp directory:{temp_dir}')
        doc.build([
            *chapter_1(set_id, start_time, end_time, min_date, max_date),
            *chapter_2(set_id, start_time, end_time, temp_dir),
            *chapter_3(set_id, start_time, end_time, temp_dir),
            *chapter_4(set_id, min_date, max_date, temp_dir),
            PageBreak(),
            ])

# main
def build_brief_report_all(*args, **kwargs):
    '''
    end_time : 截至时间
    delta : 单位天
    >>> build_brief_report_all(end_time='', delta=180)
    '''
    delta = kwargs.get('delta', 30)
    end_time = kwargs.get('end_time', None)
    if end_time not in (None, ''):
        end_time = pd.to_datetime(kwargs['end_time']).date()
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{delta}d")
    df = PGFacade.read_model_device()
    for set_id in df['set_id'].unique():
        filename = f"brief_report_{set_id}_{end_time}_{delta}d.pdf"
        pathname = REPORT_OUT_DIR/filename
        build_brief_report(
            pathname=pathname.as_posix(), 
            set_id=set_id, 
            start_time=start_time,
            end_time=end_time
            ) 

#%% main
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    build_brief_report_all(delta=120)