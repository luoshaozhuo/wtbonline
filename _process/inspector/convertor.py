from wtbonline._process.inspector.base import BaseInspector

class ConvertorInspector(BaseInspector):
    '''
    >>> ConvertorInspector().inspect('20835', 's10001', '2023-08-01', '2023-09-01')
    '''
    def _initalize(self):
        self.var_names = ['var_15004', 'var_15005', 'var_15006', 'var_12016']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '变流器关键参数超限'   