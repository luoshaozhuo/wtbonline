'''
luosz
2024.04.03

验证字段是否有效，手段：
1、超出阈值
2、冗余字段间可相互印证
'''

#%% import

#%% function
def _validate(df, col1, col2, atol, rtol, _min=None, _max=None) -> int:
    ''' 检测是否超出阈值
    atol : float
        绝对阈值
    rtol : float
        相对阈值
    _min : float
        最小值
    _max : float
        最大值
    return : int, 1 或 0
        1=超出阈值
    '''
    rev = 0
    if col1 in df.columns and col2 in df.columns:
        if rtol != None:
            diff = abs(df[col1].median() - df[col2].median())
            ref =  abs(df[col1].median())
            rev = rev if diff<ref*rtol else 1
        if atol != None:
            diff = (df[col1].rolling(10).mean() - df[col2].rolling(10).mean()).abs().max()
            rev = rev if diff<atol else 1
        if _min != None:
            rev = rev if rev>=_min else 1
        if _max != None:
            rev = rev if rev<=_max else 1
    return rev

def validate_measurement(df, gearbox_ratio) -> int:
    ''' 利用冗余传感器验证测量数据 
    十进制数的每一位代表一个检测项目，对应位为1表示此项检测不通过，全0表示所有检测通过
    '''
    df = df.copy()
    df['rptspd'] = df['var_94']*gearbox_ratio
    if 'var_2732' in df.columns:
        df['torque'] = df['var_2732']*2
    rev = 0
    # var_101 1#叶片实际角度, var_104 1#叶片冗余变桨角度
    rev += _validate(df, 'var_101', 'var_104', 2, None)
    # var_102 2#叶片实际角度, var_105 1#叶片冗余变桨角度
    rev += _validate(df, 'var_102', 'var_105', 2, None)*10
    # var_103 3#叶片实际角度, var_106 1#叶片冗余变桨角度
    rev += _validate(df, 'var_103', 'var_106', 2, None)*100
    # var_355 1#风速计瞬时风速, var_356 2#风速计瞬时风速
    rev += _validate(df, 'var_355', 'var_356', None, 0.1, 0, 100)*1000
    # var_226 发电机转矩, var_2732 变频器1发电机转矩
    rev += _validate(df, 'var_226', 'torque', None, 0.05)*10000
    # , var_2731 变频器1发电机转速反馈, var_94 风轮转速
    rev += _validate(df, 'var_2731', 'rptspd', None, 0.05)*100000
    return rev