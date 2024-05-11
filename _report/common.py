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

from wtbonline.configure import WINDFARM_CONF

plt.rcParams['font.family']='sans-serif'        
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._common.utils import make_sure_dataframe, make_sure_list, make_sure_datetime, send_email
from wtbonline._logging import get_logger
from wtbonline._plot import graph_factory
import wtbonline._plot as plt
from wtbonline._process.tools.filter import normal_production
from wtbonline._common.utils import send_email

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

PS_HEADINGS = [PS_HEADING_1, PS_HEADING_2]

PS_BODY = ParagraphStyle('body', 
                          fontSize=10, 
                          fontName='Simsun',
                          leading=16)
PS_TITLE = ParagraphStyle('table', 
                          fontSize=8, 
                          fontName='Simhei',
                          spaceBefore=8,
                          spaceAfter=8,
                          leading=18)
PS_TABLE = ParagraphStyle('table', 
                          fontSize=6, 
                          fontName='Simhei',
                          leading=6)

PLOT_ENGINE = 'orca' if platform().startswith('Windows') else 'kaleido'

TEMP_DIR = Path(RSDBFacade.read_app_configuration(key_='tempdir')['value'].squeeze())
TEMP_DIR.mkdir(exist_ok=True)

REPORT_OUT_DIR = Path(RSDBFacade.read_app_configuration(key_='report_outpath')['value'].squeeze())
REPORT_OUT_DIR.mkdir(parents=True, exist_ok=True)

LOGGER = get_logger('brief_report')

DBNAME = RSDBFacade.read_app_server(name='tdengine', remote=1)['database'].iloc[0]


POINT_DF = PGFacade.read_model_point()
DEVICE_DF = PGFacade.read_model_device().set_index('device_id', drop=False)
DEVICE_DF.index.name = ''
FAULT_TYPE_DF = RSDBFacade.read_turbine_fault_type()
FARMCONF_DF = RSDBFacade.read_windfarm_configuration().set_index('set_id', drop=False)
FARMCONF_DF.index.name = ''
FARM_NAME = PGFacade.read_model_factory()['factory_name'].iloc[0]

TITLE = f'{FARM_NAME}<br />风电机组运行报告'
DEPARTMENT = '研究院'

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
    style = ParagraphStyle('a')
    style.fontName = 'Simfang'
    style.fontSize = 38
    style.alignment = TA_CENTER
    style.textColor = colors.red
    style.leading = 48
    p = Paragraph(title, style)
    p.wrapOn(canv, FRAME_WIDTH_LATER, FRAME_HEIGHT_LATER)
    p.drawOn(canv, MARGIN_LEFT, PAGE_HEIGHT-MARGIN_TOP-60)

    style = ParagraphStyle('b', fontName='Simfang', fontSize=15)
    p = Paragraph(f'{dt}', style)
    p.wrapOn(canv, FRAME_WIDTH_LATER, FRAME_HEIGHT_LATER)
    p.drawOn(canv, MARGIN_LEFT, FRAME_HEIGHT_FIRST+MARGIN_BOTTOM+10)
    
    style = ParagraphStyle('c', fontName='Simfang', fontSize=15)
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


def standard(set_id, df):
    ''' 按需增加device_id、测点名称、设备编号 '''
    rev = df.copy()
    if 'device_id' in rev.columns and ('device_name' not in rev.columns):
        rev = pd.merge(rev, DEVICE_DF[['device_name', 'device_id']], how='left')  
    return rev

def build_tables(df, temp_dir, title):
    df = df.reset_index()
    df['index'] = df['index']+1
    rev = []
    count = 30
    for i in range(int(np.ceil(df.shape[0]/count))):
        sub_df = df.iloc[i*count:(i+1)*count, :]
        fig_tbl = ff.create_table(sub_df.iloc[0:], height_constant=50)
        sub_title = f'{title}_{i+1}'
        rev.append(build_graph(fig_tbl, sub_title, f'{sub_title}.jpg', temp_dir=temp_dir))
    return rev

def plot_stat(df, groupby_ts=['date', 'cause'], grouby_sb=['cause', 'device_name']):
    df = make_sure_dataframe(df)
    if len(df)<1:
        return []
    df['date'] = df['start_time'].dt.date
    
    graphs = []
    plot_df = df.groupby(groupby_ts).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
    fig = px.bar(plot_df, x=groupby_ts[0], y='count', color=groupby_ts[1], width=900, height=500)
    graphs.append(fig)
    
    plot_df = df.groupby(grouby_sb).agg({'device_id':len}).reset_index().rename(columns={'device_id':'count'})
    fig = px.sunburst(
        plot_df, path=grouby_sb, values='count',
        color='count', 
        color_continuous_scale='RdBu',
        color_continuous_midpoint=plot_df['count'].mean()
        )
    graphs.append(fig)
    return graphs

def plot_sample_ts(df):
    df = make_sure_dataframe(df)
    if len(df)<1:
        return []
    graphs = []
    for _,row in df.iterrows():
        var_names = row['var_names'].split(',')
        delta = pd.Timedelta(f"{max(int(row['time_span']), 1)}m")
        obj = graph_factory.get(row['graph'])()
        obj.init(var_names=var_names)
        fig = obj.plot(
            set_id=row['set_id'], 
            device_ids=row['device_id'], 
            start_time=row['start_time']-delta, 
            end_time=row['end_time']+delta
            )
        graphs.append(fig)
    return graphs

def mail_report(pathname):
    farm = PGFacade.read_model_factory()['factory_name'].iloc[0]
    recv = RSDBFacade.read_app_configuration(key_='email_address')['value'].iloc[0]
    account = RSDBFacade.read_app_configuration(key_='email_account')['value'].iloc[0]
    user_name, password, host, port = account.split('_')
    if recv not in [None, '']:
        send_email(recv, f'{farm} 数据分析报告{Path(pathname).name}', '请查阅附件。本邮件自动发送。', 
                    user_name, password, host, port, pathname=pathname)


# def build_tables(record_df, temp_dir, title):
#     df = record_df.groupby(['device_name', 'fault_id']).agg({'device_id':[len], 'start_time':['max']})
#     df = df.reset_index().droplevel(level=1, axis=1).rename(columns={'fault_id':'id'})
#     df = pd.merge(df, FAULT_TYPE_DF[['id', 'cause']], how='left').drop('id', axis=1)
#     df = df.sort_values(['device_name', 'cause'], ascending=True).reset_index(drop=True).reset_index()
#     df = df[['index', 'device_name', 'cause', 'device_id', 'start_time']]
#     df.columns = ['序号', '设备名', '故障原因', '发生次数', '最近一次发生时间']
#     rev = []
#     count = 30
#     for i in range(int(np.ceil(df.shape[0]/count))):
#         sub_df = df.iloc[i*count:(i+1)*count, :]
#         fig_tbl = ff.create_table(sub_df.iloc[0:], height_constant=50)
#         sub_title = f'{title}_{i+1}'
#         rev.append(build_graph(fig_tbl, sub_title, f'{sub_title}.jpg', temp_dir=temp_dir))
#     return rev