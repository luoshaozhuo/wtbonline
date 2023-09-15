# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 18:50:01 2023

@author: luosz

绘图函数
"""
# =============================================================================
# import
# =============================================================================
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from collections.abc import Iterable
from typing import List, Union, Optional

from wtbonline._pages.tools.utils import var_name_to_point_name
from wtbonline._db.common import make_sure_list, make_sure_dataframe

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

def scatter_matrix_anormaly(df=None, columns=None, set_id=None, selectedpoints=[]):
    columns = make_sure_list(columns)
    fig = go.Figure()
    if df is not None and set_id is not None and len(columns)>0:
        idx = df[df['is_anormaly']==1].index
        df['textd'] ='正常'
        df.loc[idx, 'textd'] = '离群'
        df['color'] = 'gray'
        df.loc[idx, 'color'] = 'red'
        df['opacity'] = 0.2
        df.loc[idx, 'opacity'] = 1
        
        dimensions = []
        labels = var_name_to_point_name(
            set_id=set_id, 
            var_name=tuple(pd.Series(columns).str.replace('_mean', ''))
            )
        for col, label in zip(columns, labels):
            if col=='is_anormaly' or col=='id':
                continue
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
                customdata =df['id'],
                selected={'marker':{'color':'cyan', 'opacity':1, 'size':6}},
                diagonal=dict(visible=False),
                selectedpoints=selectedpoints
                )
            )
    fig.update_layout(
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
                if 'x' in (df.columns) or ref_col is None:
                    continue
                freq_ref = df[ref_col].abs().mean()
                freq_ref = freq_ref/60 if freq_ref>0 else 1
                df['x'] = x_fft if ref_col is None else x_fft/freq_ref
    if 'x' in (df.columns):
        df = df[df['x']>0]
    else:
        df = pd.DataFrame(columns=df.columns.tolist()+['x'])
    xtitle = '转频倍率'
    fig = ts_plot_multiple_y(df, ycols, [f'({i})^2' for i in units], ytitles=ytitles, x='x', xtitle=xtitle)
    if 'x' in (df.columns) and df.shape[0]>1:
        for i in range(int(min(df['x'].max(), 10))):
            fig.add_vline(
                x=i+1, 
                annotation_text=f"{i+1}倍频",
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                )
    return fig

def simple_plot(
        *, 
        x_lst:List[List[float]]=[],
        y_lst:List[List[float]]=[], 
        xtitle:str='', 
        ytitle:str='', 
        name_lst:List[str]=[],
        mode:str='markers+lines',
        _type:str='scatter',
        ref_freqs:List[float]=None,
        ):
    name_lst = make_sure_list(name_lst)
    ref_freqs = make_sure_list(ref_freqs)
    fig = go.Figure()
    for i, name in enumerate(name_lst):
        if _type=='polar':
            trace = go.Scatterpolar(
                theta=x_lst[i], 
                r=y_lst[i],
                name=name,
                mode=mode,
                showlegend=True,
                marker=dict(size=3, opacity=0.5)
                )
        elif _type=='spectrum':
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
        elif _type=='scatter':
            trace = go.Scatter(
                x=x_lst[i], 
                y=y_lst[i], 
                name=name,
                mode=mode,
                showlegend=True,
                marker=dict(size=3, opacity=0.5)
                )
        fig.add_trace(trace)
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
    fig.update_layout(
        height=700,
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
        
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()
    