# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """
#%% import
from pathlib import Path
import pandas as pd
import numpy as np
from platform import platform
from typing import List, Union
from datetime import date
import itertools
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

plt.rcParams['font.family']='sans-serif'        
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

from wtbonline._db.rsdb.dao import RSDB
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._common.utils import make_sure_dataframe, make_sure_list, make_sure_datetime
from wtbonline._logging import get_logger, log_it
from wtbonline._plot import graph_factory
import wtbonline._plot as plt
from wtbonline._process.tools.filter import filter_for_modeling
from wtbonline._process.model.anormlay.predict import load_model

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
    # if 'var_name' in df.columns and ('测点名称' not in df.columns) :
    #     point_df = POINT_DF[POINT_DF['set_id']==set_id]
    #     dct = {row['var_name']:row['point_name'] for _,row in point_df.iterrows()}
    #     df.insert(0, '测点名称', df['var_name'].replace(dct))
    # if 'device' in df.columns and  ('device_id' not in df.columns):
    #     df.insert(0, 'device_id', df['device'])    
    # if 'device_id' in df.columns and ('map_id' not in df.columns):
    #     conf_df = DEVICE_DF[DEVICE_DF['set_id']==set_id]
    #     dct = {row['device_id']:row['map_id'] for _,row in conf_df.iterrows()}
    #     df.insert(0, 'map_id', df['device_id'].replace(dct))
    if 'device_id' in rev.columns and ('device_name' not in rev.columns):
        rev = pd.merge(rev, DEVICE_DF[['device_name', 'device_id']], how='left')  
    return rev

# def _stat(set_id, start_time, end_time, cols, funcs, groupby='device', turbine_id=None, interval=None, sliding=None):
#     cols = make_sure_list(cols)
#     funcs = make_sure_list(funcs)
#     func_dct = {i:funcs for i in cols}
#     assert len(func_dct)>0
#     where = 'and workmode=32 '
#     df, point_df = TDFC.read(
#         set_id=set_id,
#         turbine_id=turbine_id,
#         start_time=start_time,
#         end_time=end_time,
#         where=where,
#         func_dct=func_dct,
#         groupby=groupby,
#         interval=interval,
#         sliding=sliding
#         )
#     return _standard(set_id, df), point_df

# def _build_table(df, bound_df, title, temp_dir):
#     ''' 超限表格 '''
#     bound_df = bound_df.sort_values('var_name')
#     cols = bound_df['var_name']
#     stat_df = pd.DataFrame({
#         '测点名称':bound_df['name'].tolist(),
#         '最小值':df[[f'{i}_min' for i in cols]].min().tolist(),
#         '最大值':df[[f'{i}_max' for i in cols]].max().tolist(),
#         '下限':bound_df['lower_bound'].tolist(),
#         '上限':bound_df['upper_bound'].tolist(),
#         })
#     for col in stat_df.select_dtypes('float').columns:
#         stat_df[col] = stat_df[col].apply(lambda x:round(x, 2))
#     fig_tbl = ff.create_table(stat_df, height_constant=50)
#     return build_graph(fig_tbl, title, f'{title}.jpg', temp_dir=temp_dir)

# def _exceed(raw_df, bound_df, set_id=None):
#     value_vars_max = raw_df.filter(axis=1, regex='.*_max$').columns.tolist()
#     value_vars_min = raw_df.filter(axis=1, regex='.*_min$').columns.tolist()
#     value_vars = value_vars_max + value_vars_min
#     id_vars = raw_df.columns[~raw_df.columns.isin(value_vars)]
#     raw_melt = raw_df.melt(id_vars, value_vars)
    
#     bound_df = bound_df.rename(columns={'lower_bound':'_min', 'upper_bound':'_max'})
#     value_vars = bound_df.filter(axis=1, regex='.*_(max|min)$').columns
#     id_vars = bound_df.columns[~bound_df.columns.isin(value_vars)]
#     bound_melt = bound_df.melt(id_vars, value_vars, value_name='bound')
#     bound_melt['variable'] = bound_melt['var_name']+bound_melt['variable']
    
#     rev = pd.merge(raw_melt, bound_melt[['variable', 'name', 'bound']], how='inner', on='variable')
#     idxs = []
#     temp = rev[rev['variable'].isin(value_vars_max)].index
#     if len(temp)>0:
#         sub = rev.loc[temp]
#         idxs += sub[sub['value']>sub['bound']].index.tolist()    
#     temp = rev[rev['variable'].isin(value_vars_min)].index
#     if len(temp)>0:
#         sub = rev.loc[temp]
#         idxs += sub[sub['value']<sub['bound']].index.tolist()     
#     rev = rev.iloc[idxs]
#     if rev.shape[0]>0: 
#         rev = rev.sort_values('map_id').reset_index(drop=True)
#         if set_id is not None:
#             rev['set_id'] = set_id
    
#     return rev


# def _sample(
#         set_id:str,
#         exceed_df:pd.DataFrame, 
#         start_time:Union[str, date], 
#         end_time:Union[str, date]
#         )->list:
#     exceed_df = make_sure_dataframe(exceed_df)
#     if len(exceed_df)<1:
#         return {}
#     exceed_df = _standard(set_id, exceed_df)
#     start_time = make_sure_datetime(start_time)
#     end_time = make_sure_datetime(end_time)
    
#     rev = {}
#     for _, grp in exceed_df.groupby('variable'):
#         var_name, func = grp['variable'].str.rsplit('_', n=1).iloc[0]
#         title_subfix = '超下限' if func=='min' else '超上限'
#         tid, id_ = grp.iloc[0][['device', 'map_id']]
#         temp, _ =  TDFC.read(
#             set_id=set_id,
#             turbine_id=tid,
#             start_time=start_time,
#             end_time=end_time,
#             where='and workmode=32',
#             func_dct={var_name:[func]},
#             )
#         var_name = (pd.Series(var_name)
#             .str.extractall('(var_\d+)')
#             .iloc[:, 0]
#             .drop_duplicates()
#             .tolist())
#         ts = pd.to_datetime(temp['ts'].iloc[0])
#         df, point_df = TDFC.read(
#             set_id=set_id,
#             turbine_id=tid,
#             start_time=ts-pd.Timedelta('15m'),
#             end_time=ts+pd.Timedelta('15m'),
#             var_name=var_name
#             )
#         df.rename(
#             columns={r['var_name']:r['point_name'] for _,r in point_df.iterrows()}, 
#             inplace=True
#             )
#         point_df.set_index('var_name', inplace=True)
#         fig_ts = line_plot(
#             df, 
#             point_df.loc[var_name, 'point_name'], 
#             point_df.loc[var_name, 'unit'],
#             height=450,
#             )
#         title=id_ + '_' + grp['name'].iloc[0] + '_' + title_subfix
#         rev.update({title:fig_ts})
#     return rev

# def _read_power_curve(set_id:str, turbine_id:List[str], min_date:Union[str, date], max_date:Union[str, date]):
#     df = RSDBInterface.read_statistics_sample(
#         set_id=set_id,
#         turbine_id=turbine_id,
#         start_time=min_date,
#         end_time=max_date,
#         columns = ['turbine_id', 'var_355_mean', 'var_246_mean', 'totalfaultbool_mode',
#                    'totalfaultbool_nunique', 'ongrid_mode', 'ongrid_nunique',
#                    'limitpowbool_mode', 'limitpowbool_nunique', 'evntemp_mean']
#         )
#     # 正常发电数据
#     df = df[
#         (df['totalfaultbool_mode']=='False') &
#         (df['totalfaultbool_nunique']==1) &
#         (df['ongrid_mode']=='True') & 
#         (df['ongrid_nunique']==1) & 
#         (df['limitpowbool_mode']=='False') &
#         (df['limitpowbool_nunique']==1)
#         ]
#     df.rename(columns={'var_355_mean':'mean_wind_speed', 
#                        'var_246_mean':'mean_power'}, 
#                        inplace=True)
#     # 15°空气密度
#     df['mean_wind_speed'] = df['mean_wind_speed']*np.power((273.15+df['evntemp_mean'])/288.15,1/3.0)
#     return df

# def _construct_graph(exceed_df, delta, cls):
#     exceed_df = exceed_df.copy()
#     graphs = []
#     if exceed_df.shape[0]>0:
#         ts = pd.to_datetime(exceed_df['ts'])
#         exceed_df['start_time'] = ts - pd.Timedelta(delta)
#         exceed_df['end_time'] = ts + pd.Timedelta(delta)
#         sub_df = exceed_df
#         plots = cls(sub_df)
#         graphs = [(title, fig) for title,fig in zip(sub_df['map_id'], plots.figs)]
#     return graphs

# def build_chapter(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter_index,
#                   chapter_title, table_title, inspector, grapher, fig_height, delta, fault_id):
#     _LOGGER.info(f'chapter {chapter_index} {chapter_title}')
#     candidates_df = RSDBInterface.read_statistics_fault(set_id=set_id, fault_id=fault_id, start_time=min_date, end_time=max_date)
#     candidates_df = candidates_df.loc[candidates_df.groupby('turbine_id')['timestamp'].idxmax()]
    
#     exceed_df = []
#     for _,row in candidates_df.iterrows():
#         start_time = pd.to_datetime(row['date'])
#         exceed_df.append(
#             inspector().inspect(
#                 set_id=set_id,
#                 turbine_id=row['turbine_id'],
#                 start_time=start_time,
#                 end_time=start_time+pd.Timedelta('1d'),
#                 )
#             )
#     if len(exceed_df)>0:
#         exceed_df = pd.concat(exceed_df, ignore_index=True)
#         exceed_df = exceed_df.groupby(['set_id', 'map_id']).head(1).reset_index()
#         if pd.api.types.is_number(exceed_df['value']):
#             exceed_df['value'] = exceed_df['value'].round(2)
#         columns = ['set_id', 'map_id', 'ts', 'value', 'bound']
#         fig_tbls = []
#         cnt = 20
#         for i in exceed_df.index.tolist()[::cnt]:
#             sub_df = exceed_df.iloc[i:(i+cnt)]
#             tbl = ff.create_table(sub_df[columns], height_constant=50)
#             fig_tbls.append(tbl)
#             del(tbl)
#         graphs = _construct_graph(exceed_df.head(1), delta, grapher)
    
#     rev = []
#     rev.append(Paragraph(f'{chapter_index} {chapter_title}', PS_HEADING_2))
#     rev.append(Spacer(FRAME_WIDTH_LATER, 10))
#     if len(exceed_df)<1:
#         rev.append(Paragraph('无故障', PS_BODY))
#     else:
#         title = chapter_title
#         for i, tbl in enumerate(fig_tbls):
#             rev.append(
#                 build_graph(tbl, f'{table_title}_{i}', f'{chapter_index}_{title}_{i}_table.jpg', temp_dir=temp_dir)
#                 )
#         for i, (title, plot) in enumerate(graphs):
#             rev.append(build_graph(plot, title, f'{chapter_index}_{i}_{title}.jpg', temp_dir=temp_dir, height=fig_height))
#     return rev 


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
    df = RSDBFacade.read_statistics_sample(set_id=set_id, unique=True, columns=['device_id'])
    n = df.shape[0]
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
        columns={'totalenergy':['first', 'last']})

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

# def active_power(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
#     _LOGGER.info(f'chapter {chapter}')
#     conf_df =  RSDBInterface.read_windfarm_configuration(set_id=set_id)
#     model_name = RSDBInterface.read_windfarm_turbine_model(set_id=set_id)['model_name'].iloc[0]
#     ref_df = RSDBInterface.read_windfarm_power_curve(model_name=model_name)
#     ref_df['mean_power'] = ref_df['mean_power'].astype(int)
#     ref_df.set_index('mean_speed', inplace=True)
   
#     graphs = {}
#     for model_name, grp in conf_df.groupby('model_name'):
#         turbine_id = grp['turbine_id'].tolist()
#         df = _read_power_curve(set_id, turbine_id, min_date, max_date)
#         temp = RSDBInterface.read_windfarm_configuration(set_id=set_id)
#         df['turbine_id'] = df['turbine_id'].replace({
#             row['turbine_id']:row['map_id'] for _,row in temp.iterrows()
#             })
#         df = df.sort_values(by=['turbine_id'])
#         wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26, 0.5)- 0.25)
#         df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
#         df = df[(df['wspd']>=7) & (df['wspd']<=10)]
        
#         stat_df = df.pivot_table(values='mean_power', index='turbine_id', columns='wspd').round(1)
#         isnormal_df = (stat_df-stat_df.mean()).abs() < (1.0*stat_df.std())
#         stat_df = stat_df.reset_index().rename(columns={'turbine_id':'风机编号'})
#         isnormal_df = isnormal_df.reset_index().rename(columns={'turbine_id':'风机编号'})
#         isnormal_df.iloc[:, 0] = True
#         fill_color_df = stat_df.astype(str)
#         fill_color_df.iloc[0::2, :] = '#ebecf1'
#         fill_color_df.iloc[1::2, :] = '#f9fafe'
#         fill_color_df = fill_color_df.where(isnormal_df, '#FF4500')
        
#         columns = [f'{i} ({ref_df.loc[i, "mean_power"]})' for i in stat_df.columns[1:]]
#         stat_df.columns = [f'{stat_df.columns[0]}'] + columns
        
        
#         k = 10
#         n = int(np.ceil(stat_df.shape[0]/k))
#         for i in range(n):
#             stat_sub = stat_df.iloc[(i*k):(i+1)*k, :]
#             fill_color_sub = fill_color_df.iloc[(i*k):(i+1)*k, :]
#             fig = go.Figure(data=[go.Table(
#                 header=dict(values=list(stat_sub.columns),
#                             fill_color='#3a416d',
#                             font={'color':'white'},
#                             align=['center']),
#                 cells=dict(values=[stat_sub[i] for i in stat_sub],
#                         fill_color=fill_color_sub.T,
#                         align=['center'],
#                         )
#                 )
#             ])
#             title = f'机型{model_name}_7-10mps风速区间有功功率#{i}'
#             graphs.update({title:[fig, (stat_sub.shape[0]+4)*25]})
        
#     rev = []
#     rev.append(Paragraph(f'{chapter} 有功功率', PS_HEADING_2))
#     for key_ in graphs:
#         rev.append(build_graph(graphs[key_][0], key_, f'{chapter}_{key_}.jpg', height=graphs[key_][1], temp_dir=temp_dir))
#     return rev

def _conclude(record_df):
    n = len(record_df['device_id'].unique())
    conclution = '无发生此类故障。' if len(record_df)<1 else f'{n}台机组发生此类故障。'
    return conclution

def _build_tables(record_df, temp_dir, title):
    df = record_df.groupby(['fault_id', 'device_name']).agg({'device_id':[len], 'start_time':['max']})
    df = df.reset_index().droplevel(level=1, axis=1).rename(columns={'fault_id':'id'})
    df = pd.merge(df, FAULT_TYPE_DF[['id', 'cause']], how='left').drop('id', axis=1).reset_index()
    df = df[['index', 'cause', 'device_name', 'device_id', 'start_time']]
    df.columns = ['序号', '故障原因', '设备名', '发生次数', '最近一次发生时间']
    rev = []
    count = 30
    for i in range(int(np.ceil(df.shape[0]/count))):
        sub_df = df.iloc[i*count:(i+1)*count, :]
        fig_tbl = ff.create_table(sub_df.iloc[0:], height_constant=50)
        rev.append(build_graph(fig_tbl, title+f'.{i+1}', f'{title}.jpg', temp_dir=temp_dir))
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
        ).sort_values('start_time', ascending=False)
    record_df = _standard(ftype_df['set_id'].iloc[0], record_df)
    
    func = _plot_ts if len(ftype_df)<2 else _plot_stat
    graphs = func(ftype_df, record_df)
        
    rev = []
    rev.append(Paragraph(f"{params['chapter']}.{params['section']} {ftype_df['name'].iloc[0]}", PS_HEADING_2))
    rev.append(Paragraph(_conclude(record_df), PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    code = f"{params['chapter']}.{params['section']}"
    if len(record_df)>0:
        rev += _build_tables(record_df, temp_dir=params['temp_dir'], title=f'表 {code}.{1}')
    i = 0
    for name, figure in graphs:
        title = f"图 {code}.{i+1} {name}"
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
    device_id= anormaly_df.sort_values('create_time').tail(1).squeeze()[['device_id']]
    device_name = DEVICE_DF[DEVICE_DF['device_id']==device_id]['device_name']
    fig = graph_factory.get('Anomaly')().plot(
        set_id=set_id,
        device_id=device_id,
        start_time=min_date,
        end_time=max_date,
        )

    rev = []
    rev.append(Paragraph('4 离群数据', PS_HEADING_1))
    rev.append(Paragraph(f'本期报告时段内共有离群数据：{total}条, 待鉴别{left}条', PS_BODY))
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
        remote=False)
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
@log_it(_LOGGER, True)
def build_brief_report_all(*args, **kwargs):
    '''
    end_time : 截至时间
    delta : 单位天
    >>> build_brief_report_all(end_time='', delta=180)
    '''
    assert pd.Series(['end_time', 'delta']).isin(kwargs).all()
    if kwargs['end_time'] is not None and kwargs['end_time']!='':
        end_time = pd.to_datetime(kwargs['end_time']).date()
    else:
        end_time = pd.Timestamp.now().date()
    start_time = end_time - pd.Timedelta(f"{kwargs['delta']}d")
    df = PGFacade.read_model_device()
    for set_id in df['set_id'].unique():
        filename = f"brief_report_{set_id}_{end_time}_{kwargs['delta']}d.pdf"
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
    build_brief_report_all(end_time='2023-03-14', delta=190)