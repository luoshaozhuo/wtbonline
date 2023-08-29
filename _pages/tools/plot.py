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

