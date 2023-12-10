from wtbonline._process.inspector.gearbox import GearBoxInspector
from wtbonline._process.inspector.mainbearing import MainBearingInspector
from wtbonline._process.inspector.generator import GeneratorInspector
from wtbonline._process.inspector.convertor import ConvertorInspector
from wtbonline._process.inspector.bladeunbalanceLoad import BladeUnbalanceLoadInspector
from wtbonline._process.inspector.bladeAsynchronous import BladeAsynchronousInspector
from wtbonline._process.inspector.bladeEdgewiseOverLoaded import BladeEdgewiseOverLoadedInspector
from wtbonline._process.inspector.bladeFlapwiseOverLoaded import BladeFlapwiseOverLoadedInspector
from wtbonline._process.inspector.bladePitchkick import BladePitchkickInspector
from wtbonline._process.inspector.hubAzimuth import HubAzimuthInspector
from wtbonline._process.inspector.overPower import OverPowerInspector

INSPECTORS = {
    'gearbox':GearBoxInspector(),
    'mainbearing':MainBearingInspector(),
    'generator':GeneratorInspector(),
    'convertor':ConvertorInspector(),
    'blade_unbalance_load':BladeUnbalanceLoadInspector(),
    'blade_asynchronous':BladeAsynchronousInspector(),
    'blade_edgewise_overloaded':BladeEdgewiseOverLoadedInspector(),
    'blade_flapwise_overloaded':BladeFlapwiseOverLoadedInspector(),
    'blade_pitchkick':BladePitchkickInspector(),
    'hub_azimuth':HubAzimuthInspector(),
    'over_power':OverPowerInspector()
    }