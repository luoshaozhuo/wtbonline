import pandas as pd
import numpy as np

EPS = np.finfo(np.float32).eps

def make_sure_series(x):
    return pd.Series(x)