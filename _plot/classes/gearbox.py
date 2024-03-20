# author luosz
# created on 10.23.2023

from wtbonline._plot.classes.base import Base


class Gearbox(Base):
    '''
    >>> gb = Gearbox()
    >>> fig = gb.plot(set_id='20835', device_ids='s10003', start_time='2023-05-01 00:00:00', end_time='2023-05-01 00:30:00')
    >>> fig.show(renderer='png')
    '''
    
    def init(self, var_names=[]):
        self.var_names = ['var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
        self.height = 900
        self.width = 900
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()