'''
luosz
2024-04-02
并生成导入sql
'''

#%%
from pathlib import Path
import pandas as pd

#%% constant
SRC_PATH = Path('/mnt/d/ll/data/lz') # csv文件路径
OUT_PATH = Path('/mnt/d/ll/data/lz') # insert_data.sql文件输出路径
SQL_PATH = Path('/home/d/ll/data/lz') # sql 语句里的csv路径
DBNAME = 'scada'
TB_PREFIX = 'd_s'

#%% fcuntion
def remove_header(pathname):
    df = pd.read_csv(pathname)
    pathname.unlink()
    df = df.fillna('NULL')
    df.to_csv(pathname, header=False, index=False)    

def main(src_path=SRC_PATH, out_path=OUT_PATH, sql_path=SQL_PATH):
    sql = []
    for path in src_path.iterdir():
        if not path.is_dir():
            continue
        device_id = path.name
        print(device_id)
        for pathname in path.rglob('*.csv'):
            sql.append(f"insert into {DBNAME}.{TB_PREFIX}{device_id} file '{sql_path/device_id/pathname.name}';")
    pd.Series(sql).to_csv(out_path/'insert_data.sql', index=False, header=False)

#%% main
if __name__ == '__main__':
    main()
        
