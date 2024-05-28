# # -*- coding: utf-8 -*-
# """
# Created on Thu May 11 06:01:43 2023

# @author: luosz

# 自动生成工作快报
# """

#%% import
from typing import Union
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter

from wtbonline._report.common import BRDocTemplate, add_page_templates, TEMP_DIR, LOGGER, PageBreak, Spacer, FRAME_WIDTH_LATER
from wtbonline._report.common import Paragraph, PS_HEADINGS, PS_BODY, build_tables, build_graph, PS_HEADING_1
from wtbonline._common.utils import make_sure_datetime, make_sure_dataframe, make_sure_list
from wtbonline._db.rsdb_facade import RSDBFacade
from wtbonline._db.postgres_facade import PGFacade
from wtbonline._common.utils import send_email
from wtbonline._logging import log_it

#%% class
class Base():
    '''
    >>> obj = Base()
    >>> outpath = '/mnt/d/'
    >>> set_id = '20080'
    >>> start_date = '2023-10-01'
    >>> end_date = '2024-04-01'
    >>> pathname = obj.build_report(set_id=set_id, start_date=start_date, end_date=end_date, outpath=outpath)
    >>> _ = obj.encrypt(pathname)
    '''
    
    def __init__(self, successors=[], title=''):
        self.successors = make_sure_list(successors)
        self.title = title
        self.RSDBFC = RSDBFacade()
    
    def _compose(self, index:str, heading:str, conclusion:str='', tables={}, graphs={}, temp_dir:str=None, width=1000, height=None):
        assert temp_dir is not None if (len(tables)>0 or len(graphs)>0) else True, '未指定临时目录'
        
        n = len(index.split('.'))-1
        rev = [] 
        if n==0:
            rev.append(Spacer(FRAME_WIDTH_LATER, 1))
        rev.append(Paragraph(heading, PS_HEADINGS[n]))
        if conclusion not in ('', None):
            rev.append(Paragraph(conclusion, PS_BODY))
        for key_ in tables:
            rev += build_tables(tables[key_], temp_dir=temp_dir, title=f'{key_}') 
        rev.append(Spacer(FRAME_WIDTH_LATER, 10))
        for key_ in graphs:
            rev.append(build_graph(graphs[key_], key_, f'{key_}.jpg', temp_dir=temp_dir, width=width, height=height))
        return rev
    
    def encrypt(self, pathname):
        pdf_reader = PdfReader(pathname)
        pdf_writer = PdfWriter()

        for page in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page])

        pdf_writer.encrypt('hzfd@00')
        pathname = Path(pathname)
        out_pathname = pathname.parent/(f'encrypted_{pathname.name}')
        with open(out_pathname, 'wb') as out:
            pdf_writer.write(out)
        return out_pathname
    
    def _build(self, set_id, start_date, end_date, temp_dir, index=''):
        if self.title not in ['', None]:
            n = len(index.split('.'))-1
            heading = f'{index} {self.title}'
            LOGGER.info(heading)
            return [Spacer(FRAME_WIDTH_LATER, 1), Paragraph(heading, PS_HEADINGS[n])]
        return []
    
    def build(self, set_id, start_date, end_date, temp_dir, index:str=''):
        rev = self._build(set_id, start_date, end_date, temp_dir, index=index)
        for i in range(len(self.successors)):
            idx = f'{i+1}' if index=='' else index+f'.{i+1}'
            rev += self.successors[i].build(set_id, start_date, end_date, temp_dir, index=idx)
        return rev
    
    @log_it(LOGGER)    
    def build_report(self, set_id:str, start_date:Union[str, date], end_date:Union[str, date], outpath:str):
        start_date = make_sure_datetime(start_date).date()
        end_date = make_sure_datetime(end_date).date()
        pathname = Path(outpath)/f'{set_id}_{start_date}_{end_date}.pdf'
        doc = BRDocTemplate(pathname.as_posix())
        add_page_templates(doc)
        with TemporaryDirectory(dir=TEMP_DIR.as_posix()) as temp_dir:
            doc.build(self.build(set_id, start_date, end_date, temp_dir)+[PageBreak()])
        return pathname
    
    @log_it(LOGGER)
    def email_report(self, pathname):  
        recv = self.RSDBFC.read_app_configuration(key_='email_address')['value'].iloc[0]
        account = self.RSDBFC.read_app_configuration(key_='email_account')['value'].iloc[0]
        farm_name = PGFacade().read_model_factory()['factory_name'].iloc[0]
        user_name, password, host, port = account.split('_')
        if recv not in [None, '']:
            send_email(recv, f'{farm_name}数据分析报告, {Path(pathname).name}', '请查阅附件。本邮件自动发送。', 
                    user_name, password, host, port, pathname=pathname)

#%% main
if __name__ == "__main__":
    import doctest
    doctest.testmod()