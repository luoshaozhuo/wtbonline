'''
luosz
2024-05-23
删除scada库中部分字段。这些字段不包含在最新导出csv文件中。
否则，从csv文件导入数据会报错。
'''

import pandas as pd
from wtbonline._db.tsdb_facade import TDFC

SRC_PATHNAME = '/mnt/d/BaiduNetdiskDownload/luo/home/luo/s10003/2023-10-09.csv'

def main(pathname=SRC_PATHNAME):
    df = pd.read_csv(pathname)
    fields = TDFC.get_filed(set_id='20835', remote=True)
    columns = fields[~fields.isin(df.columns)]
    for i in columns:
        rs = TDFC.query(f'ALTER TABLE scada.s_20835 DROP COLUMN {i};', remote=True)
        print(i, rs)
    print(len(fields), len(TDFC.get_filed(set_id='20835', remote=True)))

if __name__ == '__main__':
    main()