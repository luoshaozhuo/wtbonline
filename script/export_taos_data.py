'''
luosz
2024-04-02
生成导出sql
'''

#%%
from pathlib import Path
import pandas as pd

#%% constant
SRC_PATH = Path('/home/luo') # sql语句里面的csv文件输出路径
OUT_PATH = Path('/mnt/d/BaiduNetdiskDownload/zq/taos') # export.sql文件输出路径
DATE_START = pd.to_datetime('2023-12-11').date()
DATE_END = pd.Timestamp.now().date() # 作闭右开
DBNAME = 'scada'
TB_PREFIX = 'd_d'
DEVICE_ID_START = 1
DEVICE_ID_END = 60  # 闭区间
DIGIT = 5

#%% fcuntion
def main(src_path=SRC_PATH, out_path=OUT_PATH, date_start=DATE_START, date_end=DATE_END, id_start=DEVICE_ID_START, id_end=DEVICE_ID_END, prefix=TB_PREFIX, dbname=DBNAME):
    sql = []
    for i in range(id_start, id_end+1):
        device_id = f'{i:05d}'
        for dt in pd.date_range(date_start, date_end, inclusive='left'):
            sql.append(f'''select * from {dbname}.{prefix}{device_id} where ts>='{dt}' and ts<'{dt+pd.Timedelta('1d')}' >> {src_path/device_id/str(dt)}.csv;''') 
    pd.Series(sql).to_csv(out_path/'export.sql', index=False, header=False)

#%% main
if __name__ == '__main__':
    main()
        
