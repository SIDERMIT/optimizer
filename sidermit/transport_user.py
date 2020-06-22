import operator

from sidermit.exceptions import VaIsNotValidExceptions, \
    PvIsNotValidExceptions, PwIsNotValidExceptions, PaIsNotValidExceptions, \
    PtIsNotValidExceptions, SpvIsNotValidExceptions, SpwIsNotValidExceptions, \
    SpaIsNotValidExceptions, SptIsNotValidExceptions


def passenger_property(property_name, comp_function, exception_instance,
                       docstring=None):
    def getter(self):
        return self.__getattribute__(property_name)

    def setter(self, new_value):
        if new_value is None or comp_function(new_value, 0):
            raise exception_instance
        self.__setattr__(property_name, new_value)

    return property(getter, setter, doc=docstring)


class Passenger:
    va = passenger_property('_va', operator.le, VaIsNotValidExceptions(
        "You must give a value > 0 for va"))
    pv = passenger_property('_pv', operator.lt, PvIsNotValidExceptions(
        "You must give a value >= 0 for pv"))
    pw = passenger_property('_pw', operator.lt, PwIsNotValidExceptions(
        "You must give a value >= 0 for pw"))
    pa = passenger_property('_pa', operator.lt, PaIsNotValidExceptions(
        "You must give a value >= 0 for pa"))
    pt = passenger_property('_pt', operator.lt, PtIsNotValidExceptions(
        "You must give a value >= 0 for pt"))
    spv = passenger_property('_spv', operator.lt, SpvIsNotValidExceptions(
        "You must give a value >= 0 for spv"))
    spw = passenger_property('_spw', operator.lt, SpwIsNotValidExceptions(
        "You must give a value >= 0 for spw"))
    spa = passenger_property('_spa', operator.lt, SpaIsNotValidExceptions(
        "You must give a value >= 0 for spa"))
    spt = passenger_property('_spt', operator.lt, SptIsNotValidExceptions(
        "You must give a value >= 0 for spt"))

    def __init__(self, va: float, pv: float, pw: float, pa: float, pt: float,
                 spv: float, spw: float, spa: float, spt: float) -> None:
        self.va = va
        self.pv = pv
        self.pw = pw
        self.pa = pa
        self.pt = pt
        self.spv = spv
        self.spw = spw
        self.spa = spa
        self.spt = spt

    @staticmethod
    def get_default_passenger():
        return Passenger(4.0, 2.74, 5.48, 8.22, 0.73, 2.74, 5.48, 8.22, 0.73)
