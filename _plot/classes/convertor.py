# author luosz
# created on 10.23.2023

from wtbonline._plot.classes.base import Base


class Convertor(Base):
    '''
    >>> cvt = Convertor()
    >>> fig = cvt.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''
    def init(self):
        self.var_names = ['var_15004', 'var_15005', 'var_15006', 'var_12016']
        self.height = 800
        self.width = 900
         
if __name__ == "__main__":
    import doctest
    doctest.testmod()