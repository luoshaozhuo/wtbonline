# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from wtbonline._report.common import LOGGER, DEVICE_DF, build_table_from_sketch, POINT_DF
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC

#%% constant

#%% class
class Anomaly(Base):
    '''
    >>> obj = Base(successors=[Anomaly(om_id=3)])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20835'
    >>> start_date = '2023-08-01'
    >>> end_date = '2023-10-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    def __init__(self, successors=[], title='', om_id:str=None):
        assert om_id is not None, '必须指定turbine_outlier_monitor的记录id'
        self.om_id = om_id
        super().__init__(successors, title)
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        sr = self.RSDBFC.read_turbine_outlier_monitor(id_=self.om_id).squeeze()
        system = sr["system"]
        if len(sr)==0:
            raise ValueError(f'turbine_outlier_monitor 无id={self.om_id}的记录')
        title = f'{system}关键参数异常值'
        heading = f'{index} {title}'
        conclusion = ''
        df = None
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        # 分析涉及的变量
        var_names = pd.Series(pd.Series(sr.var_names.split(',')).unique())
        cols = var_names[var_names.isin(TDFC.get_filed(set_id, remote=True))]
        if len(cols)==0:
            raise ValueError(f'tdengine里没有以下字段中任何一个:{var_names}')
        var_names = cols.tolist()
        
        # 原始数据
        # 使用tdengine对莱州的d_s10005机组var_15041字段进行PERCENTILE计算时会报InvalidChunkLength错误
        # 因此转而先获取分段原始数据的mean值，再用pandas对其进行quantile计算
        columns = {i:['avg', 'max', 'min'] for i in var_names}
        raw_df = []
        for device_id in DEVICE_DF['device_id']:
            try:
                temp = TDFC.read(set_id=set_id, device_id=device_id, columns=columns, interval='30m', start_time=start_date, end_time=end_date, remote=True)
            except ValueError as e:
                if str(e).find('"code":866')>-1:
                    continue
                raise
            temp.insert(0, 'device_id', device_id)
            if len(temp)>0:
                raw_df.append(temp)
        if len(raw_df)<0:
            conclusion = f'报告周期内没有查询到任何数据，不能完成本章节分析。'
            return self._compose(index, heading, conclusion, tbl_df, graphs, temp_dir)   
        raw_df = pd.concat(raw_df, ignore_index=True)
        
        dct = {}
        for i in var_names:
            dct.update({f'{i}_3iqr':pd.NamedAgg(column=f'{i}_avg', aggfunc=lambda x:3*(x.quantile(0.75)-x.quantile(0.25)))})
            dct.update({f'{i}_median':pd.NamedAgg(column=f'{i}_avg', aggfunc='median')})
            dct.update({f'{i}_max':pd.NamedAgg(column=f'{i}_max', aggfunc='max')})
            dct.update({f'{i}_min':pd.NamedAgg(column=f'{i}_min', aggfunc='min')})
        stat_df = raw_df.groupby('device_id').agg(**dct)
        stat_df.index = DEVICE_DF.loc[stat_df.index, 'device_name']     
        stat_df = stat_df.reset_index()
        
        # 生成表格
        point_names = POINT_DF[POINT_DF['set_id']==set_id].set_index('var_name')['point_name']
        columns = ['机组编号', '3倍四分位距', '中位数', '最大值', '最小值']
        for i in range(len(var_names)):
            vars = [f'{var_names[i]}_{suffix}' for suffix in ['3iqr', 'median', 'max', 'min']]
            sub_df = stat_df.loc[:, ['device_name']+vars].copy()
            upper_bound = sub_df[vars[1]] + sub_df[vars[0]]
            lower_bound = sub_df[vars[1]] - sub_df[vars[0]]
            highlight_rows = sub_df[(sub_df[vars[2]]>upper_bound) | (sub_df[vars[3]]<lower_bound)].index 
            sub_df.columns = columns
            rs = build_table_from_sketch(sub_df, f'{index}.{i+1} {point_names[var_names[i]]}离群值识别结果', highlight_rows=highlight_rows)
            if len(rs)>0:
                graphs.update(rs)
        
        # 绘图
        n = len(var_names)  
        colors = px.colors.qualitative.Dark2
        point_sub = POINT_DF[POINT_DF['set_id']==set_id].set_index('var_name')
        k=1
        for device_id,grp in raw_df.groupby('device_id'):
            device_name = DEVICE_DF.loc[device_id, 'device_name']
            # 一台机组一张图，每张图由n个子图构成
            fig = make_subplots(int(n/3)+1, min(3,n), horizontal_spacing=0.1)
            for i in range(n):
                vars = [f'{var_names[i]}_{suffix}' for suffix in ['3iqr', 'median', 'max', 'min']]
                point_name = '_'.join(point_sub.loc[var_names[i], ['point_name', 'unit']])
                sr = stat_df[stat_df['device_name']==device_name].squeeze()
                upper_bound = sr[vars[1]] + sr[vars[0]]
                lower_bound = sr[vars[1]] - sr[vars[0]]
                row=int(i/3)+1
                col=i%3+1
                for i,color in [(vars[2], colors[2]), (vars[3], colors[5])]:
                    fig.add_trace(
                        go.Scatter(
                            x=grp['ts'], 
                            y=grp[i],
                            mode='lines+markers',           
                            marker={'opacity':0.5, 'size':2, 'color':color},
                            line={'color':color},
                            ),
                        row=row,
                        col=col
                        )
                    fig.update_yaxes(title_text=point_name, row=row, col=col)
                for y,text in [(upper_bound,'上限'),(lower_bound, '下限')]:
                    fig.add_hline(
                        y=y, 
                        annotation_text=text,
                        annotation_font_size=10, 
                        line_width=1, 
                        line_dash="dash", 
                        line_color="red",
                        row=row,
                        col=col
                        ) 
            fig.update_xaxes(title_text='时间', row=1, col=1)
            fig.update_layout(
                showlegend=False,
                width=1000, 
                height=200*(int(n/3)+1),
                margin=dict(l=20, r=20, t=20 if title in ('', None) else 70, b=20)
                )
            graphs.update({f'图 {index}.{k} {device_name}各关键变量最小最大值时序':fig})
            k += 1
            
        # 总结
        conclusion = f'以每一台机组的{system}的关键参数的中值的±3倍四分位距为边界，识别离群数据，结果如下面的表格所示。'
        return self._compose(index, heading, conclusion, tables, graphs, temp_dir) 
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()