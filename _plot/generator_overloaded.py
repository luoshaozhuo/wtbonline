# author luosz
# created on 10.23.2023


import plotly.graph_objects as go

from wtbonline._plot.base import BaseFigure


class GeneratorOverloaded(BaseFigure):
    '''
    >>> govl = GeneratorOverloaded({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
    >>> govl.plot()
    '''
    def _init(self):
        self.var_names=['var_246']

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()