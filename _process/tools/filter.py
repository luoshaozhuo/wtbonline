#%% import

#%% function
def stationary(df):
    condtion = df['pv_c']<0.001
    idxes = df[condtion].index
    return idxes

def not_limit_power(df):
    condtion = (df['limitpowbool_mode']=='False') & (df['limitpowbool_nunique']==1)
    idxes = df[condtion].index
    return idxes

def in_power_generating_mode(df):
    condtion = (df['workmode_mode']=='32') & (df['workmode_nunique']==1)
    idxes = df[condtion].index
    return idxes

def no_fault(df):
    condtion = (df['totalfaultbool_mode']=='False') & (df['totalfaultbool_nunique']==1)
    idxes = df[condtion].index
    return idxes   

def on_grid(df):
    condtion = (df['ongrid_mode']=='True') & (df['ongrid_nunique']==1)
    idxes = df[condtion].index
    return idxes      

def verified(df):
    condtion = df['validation']==0
    idxes = df[condtion].index
    return idxes    

def filter_for_modeling(df, reset_index=False):
    idxes = stationary(df)
    idxes = not_limit_power(df.loc[idxes])
    idxes = in_power_generating_mode(df.loc[idxes])
    idxes = no_fault(df.loc[idxes])
    idxes = on_grid(df.loc[idxes])
    idxes = verified(df.loc[idxes])
    # 这里不可以reset_index，模型predict时需要保留index信息
    rev = df.loc[idxes]
    if reset_index==True:
        rev.reset_index(drop=True, inplace=True)
    return rev