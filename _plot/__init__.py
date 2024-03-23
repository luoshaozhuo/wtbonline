from wtbonline._plot.classes.blade_asynchronous import BladeAsynchronous
from wtbonline._plot.classes.blade_overloaded import BladeOverloaded
from wtbonline._plot.classes.blade_pitchkick import BladePitchkick
from wtbonline._plot.classes.blade_unbalanced_load import BladeUnblacedLoad 
from wtbonline._plot.classes.generator_overloaded import GeneratorOverloaded
from wtbonline._plot.classes.hub_azimuth import HubAzimuth
from wtbonline._plot.classes.powercurve import PowerCurve
from wtbonline._plot.classes.power_compare import PowerCompare
from wtbonline._plot.classes.gearbox import Gearbox
from wtbonline._plot.classes.convertor import Convertor
from wtbonline._plot.classes.base import Base
from wtbonline._db.rsdb_facade import RSDBFacade

_GRAPH = dict(
    bladeAsynchronous=BladeAsynchronous,
    bladeOverloaded=BladeOverloaded,
    bladePitchkick=BladePitchkick,
    bladeUnblacedLoad=BladeUnblacedLoad,
    generatorOverloaded=GeneratorOverloaded,
    hubAzimuth=HubAzimuth,
    powerCurve=PowerCurve,
    powerCompare=PowerCompare,
    gearbox=Gearbox,
    convertor=Convertor,
    )

def graph_factory(graph):
    return _GRAPH.get(graph, Base)

# def graph_factory(cause=None):
#     '''
#     >>> type(graph_factory('发电机关键参数超限'))
#     <class 'wtbonline._plot.classes.base.Base'>
#     >>> type(graph_factory('叶片pitchkick'))
#     <class 'wtbonline._plot.classes.blade_pitchkick.BladePitchkick'>
#     '''
#     sr = RSDBFacade.read_turbine_fault_type(cause=cause).iloc[0].squeeze()
#     rev =  _GRAPH.get(sr['graph'], Base)()
#     if rev == Base:
#         var_names=(sr['var_names'].str.split(',', expand=True)).str.strip()
#         rev = rev.init(var_names=var_names)
#     return rev
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()