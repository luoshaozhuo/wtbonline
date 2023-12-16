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
from typing import List, Union
from datetime import date
import itertools
from tempfile import TemporaryDirectory

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
from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._db.common import make_sure_dataframe
from wtbonline._db.common import make_sure_list, make_sure_datetime
from wtbonline._logging import get_logger, log_it
from wtbonline._plot.functions import line_plot, scatter_matrix_anormaly
import wtbonline._plot as plt
import wtbonline._process.inspector as insp
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

TEMP_DIR = RSDBInterface.read_app_configuration(key_='tempdir')['value'].squeeze()
TEMP_DIR = Path(TEMP_DIR)
TEMP_DIR.mkdir(exist_ok=True)

_LOGGER = get_logger('brief_report')

DBNAME = RSDBInterface.read_app_server(remote=1)['database'].iloc[0]

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
    where = 'and workmode=32 '
    df, point_df = TDFC.read(
        set_id=set_id,
        turbine_id=turbine_id,
        start_time=start_time,
        end_time=end_time,
        where=where,
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
    return build_graph(fig_tbl, title, f'{title}.jpg', temp_dir=temp_dir)

def _exceed(raw_df, bound_df, set_id=None):
    value_vars_max = raw_df.filter(axis=1, regex='.*_max$').columns.tolist()
    value_vars_min = raw_df.filter(axis=1, regex='.*_min$').columns.tolist()
    value_vars = value_vars_max + value_vars_min
    id_vars = raw_df.columns[~raw_df.columns.isin(value_vars)]
    raw_melt = raw_df.melt(id_vars, value_vars)
    
    bound_df = bound_df.rename(columns={'lower_bound':'_min', 'upper_bound':'_max'})
    value_vars = bound_df.filter(axis=1, regex='.*_(max|min)$').columns
    id_vars = bound_df.columns[~bound_df.columns.isin(value_vars)]
    bound_melt = bound_df.melt(id_vars, value_vars, value_name='bound')
    bound_melt['variable'] = bound_melt['var_name']+bound_melt['variable']
    
    rev = pd.merge(raw_melt, bound_melt[['variable', 'name', 'bound']], how='inner', on='variable')
    idxs = []
    temp = rev[rev['variable'].isin(value_vars_max)].index
    if len(temp)>0:
        sub = rev.loc[temp]
        idxs += sub[sub['value']>sub['bound']].index.tolist()    
    temp = rev[rev['variable'].isin(value_vars_min)].index
    if len(temp)>0:
        sub = rev.loc[temp]
        idxs += sub[sub['value']<sub['bound']].index.tolist()     
    rev = rev.iloc[idxs]
    if rev.shape[0]>0: 
        rev = rev.sort_values('map_id').reset_index(drop=True)
        if set_id is not None:
            rev['set_id'] = set_id
    
    return rev

def _conclude(exceed_df):
    if len(exceed_df)==0:
        conclution = '无超限'
    else:
        conclution = ''
        for key_, grp in exceed_df.groupby('name'):
            map_ids = grp['map_id'].drop_duplicates().sort_values()
            conclution += f"{key_}超限：{','.join(map_ids)}<br />\n"
    return conclution

def _sample(
        set_id:str,
        exceed_df:pd.DataFrame, 
        start_time:Union[str, date], 
        end_time:Union[str, date]
        )->list:
    exceed_df = make_sure_dataframe(exceed_df)
    if len(exceed_df)<1:
        return {}
    exceed_df = _standard(set_id, exceed_df)
    start_time = make_sure_datetime(start_time)
    end_time = make_sure_datetime(end_time)
    
    rev = {}
    for _, grp in exceed_df.groupby('variable'):
        var_name, func = grp['variable'].str.rsplit('_', n=1).iloc[0]
        title_subfix = '超下限' if func=='min' else '超上限'
        tid, id_ = grp.iloc[0][['device', 'map_id']]
        temp, _ =  TDFC.read(
            set_id=set_id,
            turbine_id=tid,
            start_time=start_time,
            end_time=end_time,
            where='and workmode=32',
            func_dct={var_name:[func]},
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
        title=id_ + '_' + grp['name'].iloc[0] + '_' + title_subfix
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

def _construct_graph(exceed_df, delta, cls):
    exceed_df = exceed_df.copy()
    graphs = []
    if exceed_df.shape[0]>0:
        ts = pd.to_datetime(exceed_df['ts'])
        exceed_df['start_time'] = ts - pd.Timedelta(delta)
        exceed_df['end_time'] = ts + pd.Timedelta(delta)
        sub_df = exceed_df
        plots = cls(sub_df)
        graphs = [(title, fig) for title,fig in zip(sub_df['map_id'], plots.figs)]
    return graphs

def build_chapter(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter_index,
                  chapter_title, table_title, inspector, grapher, fig_height, delta, fault_id):
    _LOGGER.info(f'chapter {chapter_index} {chapter_title}')
    candidates_df = RSDBInterface.read_statistics_fault(set_id=set_id, fault_id=fault_id, start_time=min_date, end_time=max_date)
    candidates_df = candidates_df.loc[candidates_df.groupby('turbine_id')['timestamp'].idxmax()]
    
    exceed_df = []
    for _,row in candidates_df.iterrows():
        start_time = pd.to_datetime(row['date'])
        exceed_df.append(
            inspector().inspect(
                set_id=set_id,
                turbine_id=row['turbine_id'],
                start_time=start_time,
                end_time=start_time+pd.Timedelta('1d'),
                )
            )
    if len(exceed_df)>0:
        exceed_df = pd.concat(exceed_df, ignore_index=True)
        exceed_df = exceed_df.groupby(['set_id', 'map_id']).head(1).reset_index()
        if pd.api.types.is_number(exceed_df['value']):
            exceed_df['value'] = exceed_df['value'].round(2)
        columns = ['set_id', 'map_id', 'ts', 'value', 'bound']
        fig_tbls = []
        cnt = 20
        for i in exceed_df.index.tolist()[::cnt]:
            sub_df = exceed_df.iloc[i:(i+cnt)]
            tbl = ff.create_table(sub_df[columns], height_constant=50)
            fig_tbls.append(tbl)
            del(tbl)
        graphs = _construct_graph(exceed_df.head(1), delta, grapher)
    
    rev = []
    rev.append(Paragraph(f'{chapter_index} {chapter_title}', PS_HEADING_2))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    if len(exceed_df)<1:
        rev.append(Paragraph('无故障', PS_BODY))
    else:
        title = chapter_title
        for i, tbl in enumerate(fig_tbls):
            rev.append(
                build_graph(tbl, f'{table_title}_{i}', f'{chapter_index}_{title}_{i}_table.jpg', temp_dir=temp_dir)
                )
        for i, (title, plot) in enumerate(graphs):
            rev.append(build_graph(plot, title, f'{chapter_index}_{i}_{title}.jpg', temp_dir=temp_dir, height=fig_height))
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
    farm_df = RSDBInterface.read_windfarm_configuration(set_id=set_id)
    df = RSDBInterface.read_statistics_sample(set_id=set_id, unique=True, columns=['turbine_id'])
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
    fns = ['first', 'last']
    df = []
    for func in fns:
        temp,_ = TDFC.read(set_id=set_id, turbine_id=None, start_time=min_date, end_time=max_date,
                    groupby='device', func_dct={'totalenergy':[func]})
        df.append(temp)
    df = pd.merge(*df, how='inner', on='device').round(0)

    df['发电量（kWh）'] = df['totalenergy_last'] - df['totalenergy_first']
    df = df.sort_values('发电量（kWh）', ascending=False)
    df = _standard(set_id, df)

    cols = ['map_id', '发电量（kWh）']
    graphs = {}
    for i in range(int(np.ceil(df.shape[0]/10))):
        sub_df = df.iloc[i*10:(i+1)*10, :]
        fig = ff.create_table(sub_df[cols], height_constant=50)
        fig.add_traces([go.Bar(x=sub_df['map_id'], 
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
        fig.layout.xaxis2.update({'title': 'map_id'})
        fig.layout.update({'title': f'{min_date}至{max_date}累积发电量'})
        graphs.update({f'排名{i*10+1}至{i*10+10}':fig})

    rev = []
    rev.append(Paragraph('2 发电情况', PS_HEADING_1))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir=temp_dir))
    return rev

def active_power(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    conf_df =  RSDBInterface.read_windfarm_configuration(set_id=set_id)
    model_name = RSDBInterface.read_windfarm_turbine_model(set_id=set_id)['model_name'].iloc[0]
    ref_df = RSDBInterface.read_windfarm_power_curve(model_name=model_name)
    ref_df['mean_power'] = ref_df['mean_power'].astype(int)
    ref_df.set_index('mean_speed', inplace=True)
   
    graphs = {}
    for model_name, grp in conf_df.groupby('model_name'):
        turbine_id = grp['turbine_id'].tolist()
        df = _read_power_curve(set_id, turbine_id, min_date, max_date)
        temp = RSDBInterface.read_windfarm_configuration(set_id=set_id)
        df['turbine_id'] = df['turbine_id'].replace({
            row['turbine_id']:row['map_id'] for _,row in temp.iterrows()
            })
        df = df.sort_values(by=['turbine_id'])
        wspd = pd.cut(df['mean_wind_speed'],  np.arange(0,26, 0.5)- 0.25)
        df['wspd'] = wspd.apply(lambda x:x.mid).astype(float)
        df = df[(df['wspd']>=7) & (df['wspd']<=10)]
        
        stat_df = df.pivot_table(values='mean_power', index='turbine_id', columns='wspd').round(1)
        isnormal_df = (stat_df-stat_df.mean()).abs() < (1.0*stat_df.std())
        stat_df = stat_df.reset_index().rename(columns={'turbine_id':'风机编号'})
        isnormal_df = isnormal_df.reset_index().rename(columns={'turbine_id':'风机编号'})
        isnormal_df.iloc[:, 0] = True
        fill_color_df = stat_df.astype(str)
        fill_color_df.iloc[0::2, :] = '#ebecf1'
        fill_color_df.iloc[1::2, :] = '#f9fafe'
        fill_color_df = fill_color_df.where(isnormal_df, '#FF4500')
        
        columns = [f'{i} ({ref_df.loc[i, "mean_power"]})' for i in stat_df.columns[1:]]
        stat_df.columns = [f'{stat_df.columns[0]}'] + columns
        
        
        k = 10
        n = int(np.ceil(stat_df.shape[0]/k))
        for i in range(n):
            stat_sub = stat_df.iloc[(i*k):(i+1)*k, :]
            fill_color_sub = fill_color_df.iloc[(i*k):(i+1)*k, :]
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(stat_sub.columns),
                            fill_color='#3a416d',
                            font={'color':'white'},
                            align=['center']),
                cells=dict(values=[stat_sub[i] for i in stat_sub],
                        fill_color=fill_color_sub.T,
                        align=['center'],
                        )
                )
            ])
            title = f'机型{model_name}_7-10mps风速区间有功功率#{i}'
            graphs.update({title:[fig, (stat_sub.shape[0]+4)*25]})
        
    rev = []
    rev.append(Paragraph(f'{chapter} 有功功率', PS_HEADING_2))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_][0], key_, f'{chapter}_{key_}.jpg', height=graphs[key_][1], temp_dir=temp_dir))
    return rev


def gearbox(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    cols = ['var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, min_date, max_date)

    rev = []
    rev.append(Paragraph(f'{chapter} 齿轮箱', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '齿轮箱关键参数', temp_dir=temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{chapter}_{key_}.jpg', temp_dir=temp_dir))
    return rev


def main_bearing(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    cols = ['var_171', 'var_172', 'abs(var_171-var_172)']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, min_date, max_date)

    rev = []
    rev.append(Paragraph(f'{chapter} 主轴承', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))  
    rev.append(_build_table(raw_df, bound_df, '主轴承关键参数', temp_dir=temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{chapter}_{key_}.jpg', temp_dir=temp_dir))
    return rev


def generator(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    cols = ['var_206', 'var_207', 'var_208', 'var_209', 'var_210', 'var_211']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, min_date, max_date)

    rev = []
    rev.append(Paragraph(f'{chapter} 发电机', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '发电机关键参数', temp_dir=temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{chapter}_{key_}.jpg', temp_dir=temp_dir))
    return rev


def converter(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    cols = ['var_15004', 'var_15005', 'var_15006', 'var_12016']
    bound_df = RSDBInterface.read_turbine_variable_bound(set_id=set_id, var_name=cols)
    funcs = ['min', 'max']
    raw_df, _ = _stat(set_id, min_date, max_date, cols, funcs)
    exceed_df = _exceed(raw_df, bound_df)
    conclution = _conclude(exceed_df)
    graphs = _sample(set_id, exceed_df, min_date, max_date)

    rev = []
    rev.append(Paragraph(f'{chapter} 变流器', PS_HEADING_2))
    rev.append(Paragraph(conclution, PS_BODY))
    rev.append(Spacer(FRAME_WIDTH_LATER, 10))
    rev.append(_build_table(raw_df, bound_df, '变流器关键参数', temp_dir=temp_dir))
    for key_ in graphs:
        rev.append(build_graph(graphs[key_], key_, f'{chapter}_{key_}.jpg', temp_dir=temp_dir))
    return rev

def energy_difference(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir, chapter):
    _LOGGER.info(f'chapter {chapter}')
    dbname = RSDBInterface.read_app_server(remote=1)['database'].iloc[0]
    # 选出发电量排前2及后2的机组
    cols = ['totalenergy']
    funcs = ['first', 'last']
    vars = [f'{f}({v}) as {v}_{f}' for v, f in itertools.product(cols, funcs)]
    sql = f'''
        select 
            device,
            {', '.join(vars)} 
        from 
            s_{set_id} 
        where 
            ongrid=1 
            and ts>='{min_date}' 
            and ts<'{max_date}'
        group by 
            device
        '''
    raw_df = _standard(set_id, TDFC.query(sql))
    raw_df['totalenergy'] = raw_df['totalenergy_last'] - raw_df['totalenergy_first']
    raw_df.sort_values('totalenergy', ascending=True, inplace=True)
    raw_df = pd.concat([raw_df.head(2), raw_df.tail(2)], ignore_index=True).drop_duplicates('map_id')
    # 绘图
    sql = f'''
        SELECT
            var_94_mean,
            var_246_mean,
            var_101_mean,
            var_102_mean,
            var_103_mean 
        FROM
            statistics_sample 
        WHERE
            workmode_unique = 32 
            and ongrid_unique = 'True' 
            and totalfaultbool_unique = 'False' 
            and limitpowbool_unique = 'False'
            and bin>='{min_date}' 
            and bin<'{max_date}'
        '''
    fig_scatter = None
    count = 3000
    colors = px.colors.qualitative.Plotly
    for i, row in raw_df.iterrows():
        if fig_scatter is None:
            fig_scatter = make_subplots(2, 1, shared_xaxes=True, vertical_spacing=0.05)
        plot_df = RSDB.read_sql(sql)
        if plot_df.shape[0]<1:
            continue
        plot_df = plot_df.sample(count) if plot_df.shape[0]>count else plot_df
        fig_scatter.add_trace(
            go.Scatter(
                x=plot_df['var_246_mean'], 
                y=(plot_df['var_101_mean'] + plot_df['var_101_mean'] + plot_df['var_101_mean'])/3.0, 
                mode='markers',
                marker=dict(size=3,opacity=0.5,color=colors[i]), 
                name=f'''{row['map_id']}@{row['totalenergy']}(kWh)'''
                ),
            row=1,
            col=1    
            )
        fig_scatter.add_trace(
            go.Scatter(
                x=plot_df['var_246_mean'], 
                y=plot_df['var_94_mean'], 
                mode='markers',
                marker=dict(size=3,opacity=0.5,color=colors[i]),
                name=f'''{row['map_id']}@{row['totalenergy']}(kWh)''',
                showlegend=False,
                ),
            row=2,
            col=1    
            )
        
    if fig_scatter is not None:
        fig_scatter.update_xaxes(title_text='并网有功功率（kWh）', row=2, col=1)
        fig_scatter.update_yaxes(title_text='叶片实际角均值（°）', row=1, col=1)
        fig_scatter.update_yaxes(title_text='风轮转速', row=2, col=1)
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
  
    rev = []
    rev.append(Paragraph(f'{chapter} 发电量差异分析', PS_HEADING_2))
    rev.append(Paragraph(f'包含发电量最低及最高各两台设备清单（按发电量升序）：{", ".join(raw_df["map_id"])}', PS_BODY))
    rev.append(build_graph(fig_scatter, '并网有功功率-桨距角', f'{chapter}_scatter.jpg', temp_dir=temp_dir))
    return rev


def chapter_3(set_id:str, min_date:Union[str, date], max_date:Union[str, date], temp_dir):
    _LOGGER.info('chapter 3')
    params = dict(set_id=set_id, min_date=min_date, max_date=max_date, temp_dir=temp_dir)
    return [
        Paragraph('3 运行一致性', PS_HEADING_1),        
        *active_power(**params, chapter='3-1'),
        *gearbox(**params, chapter='3-2'),
        *generator(**params, chapter='3-3'),
        *converter(**params, chapter='3-4'),
        *main_bearing(**params, chapter='3-5'),
        *build_chapter(**params, chapter_index='3-6', chapter_title='叶根载荷不平衡', table_title='叶根弯矩不平衡超限', 
                       inspector=insp.BladeUnbalanceLoadInspector, grapher=plt.BladeUnblacedLoad, fig_height=None, delta='12h', fault_id=8),
        *build_chapter(**params, chapter_index='3-7', chapter_title='叶根摆振弯矩', table_title='叶根摆振弯矩超限', 
                       inspector=insp.BladeEdgewiseOverLoadedInspector, grapher=plt.BladeOverloaded, fig_height=None, delta='30m', fault_id=10),
        *build_chapter(**params, chapter_index='3-8', chapter_title='叶根挥舞弯矩', table_title='叶根挥舞弯矩超限', 
                inspector=insp.BladeFlapwiseOverLoadedInspector, grapher=plt.BladeOverloaded, fig_height=None, delta='30m', fault_id=11),
        *build_chapter(**params, chapter_index='3-9', chapter_title='Pitchkick', table_title='触发Pitchkick', 
                inspector=insp.BladePitchkickInspector, grapher=plt.BladePitchkick, fig_height=None, delta='10m', fault_id=6),
        *build_chapter(**params, chapter_index='3-10', chapter_title='叶片不同步', table_title='叶片不同步事件', 
                inspector=insp.BladeAsynchronousInspector, grapher=plt.BladeAsynchronous, fig_height=None, delta='10m', fault_id=7),
        *energy_difference(**params, chapter='3-11'),
        *build_chapter(**params, chapter_index='3-12', chapter_title='风轮方位角', table_title='风轮方位角异常事件', 
                inspector=insp.HubAzimuthInspector, grapher=plt.HubAzimuth, fig_height=None, delta='12h', fault_id=9),
        *build_chapter(**params, chapter_index='3-13', chapter_title='发电机超功率', table_title='发电机超功率事件', 
                inspector=insp.OverPowerInspector, grapher=plt.GeneratorOverloaded, fig_height=None, delta='12h', fault_id=5),
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
        rev.append(Paragraph('指定时间范围内无离群值识别记录', PS_BODY))
        return rev
    
    label_df = RSDBInterface.read_model_label(set_id=set_id).drop_duplicates('sample_id')
    total = anormaly_df.shape[0]
    left = total - label_df.shape[0]

    # 取最后一个样本点
    turbine_id, uuids = anormaly_df.sort_values('create_time').tail(1).squeeze()[['turbine_id', 'model_uuid']]
    sub_anormaly = anormaly_df[(anormaly_df['set_id']==set_id) & (anormaly_df['turbine_id']==turbine_id)]
    stat_df = RSDBInterface.read_statistics_sample(
                set_id=set_id,
                turbine_id=turbine_id,
                start_time=min_date,
                end_time=max_date
                )
    # 利用模型里的filter函数筛选样本
    _, trainer = load_model(uuids.split(',')[0], return_trainer=True)
    stat_df = trainer.data_filter(stat_df).set_index('id', drop=True)
    # 正常样本抽样，异常样本全部保留
    stat_df['is_anormaly'] = False
    stat_normal = stat_df if len(stat_df)<4001 else stat_df.sample(4000)
    stat_abnormal = stat_df.loc[sub_anormaly['sample_id']]
    stat_abnormal['is_anormaly'] = True
    plot_df = pd.concat([stat_abnormal, stat_normal], axis=0, ignore_index=True).drop_duplicates('bin', keep='first')
    columns = ['var_94_mean', 'var_355_mean', 'var_226_mean', 'var_101_mean', 'var_382_mean', 'var_383_mean']
    fig = scatter_matrix_anormaly(plot_df, set_id=set_id, columns=columns)

    map_id = _standard(set_id, plot_df.head(1)).squeeze()['map_id']

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
        rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir=temp_dir))
    return rev

def build_brief_report(
        *, 
        pathname:str, 
        set_id:str, 
        start_time:Union[str, date], 
        end_time:Union[str, date]
        ):
    fns = ['first', 'last']
    df = []
    for func in fns:
        temp, _ = TDFC.read(
            set_id=set_id, turbine_id=None, start_time=start_time, end_time=end_time, 
            func_dct={'ts':[func]}, groupby='device', remote=False)
        df.append(temp)
    df = pd.concat(df, axis=1)
    min_date = df['ts_first'].min()
    max_date = df['ts_last'].max()

    doc = BRDocTemplate(pathname)
    add_page_templates(doc)
    with TemporaryDirectory(dir=TEMP_DIR.as_posix()) as temp_dir:
        _LOGGER.info(f'temp directory:{temp_dir}')
        doc.build([
            *chapter_1(set_id, start_time, end_time, min_date, max_date),
            *chapter_2(set_id, min_date, max_date, temp_dir),
            *chapter_3(set_id, min_date, max_date, temp_dir),
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
    build_brief_report_all(end_time='2023-12-14', delta=90)