from wtbonline._db.tsdb_facade import TDFC
from wtbonline._process.preprocess import _LOGGER

def init_tdengine(*args, **kwargs):
    TDFC.init_database()
    
# %%
if __name__ == "__main__":
    init_tdengine()