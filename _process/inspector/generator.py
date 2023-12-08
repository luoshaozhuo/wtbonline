
from wtbonline._process.inspector.base import BaseInspector

class GeneratorInspector(BaseInspector):
    def _initalize(self):
        self.var_names = ['var_206', 'var_207', 'var_208', 'var_209', 'var_210', 'var_211']
        self.vars_bound = self.var_names
        self.funcs = ['max', 'min']
        self.name = '发电机关键参数超限'

