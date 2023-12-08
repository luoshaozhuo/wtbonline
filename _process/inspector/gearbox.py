from wtbonline._process.inspector.base import BaseInspector

class GearBoxInspector(BaseInspector):
    '''
    >>> GearBoxInspector().inspect('20835', 's10002', '2023-08-01', '2023-09-01')
    '''
    def _initalize(self):
        self.var_names = ['var_175', 'var_182', 'var_2713', 'var_2714', 'var_2715']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '齿轮箱关键参数超限'