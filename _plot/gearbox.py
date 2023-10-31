# author luosz
# created on 10.23.2023

from wtbonline._plot.base import BaseFigure


class Gearbox(BaseFigure):
    '''
    >>> fig = Gearbox({'set_id':'20835', 'map_id':'A02', 'start_time':'2023-05-01', 'end_time':'2023-05-02'})
    >>> fig.plot()
    '''
    def _init(self):
        self.var_names = ['var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
         
if __name__ == "__main__":
    import doctest
    doctest.testmod()