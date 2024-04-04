
#%% import
from wtbonline._logging import get_logger
from wtbonline._process.model.classifier.anomaly import Anomaly

#%% constant
_LOGGER = get_logger('model')

def model_factory(type_, **kwargs):
    if type_=='anomaly':
        return Anomaly(**kwargs)
    raise ValueError(f'not supported type {type_}')