#%% import
import pandas as pd

#%% function
# def stationary(df):
#     condtion = df['pv_c']<0.001
#     idxes = df[condtion].index
#     return idxes

# def not_limit_power(df):
#     condtion = (df['limitpowbool_mode']=='False') & (df['limitpowbool_nunique']==1)
#     idxes = df[condtion].index
#     return idxes

# def in_power_generating_mode(df):
#     condtion = (df['workmode_mode']=='32') & (df['workmode_nunique']==1)
#     idxes = df[condtion].index
#     return idxes

# def no_fault(df):
#     condtion = (df['totalfaultbool_mode']=='False') & (df['totalfaultbool_nunique']==1)
#     idxes = df[condtion].index
#     return idxes   

# def on_grid(df):
#     condtion = (df['ongrid_mode']=='True') & (df['ongrid_nunique']==1)
#     idxes = df[condtion].index
#     return idxes         

def stationary(df):
    return df['pv_c']<0.001

def not_limit_power(df):
    return (df['limitpowbool_mode']=='False') & (df['limitpowbool_nunique']==1)

def in_power_generating_mode(df):
    return (df['workmode_mode']=='32') & (df['workmode_nunique']==1)

def no_fault(df):
    return  (df['totalfaultbool_mode']=='False') & (df['totalfaultbool_nunique']==1)

def on_grid(df):
    return(df['ongrid_mode']=='True') & (df['ongrid_nunique']==1)  

def filter_for_modeling(df, reset_index=False, return_cond=False):
    cond_df = pd.DataFrame()
    cond_df.insert(0, 'is_stationary', stationary(df))
    cond_df.insert(0, 'not_limit_power', not_limit_power(df))
    cond_df.insert(0, 'in_power_generating_mode', in_power_generating_mode(df))
    cond_df.insert(0, 'no_fault', no_fault(df))
    cond_df.insert(0, 'on_grid', on_grid(df))
    # 这里不可以reset_index，模型predict时需要保留index信息
    rev = df[cond_df.all(axis=1)]
    if reset_index==True:
        rev.reset_index(drop=True, inplace=True)
    if return_cond:
        return rev, return_cond
    return rev 