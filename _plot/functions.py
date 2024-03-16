import pstats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from collections.abc import Iterable
from typing import List

from wtbonline._common.utils import make_sure_list, make_sure_dataframe
# from wtbonline._common import utils
# from wtbonline._db.rsdb_facade import RSDBFacade
import wtbonline.configure as cfg
# from wtbonline._process.tools.frequency import power_spectrum, amplitude_spectrum
from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.tools.frequency import power_spectrum

# =============================================================================
# function
# =============================================================================
def ts_plot_stack(df, ycols, ytitles:List[str], *, xcol='ts', xtitle='时间', title='时序图', 
              refx=None, refy=None, row_height:int=200, showlegend=False):  
    ''' 并列单系列折线图 
    row_height : 单个子图的高度
    >>> cols = ['totalfaultbool', 'var_101', 'var_355']
    >>> df = TDFC.read(set_id='20835', device_id='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00', columns=cols)
    >>> graph = ts_plot_stack(df, cols, cols)
    >>> graph.show(renderer='svg')
    '''
    ytitles = make_sure_list(ycols)
    ycols = make_sure_list(ycols)
    assert len(ycols)==len(ytitles), f'每一个子图都应该有一个坐标title，ycols={ycols}, ytiltes={ytitles}'
    nrow = len(ycols)      
    line_chart = make_subplots(rows=nrow, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    if df[ycols].shape[0]<1:
        return line_chart
    
    for i in range(len(ycols)):
        line_chart.add_trace(
            go.Scatter(
                x=df[xcol], 
                y=df[ycols[i]],
                mode='lines+markers',           
                marker={'opacity':0.5, 'size':4}
                ),
            row=i+1, 
            col=1)
        if refx is not None and refy is not None:
            line_chart.add_trace(
                go.Scatter(
                    x=refx,
                    y=refy,
                    line=dict(color='black', dash='dash'),
                    mode='lines',
                    ),
                row=i+1,
                col=1,
                ) 
        line_chart.update_yaxes(title_text=ytitles[i], row=i+1, col=1)
    line_chart.update_xaxes(title_text=xtitle, row=nrow, col=1)
        
    line_chart.update_layout(
        title=dict(text=title, font=dict(size=15), xanchor='center', yanchor='top', x=0.5),
        height=row_height*len(ycols),
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
        margin=dict(l=20, r=20, t=20 if title in ('', None) else 50, b=20),
        hovermode="x unified"
        )
    line_chart.update_yaxes(showspikes=True)
    return line_chart

def scatter_matrix_plot_anomaly(df, columns:List[str], labels:List[str]=None, selectedpoints=[], title=''):
    '''
    >>> n=100
    >>> columns=['a', 'b', 'c', 'd']
    >>> df = pd.DataFrame(np.random.randn(n, 4), columns=columns)
    >>> df['is_suspector'] = np.random.choice([1,-1], size=n)
    >>> df['is_anomaly'] = np.random.choice([1,-1], size=n)
    >>> graph = scatter_matrix_plot_anomaly(df, columns, title='abc')
    >>> graph.show(renderer='svg')
    '''
    columns = make_sure_list(columns)
    labels = columns if labels is None else make_sure_list(labels)
    assert len(columns)==len(labels), 'columns与labels长度必须一致'
    fig = go.Figure()
    if df.shape[0]<1 or len(columns)<1:
        return fig
    
    idx_not_susptor= df[df['is_suspector']==-1].index
    idx_suspetor_without_label = df[(df['is_anomaly']==0) & (df['is_suspector']==1)].index
    idx_anormaly = df[df['is_anomaly']==1].index
    idx_not_anormaly = df[df['is_anomaly']==-1].index
    df.loc[idx_not_susptor, 'textd'] = '非离群'
    df.loc[idx_suspetor_without_label, 'textd'] ='离群，未标注'
    df.loc[idx_anormaly, 'textd'] = '异常'
    df.loc[idx_not_anormaly, 'textd'] = '正常'
    df.loc[idx_not_susptor, 'color'] = cfg.ANOMALY_MATRIX_PLOT_COLOR['非离群']
    df.loc[idx_suspetor_without_label, 'color'] = cfg.ANOMALY_MATRIX_PLOT_COLOR['离群，未标注']
    df.loc[idx_anormaly, 'color'] = cfg.ANOMALY_MATRIX_PLOT_COLOR['异常']
    df.loc[idx_not_anormaly, 'color'] = cfg.ANOMALY_MATRIX_PLOT_COLOR['正常']
    df.loc[idx_not_susptor, 'opacity'] = 0.2
    df.loc[idx_suspetor_without_label, 'opacity'] = 1
    df.loc[idx_anormaly, 'opacity'] = 1
    df.loc[idx_not_anormaly, 'opacity'] = 1 
    customdata = df['id'].to_list() if 'id' in df.columns else None
    
    dimensions = []
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
        title=dict(text=title, font=dict(size=15), xanchor='center', yanchor='top', x=0.5),
        clickmode='event+select',
        height=800,
        hovermode='closest',
        margin=dict(l=20, r=20, t=20 if title in ('', None) else 50, b=20),
        )
    
    return fig

def ts_plot_multiple_y(df, ycols:List[str], ytitles:List[str]=None,  xcol='ts', xtitle='时间', height=350, title=''):
    ''' 双y坐标
    >>> cols = ['totalfaultbool', 'var_101', 'var_355']
    >>> df = TDFC.read(set_id='20835', device_id='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00', columns=cols)
    >>> graph = ts_plot_multiple_y(df, ycols=cols)
    >>> graph.show(renderer='svg')
    '''
    df = make_sure_dataframe(df)
    ycols = make_sure_list(ycols)
    ytitles = ycols if ytitles is None else make_sure_list(ytitles)
    assert len(ycols)==len(ytitles), f'ycols must has the same length as ytitles if ytitles is not None'
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if df.shape[0]<1:
        return fig

    secondary_y = [False, True]
    N = min(len(ycols), 2)
    for i in range(N):
        fig.add_trace(
            go.Scatter(
                x=df[xcol],
                y=df[ycols[i]],
                mode='lines',
                name=ytitles[i],
                ),
            secondary_y=secondary_y[i],
            ) 
        fig.update_yaxes(title_text=ytitles[i], secondary_y=secondary_y[i])

    fig.update_xaxes(title_text=xtitle)
    fig.update_layout(
        title=dict(text=title, font=dict(size=15), xanchor='center', yanchor='top', x=0.5),
        height=height,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        clickmode='event+select',
        hovermode='x',
        margin=dict(l=20, r=20, t=20 if title in ('', None) else 50, b=20),
        )
    return fig
    
def spc_plot_multiple_y(df, ycols:List[str], ytitles:List[str]=None, ref_freqs=[], sample_spacing=1, height=500):
    ''' 双y坐标
    >>> cols = ['var_101', 'var_355']
    >>> df = TDFC.read(set_id='20835', device_id='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00', columns=cols)
    >>> graph = spc_plot_multiple_y(df, ycols=cols, ref_freqs=[0.1, 0.2])
    >>> graph.show(renderer='svg')
    '''
    df = make_sure_dataframe(df)
    ref_freqs = make_sure_list(ref_freqs)
    fft_df = pd.DataFrame()
    for i in range(min(len(ycols),2)):
        ycol = ycols[i]
        y_t = df[ycol] - df[ycol].mean()
        temp_df = power_spectrum(y_t, sample_spacing=sample_spacing)
        fft_df[ycol] = temp_df['amp']
    fft_df.insert(0, 'freq', temp_df['freq'])
    xtitle = 'Frequency Hz'
    fig = ts_plot_multiple_y(fft_df, fft_df.columns[1:], ytitles=ytitles, xcol='freq', xtitle=xtitle, title='功率谱', height=height)
    if len(ref_freqs)>0:
        for i, x in enumerate(ref_freqs):
            fig.add_vline(
                x=x, 
                annotation_text=f'{i+1}',
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                )
    return fig

# def get_simple_plot_parameters(xcol:str, ycol:str, y2col:str, plot_type:str, set_id:str):
#     point_name = pd.Series([xcol, ycol, y2col]).replace(['ts', '时间','频率'], None).dropna()
#     df = RSDBInterface.read_turbine_model_point(
#         set_id=set_id,
#         point_name=point_name,
#         select=None
#         ).drop_duplicates('point_name').set_index('point_name', drop=False)
#     assert len(df)==len(point_name), f'部分字段获取失败，需要{point_name.tolist()}，实际返回{df.index.tolist()}'
    
#     get_col = lambda x:None if x in [None, ''] else df.loc[x, 'var_name'].lower()
#     get_title = lambda x:None if x in [None, ''] else df.loc[x, 'point_name'] + '_' + df.loc[x, 'unit']
    
#     ytitle = get_title(ycol)
#     ycol = get_col(ycol)
#     y2title = get_title(y2col)
#     y2col = get_col(y2col)
#     if plot_type == '时序图':
#         xcol = 'ts'
#         xtitle = '时间'
#         mode = 'markers+lines'
#     elif plot_type in ('散点图', '极坐标图'):
#         xtitle = get_title(xcol)
#         xcol = get_col(xcol)
#         mode = 'markers'
#     elif plot_type == '频谱图':
#         xtitle = '频率 Hz'
#         xcol = 'ts'
#         mode = 'markers+lines'
#     else:
#         raise ValueError(f'不支持此种图形类别：{plot_type}')
    
#     return xcol, xtitle, ycol, ytitle, y2col, y2title, mode

# def get_simple_plot_selections(set_id, plot_type):
#     model_point_df = RSDBInterface.read_turbine_model_point(
#         set_id=set_id,
#         columns=['point_name', 'unit', 'set_id', 'datatype'],
#         select=[0,1]
#         )
#     if plot_type=='时序图':
#         x_data = ['时间']
#         x_value = '时间'
#         y_data = model_point_df['point_name']
#         y_value = None
#     elif plot_type=='散点图':
#         x_data = model_point_df['point_name']
#         x_value = None
#         y_data = model_point_df['point_name']
#         y_value = None
#     elif plot_type=='极坐标图':
#         x_data = model_point_df['point_name'][
#                     (model_point_df['point_name'].str.find('角')>-1) & 
#                     (model_point_df['unit']=='°')
#                     ]
#         x_value = None
#         y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
#         y_value = None    
#     elif plot_type=='频谱图':
#         x_data = ['频率']
#         x_value = '频率'
#         y_data = model_point_df[model_point_df['datatype']=='F']['point_name']
#         y_value = None
#     x_data = [{'value':i, 'label':i} for i in x_data]
#     y_data = [{'value':i, 'label':i} for i in y_data]
#     return x_data, x_value, y_data, y_value

def simple_plot(
    df,
    xcol:str=None, 
    ycol:str=None, 
    xtitle:str=None,
    ytitle:str=None, 
    type_:str='散点图', 
    vlines:List[float]=[], 
    hlines:List[float]=[], 
    title:str=None,
    sample_spacing=1,
    height=300
    ):
    '''
    type_ : ['极坐标图', '频谱图', '散点图', '时序图']
    >>> cols = ['var_101', 'var_355', 'var_18006']
    >>> df = TDFC.read(set_id='20835', device_id='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00', columns=cols)
    >>> graph = simple_plot(df, xcol='var_101', ycol='var_355', type_='散点图')
    >>> graph.show(renderer='svg')
    >>> graph = simple_plot(df, xcol='ts', ycol='var_355', type_='时序图')
    >>> graph.show(renderer='svg')
    >>> graph = simple_plot(df, ycol='var_355', type_='频谱图', vlines=[0.1,0.2])
    >>> graph.show(renderer='svg')
    >>> graph = simple_plot(df, xcol='var_18006', ycol='var_355', type_='极坐标图')
    >>> graph.show(renderer='svg')
    '''
    xcol = 'ts' if xcol is None else xcol
    assert ycol is not None, '必须指定ycol'
    xtitle = xcol if xtitle is None else xtitle
    ytitle = ycol if ytitle is None else ytitle
    fig = make_subplots()
    if type_=='极坐标图':
        trace = go.Scatterpolar(
            theta=df[xcol], 
            r=df[ycol],
            mode='markers',
            showlegend=True,
            marker=dict(size=3, opacity=0.5)
            )
        fig.add_trace(trace)
    elif type_=='频谱图':
        fft_df = power_spectrum(df[ycol], sample_spacing=sample_spacing)
        fft_df = fft_df[fft_df['freq']>0]
        trace = go.Scatter(
            x=fft_df['freq'], 
            y=fft_df['amp'], 
            mode='lines+markers',
            showlegend=True,
            marker=dict(size=3, opacity=0.5)
            )
        fig.add_trace(trace)   
        xtitle='Frequency Hz'
    elif type_=='散点图':
        trace = go.Scatter(
            x=df[xcol],  
            y=df[ycol], 
            mode='markers',
            showlegend=True,
            marker=dict(size=3, opacity=0.5)
            )
        fig.add_trace(trace)
    elif type_=='时序图':
        trace = go.Scatter(
            x=df[xcol],  
            y=df[ycol], 
            mode='lines+markers',
            showlegend=True,
            marker=dict(size=3, opacity=0.5)
            )
        fig.add_trace(trace)   
    
    fig.update_xaxes(title_text=xtitle)
    fig.update_yaxes(title_text=ytitle)
    
    if type_ != '极坐标图':
        for i,y in enumerate(hlines): 
            fig.add_hline(
                y=y, 
                annotation_text=f"{i+1}",
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                ) 
        for i,x in enumerate(vlines): 
            fig.add_vline(
                x=x, 
                annotation_text=f"{i+1}",
                annotation_font_size=10, 
                line_width=1, 
                line_dash="dash", 
                line_color="green"
                )    

    fig.update_layout(
        title=dict(text=title, font=dict(size=15), xanchor='center', yanchor='top', x=0.5),
        height=height,
        showlegend=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        clickmode='event+select',
        hovermode='x',
        margin=dict(l=20, r=20, t=20 if title in ('', None) else 50, b=20),
        )
    return fig

# %%
if __name__ == "__main__":
    import doctest
    doctest.testmod()