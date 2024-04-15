'''
luosz
2024-04-02
修改taos2导出的数据文件内容
'''

#%%
from pathlib import Path
import pandas as pd

#%% constant
SRC_PATH = Path('/mnt/d/ll/data/lz/10034') # csv文件路径

#%% fcuntion
def remove_header(pathname):
    df = pd.read_csv(pathname)
    pathname.unlink()
    df = df.fillna('NULL')
    df.to_csv(pathname, header=False, index=False)    

def main(src_path=SRC_PATH):
    for pathname in src_path.rglob('*.csv'):
        print(pathname)
        with open(pathname) as f:
            header = f.readline()
        if header.find('ts')>-1:
            remove_header(pathname)


#%% main
if __name__ == '__main__':
    main()
        
