from wtbonline._db.tsdb_facade import TDFC
from wtbonline._logging import log_it
from wtbonline._process.preprocess import _LOGGER

@log_it(_LOGGER, True)
def init_tdengine(*args, **kwargs):
    TDFC.init_database()
    
# %%
if __name__ == "__main__":
    init_tdengine()