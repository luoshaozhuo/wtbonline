# author luosz
# created on 10.23.2023

from wtbonline._plot.classes.base import BaseFigure


class Convertor(BaseFigure):
    '''
    >>> fig = Convertor({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-05'})
    >>> fig.plot()
    '''
    def _init(self):
        self.var_names = ['var_15004', 'var_15005', 'var_15006', 'var_12016']

         
if __name__ == "__main__":
    import doctest
    doctest.testmod()