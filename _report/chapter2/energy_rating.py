# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff

from wtbonline._report.common import LOGGER, standard
from wtbonline._report.base import Base
from wtbonline._db.tsdb_facade import TDFC

#%% class
class EnergyRating(Base):
    '''
    >>> obj = Base(successors=[EnergyRating()])
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathanme = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    '''
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        title = '发电量排名'
        heading = f'{index} {title}'
        conclusion = ''
        tables = {}
        graphs = {}
        LOGGER.info(heading)
        
        df = TDFC.read(
            set_id=set_id, 
            device_id=None, 
            start_time=start_date, 
            end_time=end_date,
            groupby='device', 
            columns={'totalenergy':['first', 'last']},
            remote=True)

        df['发电量（kWh）'] = df['totalenergy_last'] - df['totalenergy_first']
        df = df.sort_values('发电量（kWh）', ascending=False)
        df = standard(set_id, df)

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
            fig.layout.update({'title': f'{start_date}至{end_date}累积发电量'})
            graphs.update({f'排名{i*10+1}至{i*10+10}':fig})

        return self._compose(index, heading, conclusion, tables, graphs, temp_dir)
        
#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()