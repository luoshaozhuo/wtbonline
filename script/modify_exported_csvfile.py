'''
luosz
2024-04-02
修改taos2导出的数据文件内容，包括删除表头以及删除scada库中没有的字段。
'''

#%%
from pathlib import Path
import pandas as pd
from wtbonline._db.tsdb_facade import TDFC

#%% constant
SRC_PATH = Path('/mnt/d/BaiduNetdiskDownload/home/luo/s10003') # csv文件路径

#%% fcuntion
def remove_header(pathname):
    df = pd.read_csv(pathname)
    pathname.unlink()
    df = df.fillna('NULL')
    df.to_csv(pathname, header=False, index=False)    

def get_reserved_columns(df):
    fields = TDFC.get_filed(set_id='20835', remote=True)
    columns = df.columns[df.columns.isin(fields)]
    return columns

def main(src_path=SRC_PATH):
    columns = None
    for pathname in src_path.rglob('*.csv'):
        with open(pathname) as file:
            line = file.readline()
        if not line.find('ts')>-1:
            print(f'skip {pathname}')
            continue 
        print(pathname)
        df = pd.read_csv(pathname, dtype=object).fillna('NULL')
        if columns is None:
            columns = TDFC.get_filed(set_id='20835', remote=True).iloc[:-1]
        df[columns].to_csv(pathname, index=False, header=False)

#%% main
if __name__ == '__main__':
    main()
        
