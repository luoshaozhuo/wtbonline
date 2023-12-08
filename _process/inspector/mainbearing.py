from wtbonline._process.inspector.base import BaseInspector

class MainBearingInspector(BaseInspector):
    def _initalize(self):
        self.var_names = ['var_171', 'var_172', 'abs(var_171-var_172)']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '主轴承关键参数超限'