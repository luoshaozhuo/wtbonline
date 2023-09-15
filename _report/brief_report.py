# -*- coding: utf-8 -*-
"""
Created on Thu May 11 06:01:43 2023

@author: luosz

自动生成工作快报
"""
#%% import
from pathlib import Path
import pandas as pd
import numpy as np
from platform import platform
from xlwings.utils import hex_to_rgb
from typing import List, Optional, Union, Mapping
from datetime import date
import itertools
from tempfile import TemporaryDirectory

from reportlab.lib import utils, colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (BaseDocTemplate, Paragraph, PageBreak, Image,
                                Frame, PageTemplate, Spacer, Table, TableStyle)
from reportlab.platypus.doctemplate import _doNothing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import plotly.express as px 
import plotly.graph_objects as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
plt.rcParams['font.family']='sans-serif'        
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

from wtbonline._db.config import get_td_local_connector
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._pages.tools.plot import line_plot 
from wtbonline._db.common import make_sure_dataframe
from wtbonline._db.common import make_sure_list, make_sure_datetime
from wtbonline._process.modelling import data_filter, scater_matrix_anormaly
from wtbonline._logging import get_logger, log_it

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

TEMP_DIR = RSDBInterface.read_app_configuration(key_='tempdir')['value'].squeeze()
TEMP_DIR = Path(TEMP_DIR)
TEMP_DIR.mkdir(exist_ok=True)

_LOGGER = get_logger('brief_report')

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

def build_graph(fig, title, fiename, width=1000, height=None, temp_dir=TEMP_DIR):
    fig.layout.update({'title': title})
    fig.layout.margin.update({'l':10, 't':50 ,'r':10, 'b':20})
    fig.layout.update({'width':1000})
    if height is not None:
        fig.layout.update({'height':1000})
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
    ''' 按需增加turbine_id、测点名称、设备编号 '''
    df = df.copy()
    if 'var_name' in df.columns and ('测点名称' not in df.columns) :
        point_df = RSDBInterface.read_turbine_model_point(set_id=set_id)
        dct = {row['var_name']:row['point_name'] for _,row in point_df.iterrows()}
        df.insert(0, '测点名称', df['var_name'].replace(dct))
    if 'device' in df.columns and  ('turbine_id' not in df.columns):
        df.insert(0, 'turbine_id', df['device'])    
    if 'turbine_id' in df.columns and ('map_id' not in df.columns):
        conf_df = RSDBInterface.read_windfarm_configuration(set_id=set_id)
        dct = {row['turbine_id']:row['map_id'] for _,row in conf_df.iterrows()}
        df.insert(0, 'map_id', df['turbine_id'].replace(dct))  
    return df 

def _stat(set_id, start_time, end_time, cols, funcs, groupby='device', turbine_id=None, interval=None, sliding=None):
    cols = make_sure_list(cols)
    funcs = make_sure_list(funcs)
    func_dct = {i:funcs for i in cols}
    assert len(func_dct)>0
    df, point_df = TDFC.read(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        func_dct=func_dct,
        groupby=groupby,
        interval=interval,
        sliding=sliding
        )
    return _standard(set_id, df), point_df

def _build_table(df, bound_df, title, temp_dir):
    ''' 超限表格 '''
    bound_df = bound_df.sort_values('var_name')
    cols = bound_df['var_name']
    stat_df = pd.DataFrame({
        '测点名称':bound_df['name'].tolist(),
        '最小值':df[[f'{i}_min' for i in cols]].min().tolist(),
        '最大值':df[[f'{i}_max' for i in cols]].max().tolist(),
        '下限':bound_df['lower_bound'].tolist(),
        '上限':bound_df['upper_bound'].tolist(),
        })
    for col in stat_df.select_dtypes('float').columns:
        stat_df[col] = stat_df[col].apply(lambda x:round(x, 2))
    fig_tbl = ff.create_table(stat_df, height_constant=50)
    return build_graph(fig_tbl, title, f'{title}.jpg', temp_dir)

def _exceed(raw_df, bound_df):
    rev = []
    cols = ['var_name', 'name', 'lower_bound','upper_bound']
    for i, (var_name,name,lob,upb) in bound_df[cols].iterrows():
        col_upb = f'{var_name}_max'
        col_lo = f'{var_name}_min'
        sub = raw_df[(raw_df[col_upb]>upb) | (raw_df[col_lo]<lob)]
        for _,row in sub.iterrows():
            rev.append([
                var_name, name, lob, upb, row['map_id'], row['device'], row[col_lo], row[col_upb]
                ])
    rev = pd.DataFrame(rev, columns=cols+['map_id', 'device', 'min', 'max'])
    return rev

def _conclude(exceed_df):
    if len(exceed_df)==0:
        conclution = '无超限'
    else:
        conclution = ''
        for key_, grp in exceed_df.groupby('name'):
            conclution += f"{key_}超限：{','.join(grp['map_id'])}\n<br />"
    return conclution

def _sample(
        set_id:str,
        exceed_df:pd.DataFrame, 
        func:str, 
        start_time:Union[str, date], 
        end_time:Union[str, date]
        )->list:
    exceed_df = make_sure_dataframe(exceed_df)
    if len(exceed_df)<1:
        return {}
    exceed_df = _standard(set_id, exceed_df)
    func = make_sure_list(func)
    start_time = make_sure_datetime(start_time)
    end_time = make_sure_datetime(end_time)

    rev = {}
    for _, grp in exceed_df.groupby('var_name'):
        tid, var_name, id_ = grp.iloc[0][['device', 'var_name', 'map_id']]
        temp, _ =  TDFC.read(
            set_id=set_id,
            turbine_id=tid,
            start_time=start_time,
            end_time=end_time,
            func_dct={var_name:func},
            )
        var_name = (pd.Series(var_name)
            .str.extractall('(var_\d+)')
            .iloc[:, 0]
            .drop_duplicates()
            .tolist())
        ts = pd.to_datetime(temp['ts'].iloc[0])
        df, point_df = TDFC.read(
            set_id=set_id,
            turbine_id=tid,
            start_time=ts-pd.Timedelta('15m'),
            end_time=ts+pd.Timedelta('15m'),
            var_name=var_name
            )
        df.rename(
            columns={r['var_name']:r['point_name'] for _,r in point_df.iterrows()}, 
            inplace=True
            )
        point_df.set_index('var_name', inplace=True)
        fig_ts = line_plot(
            df, 
            point_df.loc[var_name, 'point_name'], 
            point_df.loc[var_name, 'unit'],
            height=450,
            )
        title=id_ + '_'.join(point_df.loc[var_name, 'point_name'])
        rev.update({title:fig_ts})
    return rev


def _read_power_curve(set_id:str, turbine_id:List[str], min_date:Union[str, date], max_date:Union[str, date]):
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=min_date,
        end_time=max_date,
        columns = ['turbine_id', 'var_355_mean', 'var_246_mean', 'totalfaultbool_mode',
                   'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique',
                   'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean']
        )
    # 正常发电数据
    df = df[
        (df['totalfaultbool_mode']=='False') &
        (df['totalfaultbool_nunique']==1) &
        (df['ongrid_mode']=='True') & 
        (df['ongrid_nunique']==1) & 
        (df['limitpowbool_mode']=='False') &
        (df['limitpowbool_nunique']==1)
        ]
    df.rename(columns={'var_355_mean':'mean_wind_speed', 
                       'var_246_mean':'mean_power'}, 
                       inplace=True)
    # 15°空气密度
    df['mean_wind_speed'] = df['mean_wind_speed']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
    return df


# report function
def chapter_1(set_id:str, 
              start_time:Union[str, date], 
              end_time:Union[str, date],
              min_date,
              max_date,
              n:int,
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
    farm_df = RSDBInterface.read_windfarm_configuration(set_id=set_id)
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
    sql = f'''
        select first(totalenergy) as min, last(totalenergy) as max, device
        from {get_td_local_connector()['database']}.s_{set_id} 
        where ts>='{min_date}' and ts<'{max_date}' 
        group by device 
        order by device
        '''
    df = TDFC.query(sql)
    df['发电量（kWh）'] = df['max'] - df['min']
    df = _standard(set_id, df)

    cols = ['map_id', '发电量（kWh）']
    fig = ff.create_table(df[cols], height_constant=50)
    fig.add_traces([go.Bar(x=df['map_id'], 
                           y=df['发电量（kWh）'].astype(int), 
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
    fig.layout.xaxis2.update({'title': 'map_id'})
    fig.layout.update({'title': f'{min_date}至{max_date}累积发电量'})
    
    rev = []
    rev.append(Paragraph('2 发电情况', PS_HEADING_1))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(build_graph(fig, f'{min_date}至{max_date}累积发电量', '2_energy.jpg', temp_dir))
    return rev

def chapter_3_1(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_1(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-1')
    conf_df =  RSDBInterface.read_windfarm_configuration(set_id=set_id)
    graphs = {}
    for model_name, grp in conf_df.groupby('model_name'):
        turbine_id = grp['turbine_id'].tolist()
        df = _read_power_curve(set_id, turbine_id, min_date, max_date)
        temp = RSDBInterface.read_windfarm_configuration(set_id=set_id)
        df['turbine_id'] = df['turbine_id'].replace({
            row['turbine_id']:row['map_id'] for _,row in temp.iterrows()
            })
        df = df.sort_values(by=['turbine_id'])

        wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        power_curve = df.groupby(['wspd', 'turbine_id'])['mean_power'].median().reset_index()
        mean_df = power_curve.groupby('wspd')['mean_power'].median().reset_index()
        upper_df = power_curve.groupby('wspd')['mean_power'].max().reset_index()
        lower_df = power_curve.groupby('wspd')['mean_power'].min().reset_index()

        ref_df = RSDBInterface.read_windfarm_power_curve(model_name=model_name)
        ref_df.rename(columns={'mean_speed':'wspd'}, inplace=True)

        fig_ts = go.Figure()
        color = px.colors.qualitative.Plotly[0] 
        fig_ts.add_trace(
            go.Scatter(
                x=ref_df['wspd'],
                y=ref_df['mean_power'],
                line=dict(color=color),
                mode='lines+markers',
                name='参考功率曲线'
                )
            )
        color = px.colors.qualitative.Plotly[1]
        fill_color = f'rgba{hex_to_rgb(color)+(0.3,)}'
        line_color = f'rgba{hex_to_rgb(color)+(0,)}' 
        fig_ts.add_trace(
            go.Scatter(
                x=mean_df['wspd'],
                y=mean_df['mean_power'],
                line=dict(color=color),
                mode='lines+markers',
                name='实际功率曲线（中位值及上、下限）'
                )
            )   
        fig_ts.add_trace(
            go.Scatter(
                x=upper_df['wspd'],
                y=upper_df['mean_power'],
                line=dict(color=line_color),
                opacity=0.3,
                mode='lines',
                showlegend=False
                )
            )
        fig_ts.add_trace(
            go.Scatter(
                x=lower_df['wspd'],
                y=lower_df['mean_power'],
                mode='lines',
                fill='tonexty',
                fillcolor=fill_color,
                line=dict(color=line_color),
                showlegend=False
                )
            )
        fig_ts.layout.xaxis.update({'title': '风速 m/s'})
        fig_ts.layout.yaxis.update({'title': '功率 kW'})
        fig_ts.update_layout(
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1)
            )
        graphs.update({f'机型：{model_name}':fig_ts})

    tids = power_curve['turbine_id'].unique()
    df = pd.DataFrame({'机组编号': tids,'k值':np.random.random(tids.shape[0])})
    df = df.round(3).sort_values('k值')
    fig_tbl = ff.create_table(df, height_constant=50)
        
    rev = []
    rev.append(Paragraph('3.1 功率曲线', PS_HEADING_2))
    rev.append(build_graph(fig_tbl, '功率曲线k值排名', '3_1_power_curve_k.jpg', temp_dir))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_2(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_2(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-2')
    cols = ['var_171', 'var_172', 'var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, 'max', min_date, max_date)

    rev = []
    rev.append(Paragraph('3.2 齿轮箱', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '齿轮箱关键参数', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_3(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_3(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-3')
    cols = ['var_171', 'var_172', 'abs(var_171-var_172)']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, 'max', min_date, max_date)

    rev = []
    rev.append(Paragraph('3.3 主轴承', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))  
    rev.append(_build_table(raw_df, bound_df, '主轴承关键参数', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_4(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_4(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-4')
    cols = ['var_206', 'var_207', 'var_208', 'var_209', 'var_210', 'var_211']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, 'max', min_date, max_date)

    rev = []
    rev.append(Paragraph('3.4 发电机', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '发电机关键参数', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_5(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_5(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-5')
    cols = ['var_15004', 'var_15005', 'var_15006', 'var_12016']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, 'max', min_date, max_date)

    rev = []
    rev.append(Paragraph('3.5 变流器', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '变流器关键参数', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_6(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_6(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-6')
    cols = ['var_246', 
            'var_104', 'var_105', 'var_106', 
            'abs(var_104-var_105)', 'abs(var_104-var_106)', 'abs(var_105-var_106)',
            ]
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, 'max', min_date, max_date)

    rev = []
    rev.append(Paragraph('3.6 叶片同步', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '叶片关键参数', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def chapter_3_7(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_7(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-7')
    funcs = ['min', 'max']
    # 单独
    org_cols = ['var_18000', 'var_18001', 'var_18002', 'var_18003', 'var_18004', 'var_18005']
    bound_single = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=org_cols)
    raw_single, _ = _stat(set_id, min_date, max_date, org_cols, funcs)
    exceed_single = _exceed(raw_single, bound_single)
    graphs = _sample(set_id, exceed_single, 'max', min_date, max_date)
    # 绝对差
    columns = []
    agg = []
    primary = []
    cols = ['abs(avg(var_18000)-avg(var_18001))', 'abs(avg(var_18000)-avg(var_18002))', 'abs(avg(var_18001)-avg(var_18002))',
            'abs(avg(var_18003)-avg(var_18004))', 'abs(avg(var_18003)-avg(var_18005))', 'abs(avg(var_18004)-avg(var_18005))']
    for i, col in enumerate(cols):
        name = f'diff_{i}'
        primary.append(col + f' as `{name}`')
        agg += [f'{func}(diff_{i})' for func in funcs]
        columns += [f'{col}_{func}' for func in funcs]
    ## 统计值
    tids = RSDBInterface.read_windfarm_configuration(set_id=set_id)['turbine_id']
    raw_df = []
    for turbine_id in tids:
        sql = f'''select {','.join(agg)} from '''
        sql += f'''(select {','.join(primary)} from windfarm.d_{turbine_id} interval(1m) sliding(1m))'''
        temp = TDFC.query(sql)
        temp.columns = columns
        temp['device'] = turbine_id
        raw_df.append(temp)
    raw_df = pd.concat(raw_df, ignore_index=True)
    raw_df = _standard(set_id, raw_df)
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    exceed_diff = _exceed(raw_df, bound_df)
    exceed_df = pd.concat([exceed_single, exceed_diff], ignore_index=True)
    conclution = _conclude(exceed_df)

    # 例图
    if exceed_diff.shape[0]>0:
        # 获取发生时间
        sr = exceed_diff.iloc[0]
        turbine_id = sr['device']
        func = 'min' if sr['min']<sr['lower_bound'] else 'max'
        sql = f'''select tt, {func}(a) from '''
        sql += f'''(select {sr['var_name']} as a, first(ts) as tt from windfarm.d_{turbine_id} interval(1m) sliding(1m))'''
        temp = TDFC.query(sql)
        ts = pd.to_datetime(temp['tt'].iloc[0])
        # 查询原始数据
        org_df, point_df = TDFC.read(
            set_id=set_id,
            turbine_id=turbine_id,
            start_time=ts-pd.Timedelta('30m'),
            end_time=ts+pd.Timedelta('30m'),
            var_name=org_cols+['var_246']
            )
        org_df.set_index('ts', inplace=True, drop=False)
        for i in org_cols:
            org_df.insert(0, f'{i}_ma', org_df[i].rolling('360s').mean())
        # 绘图
        from plotly.subplots import make_subplots
        fig = make_subplots(3, 1, shared_xaxes=True)
        args = [
            ['var_18000', '1#叶片', 1, '摆振弯矩', 'red', None, 0.3, True],
            ['var_18001', '2#叶片', 1, '摆振弯矩', 'green', None, 0.3, True],
            ['var_18002', '3#叶片', 1, '摆振弯矩', 'blue', None, 0.3, True],
            ['var_18000_ma', '1#叶片移动均值', 1, '摆振弯矩','red', 'dot', 1, True],
            ['var_18001_ma', '2#叶片移动均值', 1, '摆振弯矩','green', 'dot', 1, True],
            ['var_18002_ma', '3#叶片移动均值', 1, '摆振弯矩','blue', 'dot', 1, True],
            ['var_18003', '1#叶片', 2, '挥舞弯矩','red', None, 0.3, False],
            ['var_18004', '2#叶片', 2, '挥舞弯矩','green', None, 0.3, False],
            ['var_18005', '3#叶片', 2, '挥舞弯矩','blue', None, 0.3, False],
            ['var_18003_ma', '1#叶片移动均值', 2, '挥舞弯矩','red', 'dot', 1, False],
            ['var_18004_ma', '2#叶片移动均值', 2, '挥舞弯矩','green', 'dot', 1, False],
            ['var_18005_ma', '3#叶片移动均值', 2, '挥舞弯矩','blue', 'dot', 1, False],
            ['var_246', '电网有功功率', 3, '有功功率', 'black', None, 1, True],
            ]
        for col,name,row,title,color,dash,opacity,show in args:
            fig.add_trace(
                    go.Scatter(
                        x=org_df['ts'],
                        y=org_df[col],
                        mode='lines',
                        line=dict(color=color, dash=dash),
                        opacity=opacity,
                        name=name,
                        showlegend=show
                        ),
                    row=row,
                    col=1,
                    )
            fig.update_yaxes(title_text=title, row=row, col=1)
        fig.update_xaxes(title='时间', row=3, col=1)
        fig.update_layout(
            title=turbine_id,
            legend=dict(
                font=dict(size=10),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
                )
            )
        graphs.update({sr['map_id']:fig})

    rev = []
    rev.append(Paragraph('3.7 叶根载荷', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_single, bound_single, '叶根载荷关键参数-单独', temp_dir))
    rev.append(_build_table(raw_df, bound_df, '叶根载荷关键参数-组合', temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'3_7_{key_}.jpg', temp_dir))
    return rev


def chapter_3_8(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date='2023-10-01'
    >>> _ = chapter_3_7(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 3-8')
    cols = ['var_18000', 'var_18003']
    funcs = ['min', 'max']
    vars = [f'{f}({v}) as {v}_{f}' for v, f in itertools.product(cols, funcs)]
    sql = f'''
        select device, {', '.join(vars)} from s_{set_id} 
        where 
        ongrid=1 and ts>='{min_date}' and ts<'{max_date}'
        group by device
        '''
    raw_df = _standard(set_id, TDFC.query(sql))
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    exceed_df = exceed_df[exceed_df['var_name'].str.match('var_.*')]

    sub_df = raw_df.sort_values('var_18000_max').tail(3).copy()
    sub_df = _standard(set_id, sub_df)
    graphs = []
    for _, row in sub_df.iterrows():
        sql = f'''
            select ts, device, max(var_18000) as var_18000_max 
            from s_{set_id}
            where 
            ongrid=1 and device='{row['device']}' and ts>='{min_date}' and ts<'{max_date}'
            '''
        ts = TDFC.query(sql).squeeze()['ts']
        plot_df, point_df = TDFC.read(
            set_id=set_id, 
            turbine_id=row['device'],
            var_name=['var_18000', 'var_18006'],
            start_time=ts - pd.Timedelta('1h'),
            end_time=ts + pd.Timedelta('1h')
            )
        point_df.set_index('var_name', inplace=True)
        # 散点图
        fig_scatter = go.Figure()
        fig_scatter.add_trace(
            go.Scatter(x=plot_df['var_18006'], y=plot_df['var_18000'], mode='markers',
                    marker=dict(size=3,opacity=0.2))
            )
        fig_scatter.layout.xaxis.update({'title': point_df.loc['var_18006', 'column']})
        fig_scatter.layout.yaxis.update({'title': point_df.loc['var_18000', 'column']})
        fig_scatter.update_layout(
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1)
            )
        # 极坐标图
        plot_df.sort_values('ts', inplace=True)
        fig_polar = go.Figure()
        fig_polar.add_trace(
            go.Scatterpolar(theta=plot_df['var_18006'], 
                            r=plot_df['var_18000']-plot_df['var_18000'].mean(), 
                            mode='markers',
                            marker=dict(size=3, opacity=0.5)
                            )
            )
        fig_polar.layout.xaxis.update({'title': point_df.loc['var_18006', 'column']})
        fig_polar.layout.yaxis.update({'title': point_df.loc['var_18000', 'column']})
        fig_polar.update_layout(
            legend=dict(
                orientation="h",
                font=dict(
                        size=10,
                        color="black"
                    ),
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1)
            )
        graphs.append((row['map_id']+"_"+point_df.loc['var_18000', 'column'], fig_scatter, fig_polar))
    
    rev = []
    rev.append(Paragraph('3.8 1#叶根摆振弯矩', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '1#叶根摆振弯矩', temp_dir))
    for i, s_plot, p_plot in graphs:
        rev.append(build_graph(s_plot, i, f'{i}_scatter.jpg', temp_dir))
        rev.append(build_graph(p_plot, i, f'{i}_polar.jpg', temp_dir))
    return rev

# def chapter_3_9(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
#     rev = []
#     rev.append(Paragraph('3.8 Pitchkick', PS_HEADING_2))
#     df = pd.DataFrame([['s10010', '2023-01-01 00:05:10', '2500', '2023-01-01 00:04:10'],
#                         ['s10010', '2023-01-02 00:05:10', '2500', '2023-01-02 00:04:10'],
#                         ['s10010', '2023-01-03 00:05:10', '2500', '2023-01-03 00:04:10'],
#                         ['s10010', '2023-01-04 00:05:10', '2500', '2023-01-04 00:04:10'],
#                         ],
#                       columns = ['机组号', '触发时间', '功率最大值 kW', '发生时间',])
#     fig_tbl = ff.create_table(df, height_constant=50)

#     cols = ['1#叶片实际角度','2#叶片实际角度', '3#叶片实际角度','电网有功功率']
#     df, desc_df = tools.read_scada('s10015', '2023-02-01 17:00:00', cols)
#     fig_line = line_plot(df, cols, desc_df['unit'], layout=[1,1,1,2])
    
#     rev = []
#     rev.append(Paragraph('3.9 Pitchkick', PS_HEADING_2))
#     rev.append(Paragraph('s10010触发PichKick', PS_BODY))
#     rev.append(Spacer(FRAME_WIDTH_LATER, 10))
#     rev.append(build_graph(fig_tbl, 'Pitchkick触发记录', 'pitchkick_tbl.jpg', temp_dir))
#     rev.append(Spacer(FRAME_WIDTH_LATER, 10))
#     rev.append(build_graph(fig_line, 'Pitchkick触发样例', 'pitchkick_ts.jpg', temp_dir))
#     return rev


def chapter_3(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    _LOGGER.info('chapter 3')
    return [
        Paragraph('3 运行一致性', PS_HEADING_1),
        *chapter_3_1(set_id, min_date, max_date, temp_dir),
        *chapter_3_2(set_id, min_date, max_date, temp_dir),
        *chapter_3_3(set_id, min_date, max_date, temp_dir),
        *chapter_3_4(set_id, min_date, max_date, temp_dir),
        *chapter_3_5(set_id, min_date, max_date, temp_dir),
        *chapter_3_6(set_id, min_date, max_date, temp_dir),
        *chapter_3_7(set_id, min_date, max_date, temp_dir),
        *chapter_3_8(set_id, min_date, max_date, temp_dir),
        ]

def chapter_4(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date=None
    >>> _ = chapter_4(set_id, min_date, max_date)
    '''
    _LOGGER.info('chapter 4')
    anormaly_df = RSDBInterface.read_model_anormaly(
        set_id=set_id, start_time=min_date, end_time=max_date
        ).drop_duplicates('sample_id')
    if len(anormaly_df)<1:
        rev = []
        rev.append(Paragraph('4 离群数据', PS_HEADING_2))
        rev.append(Paragraph('无离群值识别记录', PS_BODY))
        return rev
    
    label_df = RSDBInterface.read_model_label(set_id=set_id).drop_duplicates('sample_id')
    total = anormaly_df.shape[0]
    left = total - label_df.shape[0]

    model_uuid = anormaly_df.sort_values('create_time').tail(1)
    model_uuid = model_uuid.squeeze()['model_uuid']
    uuid_lst = make_sure_list(model_uuid.split(','))
    model_df = RSDBInterface.read_model(uuid=uuid_lst)
    all_df = RSDBInterface.read_statistics_sample(
        set_id=model_df['set_id'].iloc[0],
        turbine_id=model_df['turbine_id'].iloc[0],
        start_time=model_df['start_time'].iloc[0],
        end_time=model_df['end_time'].iloc[0],
        ).set_index('id')
    anormaly_df = RSDBInterface.read_model_anormaly(
        set_id=model_df['set_id'].iloc[0],
        model_uuid=model_uuid,
        turbine_id=model_df['turbine_id'].iloc[0],
        start_time=model_df['start_time'].iloc[0],
        end_time=model_df['end_time'].iloc[0],
        )
    all_df = data_filter(all_df)
    all_df['is_anormaly'] = False
    all_df.loc[anormaly_df['sample_id'], 'is_anormaly'] = True
    a = all_df[all_df['is_anormaly']==False]
    a = a if len(a)<4001 else a.sample(4000)
    b = all_df[all_df['is_anormaly']==True]
    sub_df = all_df.loc[a.index.tolist() + b.index.tolist()]
    fig = scater_matrix_anormaly(sub_df)

    model_df = _standard(set_id, model_df)
    map_id = model_df['map_id'].iloc[0]

    rev = []
    rev.append(Paragraph('4 离群数据', PS_HEADING_1))
    rev.append(Paragraph(f'本期报告时段内共有离群数据：{total}条, 待鉴别{left}条', PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(build_graph(fig, f'{map_id}离群值散点矩阵', '4_anormaly.jpg', height=1000, temp_dir=temp_dir))
    return rev



def appendix(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    '''
    >>> set_id='20835'
    >>> min_date='2023-01-01'
    >>> max_date=None
    >>> _ = appendix(set_id, min_date, max_date)
    '''
    _LOGGER.info('appendix')
    conf_df =  RSDBInterface.read_windfarm_configuration(set_id=set_id)
    df = _read_power_curve(set_id, None, min_date, max_date)
    wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26)-0.5)
    df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
    power_curve = df.groupby(['wspd', 'turbine_id'])['mean_power'].median().reset_index()
    power_curve = _standard(set_id, power_curve)
    graphs = {}
    for map_id, grp in power_curve.groupby('map_id'):
        model_name = conf_df[conf_df['map_id']==map_id]['model_name'].iloc[0]
        ref_df = RSDBInterface.read_windfarm_power_curve(model_name=model_name)
        ref_df.rename(columns={'mean_speed':'wspd'}, inplace=True)
        graphs.update({
            f'{map_id}':line_plot(
                df=grp, 
                ycols='mean_power', 
                units='kW', 
                xcol='wspd', 
                xtitle='风速 m/s',
                refx = ref_df['wspd'],
                refy = ref_df['mean_power'],
                height = 200
                )
            })          
    rev = []
    rev.append(Paragraph('附录 A', PS_HEADING_1))
    rev.append(Paragraph('A.1 功率曲线', PS_HEADING_2))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir))
    return rev

def build_brief_report(
        *, 
        pathname:str, 
        set_id:str, 
        start_time:Union[str, date], 
        end_time:Union[str, date]
        ):
    df, _ = TDFC.read(
        set_id=set_id, turbine_id=None, start_time=start_time, end_time=end_time, 
        func_dct={'ts':['first', 'last']}, groupby='device', remote=False)
    min_date = df['ts_first'].min()
    max_date = df['ts_last'].max()
    n = df.shape[0]

    doc = BRDocTemplate(pathname)
    add_page_templates(doc)
    with TemporaryDirectory(dir=TEMP_DIR.as_posix()) as temp_dir:
        _LOGGER.info(f'temp directory:{temp_dir}')
        doc.build([
            *chapter_1(set_id, start_time, end_time, min_date, max_date, n),
            *chapter_2(set_id, min_date, max_date, temp_dir),
            *chapter_3(set_id, min_date, max_date, temp_dir),
            *chapter_4(set_id, min_date, max_date, temp_dir),
            PageBreak(),
            *appendix(set_id, min_date, max_date, temp_dir),
            ])

# main
@log_it(_LOGGER, True)
def build_brief_report_all(**kwargs):
    '''
    end_time : 截至时间
    delta : 单位天
    >>> build_brief_report_all(end_time='', delta=180)
    '''
    assert pd.Series(['end_time', 'delta']).isin(kwargs).all()
    if kwargs['end_time'] is not None and kwargs['end_time']!='':
        end_time = pd.to_datetime(kwargs['end_time'])
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    
    path = RSDBInterface.read_app_configuration(key_='report_outpath')['value'].squeeze()
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    conf_df = RSDBInterface.read_windfarm_configuration()
    for set_id in conf_df['set_id'].unique():
        filename = f"brief_report_{set_id}_{end_time}_{kwargs['delta']}d.pdf"
        pathname = path/filename
        build_brief_report(
            pathname=pathname.as_posix(), 
            set_id=set_id, 
            start_time=start_time,
            end_time=end_time
            ) 


#%% main
if __name__ == "__main__":
    # import doctest
    # doctest.testmod()#
    pass
