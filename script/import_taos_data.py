'''
luosz
2024-04-02
修改taos2导出的数据文件内容，并生成导入sql
'''

#%%
from pathlib import Path
import pandas as pd

#%% constant
SRC_PATH = Path('/home/d/BaiduNetdiskDownload/bb') # sql语句里面的csv文件路径
OUT_PATH = Path('/mnt/d/BaiduNetdiskDownload/bb') # insert_data.sql文件输出路径
DBNAME = 'scada'

#%% fcuntion
def remove_header(pathname):
    df = pd.read_csv(pathname)
    pathname.unlink()
    df = df.fillna('NULL')
    df.to_csv(pathname, header=False, index=False)    

def main(src_path=SRC_PATH, out_path=OUT_PATH):
    sql = []
    for path in src_path.iterdir():
        if not path.is_dir():
            continue
        device_id = path.name
        print(device_id)
        for pathname in path.rglob('*.csv'):
            with open(pathname) as f:
                header = f.readline()
            if header.find('ts')>-1:
                remove_header(pathname)
            sql.append(f"insert into {DBNAME}.d_{device_id} file '{src_path/device_id/pathname.name}';")
    pd.Series(sql).to_csv(out_path/'insert_data.sql', index=False, header=False)

#%% main
if __name__ == '__main__':
    main()
        
