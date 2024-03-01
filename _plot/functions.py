import pstats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from collections.abc import Iterable
from typing import List

from wtbonline._common.utils import interchage_mapid_and_tid, make_sure_list, make_sure_dataframe, interchage_varName_and_pointName
from wtbonline._common import utils
from wtbonline._db.rsdb_interface import RSDBInterface

# =============================================================================
# function
# =============================================================================
def _to_list(x):
    if x is None:
        x = []
    elif isinstance(x, str) or (not isinstance(x, Iterable)):
        x = [x]
    else:
        x = list(x)
    return x

def _line_trace(df, ycol, xcol='ts', mode='lines+markers'):
    return  go.Scatter(x=df[xcol], 
                       y=df[ycol],
                       name=ycol,
                       mode=mode,           
                       marker={'opacity':0.2})
            
def line_plot(df, ycols, units, *, xcol='ts', xtitle='时间', layout=None, title=None, 
              refx=None, refy=None, height=None, showlegend=False):  
    ''' 并列单系列折线图 '''
    ycols = _to_list(ycols)
    units = _to_list(units)
    assert len(ycols)==len(units), f'{ycols},{units}'

    if layout is None:
        rows = len(ycols)
        layout = np.arange(rows)+1
    else:
        rows = pd.Series(layout).unique().shape[0]           
        
    line_chart = make_subplots(rows=rows, cols=1, shared_xaxes=True)
    if df[ycols].shape[0]<1:
        return line_chart
    
    for i in range(len(ycols)):
        line_chart.add_trace(_line_trace(df, ycols[i], xcol), row=layout[i], col=1)
        if refx is not None and refy is not None:
            line_chart.add_trace(
                go.Scatter(
                    x=refx,
                    y=refy,
                    line=dict(color='black', dash='dash'),
                    mode='lines',
                    name='参考功率曲线'
                    ),
                row=layout[i],
                col=1,
                ) 
        line_chart.update_yaxes(title_text=ycols[i]+' '+units[i], row=layout[i], col=1)
    line_chart.update_xaxes(title_text=xtitle, row=layout[i], col=1)
        
    line_chart.update_layout(
        title=title,
        height=300*len(ycols) if height is None else height,
        legend=dict(
            orientation="h",
            font=dict(
                    size=10,
                    color="black"
                ),
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        showlegend=showlegend,
        margin=dict(l=80, r=80, t=80, b=80),
        hovermode="x unified"
        )
    line_chart.update_yaxes(showspikes=True)
    return line_chart


def anormaly_plot(df, xcol, ycol, idcol='id'):
    fig = go.Figure()
    if df[[xcol, ycol]].shape[0]<1:
        return fig
    
    fig.add_trace(
        go.Histogram2dContour(
            x = df[xcol],
            y = df[ycol],
            colorscale = 'Blues',
            showscale=False,
            xaxis = 'x',
            yaxis = 'y',
            )
        )
    sub = df[(df[xcol]>10) & (df[ycol]<2000)]
    fig.add_trace(
        go.Scatter(
            x = sub[xcol],
            y = sub[ycol],
            mode = 'markers',
            marker = {'color':'red'},
            xaxis = 'x',
            yaxis = 'y',
            opacity = 0.5,
            customdata=df[idcol]
            )
        )    
    fig.add_trace(
        go.Scatter(
            x = df[xcol],
            y = df[ycol],
            mode = 'markers',
            marker = {'color':'black'},
            xaxis = 'x',
            yaxis = 'y',
            opacity = 0.2,
            customdata=df[idcol]
            )
        )
    fig.update_layout(xaxis_title=xcol, yaxis_title=ycol)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_layout(clickmode='event+select')
    fig.update_layout(showlegend=False)
    return fig

def _amplitude_spectrum(y_t, sample_spacing=1):
    N = len(y_t)
    x_fft = np.fft.fftfreq(N, sample_spacing)
    y_fft = np.abs(np.fft.fft(y_t))*2.0/N # 单边幅度谱    
    return x_fft, y_fft

def _power_spectrum(y_t, sample_spacing=1):
    x_fft, y_fft = _amplitude_spectrum(y_t, sample_spacing)
    y_fft = y_fft*y_fft/2/np.pi/(sample_spacing*len(y_t))
    return x_fft, y_fft

def spectrum_plot(df, ycol, unit, charateristic_freq=[], sample_spacing=1):
    '''
    sample_spacing: float
        采样周期，单位秒
    '''
    fig = go.Figure()
    if df[ycol].shape[0]<1:
        return fig
    
    y_t = df[ycol] - df[ycol].mean()
    x_fft, y_fft = _power_spectrum(y_t, sample_spacing=1)
    
    xcol = 'frequency(Hz)'
    df = pd.DataFrame({xcol:x_fft, ycol:y_fft})
    df = df[df[xcol]>=0]    
    
    fig = fig.add_trace(_line_trace(df, ycol, xcol))
    fig.update_layout(xaxis_title=xcol, yaxis_title=unit)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    for i in range(len(charateristic_freq)):
        fig.add_vline(x=charateristic_freq[i], annotation_text=f"特征频率{i}",
                      annotation_font_size=10, line_width=1, line_dash="dash", line_color="green")
    return fig

def scatter_matrix_plot_anomaly(df=None, columns=None, set_id=None, selectedpoints=[]):
    columns = make_sure_list(columns)
    fig = go.Figure()
    if df is not None and set_id is not None and len(columns)>0:
        idx_not_susptor= df[df['is_suspector']==-1].index
        idx_suspetor_without_label = df[(df['is_anomaly']==0) & (df['is_suspector']==1)].index
        idx_anormaly = df[df['is_anomaly']==1].index
        idx_not_anormaly = df[df['is_anomaly']==-1].index
        df.loc[idx_not_susptor, 'textd'] = '非离群'
        df.loc[idx_suspetor_without_label, 'textd'] ='离群，未标注'
        df.loc[idx_anormaly, 'textd'] = '异常'
        df.loc[idx_not_anormaly, 'textd'] = '正常'
        df.loc[idx_not_susptor, 'color'] = 'gray'
        df.loc[idx_suspetor_without_label, 'color'] =' yellow'
        df.loc[idx_anormaly, 'color'] ='red'
        df.loc[idx_not_anormaly, 'color'] = 'green'        
        df.loc[idx_not_susptor, 'opacity'] = 0.2
        df.loc[idx_suspetor_without_label, 'opacity'] = 1
        df.loc[idx_anormaly, 'opacity'] = 1
        df.loc[idx_not_anormaly, 'opacity'] = 1 
        customdata = df['id'].to_list() if 'id' in df.columns else None
        
        dimensions = []
        labels = interchage_varName_and_pointName(
            set_id=set_id,
            var_name=tuple(pd.Series(columns).str.replace('_mean', '')),
            append_unit=True
            )
        for col, label in zip(columns, labels):
            dimensions.append(dict(label=label, values=df[col]))
        fig.add_trace(
            go.Splom(
                dimensions=dimensions,
                marker=dict(color=df['color'],
                            size=3,
                            line=dict(width=0),
                            opacity=df['opacity'],
                            ),
                text=df['textd'],
                showupperhalf=False,
                customdata=customdata,
                selected={'marker':{'color':'cyan', 'opacity':1, 'size':6}},
                diagonal=dict(visible=False),
                selectedpoints=selectedpoints,
                )
            )
    fig.update_layout(
        **{f'xaxis{(i+1)}':{'title':{'font':{'size':12}}} for i in range(len(labels))},
        **{f'yaxis{(i+1)}':{'title':{'font':{'size':12}}} for i in range(len(labels))},
        clickmode='event+select',
        height=800,
        hovermode='closest',
        margin=dict(l=20, r=20, t=20, b=20),
        )
    
    return fig

def ts_plot_multiple_y(df=None, ycols=None, units=None, ytitles=None, x='ts', xtitle='时间', ref_col=None, sample_spacing=1):
    '''
    >>> from wtbonline._pages.tools.utils import read_sample_ts
    >>> sample_id = 2300
    >>> var_name = ['var_18003', 'var_355']
    >>> df, point_df = read_sample_ts(sample_id, var_name)
    >>> point_df.set_index('var_name', inplace=True)
    >>> fig = ts_plot_multiple_y(df, var_name, point_df.loc[var_name, 'unit'], point_df.loc[var_name, 'point_name'])
    >>> fig.show()
    '''
    df = make_sure_dataframe(df)
    ycols = make_sure_list(ycols)
    units = make_sure_list(units)
    ytitles = ['']*len(ycols) if ytitles is None else make_sure_list(ytitles)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    secondary_y = False
    if df.shape[0]>0:
        for i,col in enumerate(ycols):
            if col=='':
                continue
            if col==ycols[-1] and len(ycols)>1:
                secondary_y = True
            fig.add_trace(
                go.Scatter(
                    x=df[x],
                    y=df[col],
                    mode='lines+markers',
                    marker={'size':2},
                    name=ytitles[i],
                    ),
                secondary_y=secondary_y,
                )
            if i==0 or col==ycols[-1]:
                fig.update_yaxes(title_text=ytitles[i]+' '+units[i], secondary_y=secondary_y)
    fig.update_xaxes(title_text=xtitle)
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        clickmode='event+select',
        hovermode='x',
        margin=dict(l=20, r=20, t=20, b=20),
        )
    return fig
    
def spc_plot_multiple_y(df=None, ycols=None, units=None, ytitles=None, x='ts', xtitle='时间', ref_col=None, sample_spacing=1):
    '''
    sample_spacing: float
        采样周期，单位秒
    ref_col:str
        字段单位，默认为rpm
    >>> from wtbonline._pages.tools.utils import read_sample_ts
    >>> sample_id = 2300
    >>> var_name = ['var_94']
    >>> df, point_df = read_sample_ts(sample_id, tuple(var_name+['var_94']))
    >>> point_df.set_index('var_name', inplace=True)
    >>> fig = spc_plot_multiple_y(df, var_name, point_df.loc[var_name, 'unit'], point_df.loc[var_name, 'point_name'], ref_col='var_94')
    >>> fig.show()
    '''
    df = make_sure_dataframe(df.copy())
    ycols = make_sure_list(ycols)
    if df.shape[0]>0:
            for y in ycols:
                if y=='' or (df[y]==df[y].iloc[0]).all()==True:
                    continue
                df[y] = df[y] - df[y].mean()
                x_fft, y_fft = _power_spectrum(df[y], sample_spacing=sample_spacing)
                df[y] = y_fft
                if 'x' not in df.columns:
                    df['x'] = x_fft
    if 'x' in (df.columns):
        df = df[df['x']>0]
    else:
        df = pd.DataFrame(columns=df.columns.tolist()+['x'])
    xtitle = '频率_Hz'
    fig = ts_plot_multiple_y(df, ycols, [f'({i})^2' for i in units], ytitles=ytitles, x='x', xtitle=xtitle)
    if (ref_col is not None) and df.shape[0]>1:
        freq_ref = df[ref_col].abs().mean() / 60.0
        if freq_ref>0:
            for i in range(int(min(df['x'].max()/freq_ref, 10))):
                fig.add_vline(
                    x=(i+1)*freq_ref, 
                    annotation_text=f"{i+1}倍频",
                    annotation_font_size=10, 
                    line_width=1, 
                    line_dash="dash", 
                    line_color="green"
                    )
    return fig

def get_simple_plot_parameters(xcol:str, ycol:str, y2col:str, plot_type:str, set_id:str):
    point_name = pd.Series([xcol, ycol, y2col]).replace(['ts', '时间','频率'], None).dropna()
    df = RSDBInterface.read_turbine_model_point(
        set_id=set_id,
        point_name=point_name,
        select=None
        ).drop_duplicates('point_name').set_index('point_name', drop=False)
    assert len(df)==len(point_name), f'部分字段获取失败，需要{point_name.tolist()}，实际返回{df.index.tolist()}'
    
    get_col = lambda x:None if x in [None, ''] else df.loc[x, 'var_name'].lower()
    get_title = lambda x:None if x in [None, ''] else df.loc[x, 'point_name'] + '_' + df.loc[x, 'unit']
    
    ytitle = get_title(ycol)
    ycol = get_col(ycol)
    y2title = get_title(y2col)
    y2col = get_col(y2col)
    if plot_type == '时序图':
        xcol = 'ts'
        xtitle = '时间'
        mode = 'markers+lines'
    elif plot_type in ('散点图', '极坐标图'):
        xtitle = get_title(xcol)
        xcol = get_col(xcol)
        mode = 'markers'
    elif plot_type == '频谱图':
        xtitle = '频率 Hz'
        xcol = 'ts'
        mode = 'markers+lines'
    else:
        raise ValueError(f'不支持此种图形类别：{plot_type}')
    
    return xcol, xtitle, ycol, ytitle, y2col, y2title, mode


def get_simple_plot_selections(set_id, plot_type):
    model_point_df = RSDBInterface.read_turbine_model_point(
        set_id=set_id,
        columns=['point_name', 'unit', 'set_id', 'datatype'],
        select=[0,1]
        )
    if plot_type=='时序图':
        x_data = ['时间']
        x_value = '时间'
        y_data = model_point_df['point_name']
        y_value = None
    elif plot_type=='散点图':
        x_data = model_point_df['point_name']
        x_value = None
        y_data = model_point_df['point_name']
        y_value = None
    elif plot_type=='极坐标图':
        x_data = model_point_df['point_name'][
                    (model_point_df['point_name'].str.find('角')>-1) & 
                    (model_point_df['unit']=='°')
                    ]
        x_value = None
        y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
        y_value = None    
    elif plot_type=='频谱图':
        x_data = ['频率']
        x_value = '频率'
        y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
        y_value = None
    x_data = [{'value':i, 'label':i} for i in x_data]
    y_data = [{'value':i, 'label':i} for i in y_data]
    return x_data, x_value, y_data, y_value

def simple_plot(
        *, 
        x_lst:List[List[float]]=[],
        y_lst:List[List[float]]=[], 
        y2_lst:List[List[float]]=[],
        xtitle:str='', 
        ytitle:str='', 
        y2title:str='',
        name_lst:List[str]=[],
        mode:str='markers+lines',
        _type:str='散点图',
        ref_freqs:List[float]=[],
        height:int=700
        ):
    # x_lst = make_sure_list(x_lst)
    # y_lst = make_sure_list(y_lst)
    # y2_lst = make_sure_list(y2_lst)
    name_lst = make_sure_list(name_lst)
    ref_freqs = make_sure_list(ref_freqs)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for i, name in enumerate(name_lst):
        if _type=='极坐标图':
            trace = go.Scatterpolar(
                theta=x_lst[i], 
                r=y_lst[i],
                name=name,
                mode=mode,
                showlegend=True,
                marker=dict(size=3, opacity=0.5)
                )
            fig.add_trace(trace)
        elif _type=='频谱图':
            x, y = _power_spectrum(y_lst[i])
            df = pd.DataFrame({'x':x, 'y':y})
            df = df[df['x']>0].sort_values('x')
            trace = go.Scatter(
                x=df['x'], 
                y=df['y'], 
                name=name,
                mode=mode,
                showlegend=True,
                marker=dict(size=3, opacity=0.5)
                )
            fig.add_trace(trace)   
        elif _type=='散点图':
            trace = go.Scatter(
                x=x_lst[i], 
                y=y_lst[i], 
                name=name,
                mode=mode,
                showlegend=True,
                marker=dict(size=3, opacity=0.5)
                )
            fig.add_trace(trace)
        elif _type=='时序图':
            for y, secondary_y in zip([y_lst[i], y2_lst[i]], [False, True]):
                if y is None or len(y)<1:
                    continue
                suffix = 'y' if secondary_y==False else 'y2'
                trace = go.Scatter(
                    x=x_lst[i], 
                    y=y, 
                    name='_'.join([name, suffix]),
                    mode=mode,
                    showlegend=True,
                    marker=dict(size=3, opacity=0.5)
                    )
                fig.add_trace(trace, secondary_y=secondary_y)
    if _type=='频谱图':
        for i in ref_freqs:
            fig.add_vline(
                x=i, 
                annotation_text=f"特征频率{i}",
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                )
    fig.update_xaxes(title_text=xtitle)
    fig.update_yaxes(title_text=ytitle)
    if y2title not in (None, ''):
        fig.update_yaxes(title_text=y2title, secondary_y=True)
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation='h',
            font=dict(
                    size=10,
                    color='black'
                ),
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1),
        )
    return fig