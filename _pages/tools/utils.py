
import pandas as pd

from wtbonline._db.rsdb_interface import RSDBInterface
from wtbonline._db.tsdb_facade import TDFC 
from wtbonline._db.common import make_sure_list
from wtbonline._process.modelling import data_filter

def mapid_to_tid(set_id, map_id):
    df = RSDBInterface.read_windfarm_configuration(
        set_id=set_id, 
        map_id=map_id,
        )
    assert df.shape[0]>0, f'{map_id}找不到对应的turbine_id'
    return df['turbine_id'].iloc[0]

def available_variable(set_id):
    df = RSDBInterface.read_turbine_model_point(
        set_id=set_id, 
        columns=['var_name', 'point_name', 'datatype'],
        select=1
        )
    df['var_name'] = df['var_name'].str.lower()
    df.drop_duplicates()
    rev_all = [{'label':i['point_name'], 'value':i['var_name']} for _,i in df.iterrows()]
    rev_all += [{'label':'', 'value':''}]
    df = df[df['datatype']=='F']
    rev_float = [{'label':i['point_name'], 'value':i['var_name']} for _,i in df.iterrows()]
    rev_float += [{'label':'', 'value':''}]
    return rev_all, rev_float

def var_name_to_point_name(set_id, var_name=None, point_name=None):
    var_name = make_sure_list(var_name)
    point_name = make_sure_list(point_name)
    assert len(var_name)>0 or len(point_name)>0
    
    df = RSDBInterface.read_turbine_model_point(
        set_id=set_id, 
        columns=['var_name', 'point_name', 'datatype'],
        select=1
        )
    df['var_name'] = df['var_name'].str.lower()
    df.drop_duplicates()
    
    if len(var_name)>0:
        df = df.set_index('var_name')
        rev = df.loc[var_name]['point_name'].tolist()
    else:
        df = df.set_index('point_name')
        rev = df.loc[point_name]['var_name'].tolist()
    return rev

def read_sample_ts(sample_id, var_name):
    '''
    >>> sample_id=2342
    >>> point_name = ['var_355', 'var_101']
    >>> _ = read_sample_ts(sample_id, point_name)
    '''
    columns = ['set_id', 'turbine_id', 'bin']
    sample =  RSDBInterface.read_statistics_sample(
        id_=sample_id, 
        columns=columns
        ).squeeze()
    df,point_df = TDFC.read(
        set_id=sample['set_id'],
        turbine_id=sample['turbine_id'],
        start_time=sample['bin'],
        end_time=sample['bin']+pd.Timedelta('10m'),
        var_name= pd.Series(make_sure_list(var_name)).dropna()
        )
    return df, point_df

def read_scatter_matrix_anormaly(set_id, *, turbine_id=None, map_id=None, columns=None, sample_cnt=5000):
    assert columns is not None
    turbine_id = turbine_id if turbine_id is not None else mapid_to_tid(set_id, map_id)
    columns_aug = [
        'id', 'set_id', 'turbine_id', 'pv_c', 'validation',
        'limitpowbool_mode' ,'limitpowbool_nunique',
        'workmode_mode', 'workmode_nunique',
        'totalfaultbool_mode', 'totalfaultbool_nunique',
        ]
    df = RSDBInterface.read_statistics_sample(
        set_id=set_id, turbine_id=turbine_id, columns=columns+columns_aug,
        ).set_index('id', drop=False)
    df = data_filter(df)[columns+['id']]
    
    df.insert(0, 'is_anormaly', 0)
    idx = RSDBInterface.read_model_anormaly(
        set_id=set_id, turbine_id=turbine_id
        ).drop_duplicates('sample_id')['sample_id']
    idx = idx[idx.isin(df.index)]
    df.loc[idx, 'is_anormaly'] = 1
    
    sub_normal = df[df['is_anormaly']==0]
    sub_normal = sub_normal.sample(sample_cnt) if sub_normal.shape[0]>sample_cnt else sub_normal
    sub_anormal = df[df['is_anormaly']==1]
    df = pd.concat([sub_normal, sub_anormal], ignore_index=True)
    return df

def read_anormaly_without_label(set_id, turbine_id=None, map_id=None, labeled=False):
    '''
    >>> set_id = '20835'
    >>> turbine_id = 's10001'
    >>> _ = read_anormaly_without_label(set_id, turbine_id)
    '''
    turbine_id = turbine_id if turbine_id is not None else mapid_to_tid(set_id, map_id)
    rev = RSDBInterface.read_model_anormaly(
        set_id=set_id, turbine_id=turbine_id
        ).drop_duplicates('sample_id')
    if labeled == False:
        df = (
            RSDBInterface.read_model_label(set_id=set_id, turbine_id=turbine_id)
                .drop_duplicates('sample_id')
            )
        rev = rev[~rev['sample_id'].isin(df['sample_id'])]
    return rev

def read_sample_label(sample_id):
    sr = RSDBInterface.read_model_label(sample_id=sample_id).squeeze()
    if len(sr)<1:
        rev = 0
    else:
        rev = sr['is_anormaly']
    return rev

if __name__ == "__main__":
    import doctest
    doctest.testmod()