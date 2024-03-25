import inspect
import importlib
from pathlib import Path

from wtbonline._plot import classes as graph_classes

class Graph_Factory:
    '''
    >>> _ = Graph_Factory().available_keys()
    >>> Graph_Factory().get('Spectrum')
    <class 'wtbonline._plot.classes.spectrum.Spectrum'>
    >>> Graph_Factory().get('ordinary')
    <class 'wtbonline._plot.classes.base.Base'>
    >>> Graph_Factory().get('abc')
    Traceback (most recent call last):
    ...
    KeyError: 'abc'
    '''
    def __init__(self):
        self._mapping = self._get_table_mapping()
    
    def _get_table_mapping(self):
        rev = {}
        for i in Path(graph_classes.__path__[0]).glob('*.py'):
            pakage_name = i.name[:-3]
            module = importlib.import_module('.'.join([graph_classes.__name__, pakage_name]))
            for name,obj in inspect.getmembers(module, inspect.isclass):
                rev.update({name:obj})
        return rev

    def available_keys(self):
        return list(self._mapping.keys())

    def get(self, name):
        if name=='ordinary':
            return self._mapping['Base']
        return self._mapping[name]

graph_factory = Graph_Factory()
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()