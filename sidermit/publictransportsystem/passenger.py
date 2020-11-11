from __future__ import annotations

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
        "You must give a value > 0 for va"), docstring="Walking speed [km/h]")
    pv = passenger_property('_pv', operator.lt, PvIsNotValidExceptions(
        "You must give a value >= 0 for subjective pv"), docstring="Value of in-vehicle time savings [US$/h]")
    pw = passenger_property('_pw', operator.lt, PwIsNotValidExceptions(
        "You must give a value >= 0 for subjective  pw"), docstring="Value of waiting time savings [US$/h]")
    pa = passenger_property('_pa', operator.lt, PaIsNotValidExceptions(
        "You must give a value >= 0 for subjective  pa"), docstring="Value of access time savings [US$/h]")
    pt = passenger_property('_pt', operator.lt, PtIsNotValidExceptions(
        "You must give a value >= 0 for subjective  pt"), docstring="Pure transfer penalty [EIV]")
    spv = passenger_property('_spv', operator.lt, SpvIsNotValidExceptions(
        "You must give a value >= 0 for social pv"), docstring="Social value of in-vehicle time savings [US$/h]")
    spw = passenger_property('_spw', operator.lt, SpwIsNotValidExceptions(
        "You must give a value >= 0 for social pw"), docstring="Social value of waiting time savings [US$/h]")
    spa = passenger_property('_spa', operator.lt, SpaIsNotValidExceptions(
        "You must give a value >= 0 for social  pa"), docstring="Social value of access time savings [US$/h]")
    spt = passenger_property('_spt', operator.lt, SptIsNotValidExceptions(
        "You must give a value >= 0 for social pt"), docstring="Social pure transfer penalty [EIV]")

    def __init__(self, va: float, pv: float, pw: float, pa: float, pt: float,
                 spv: float, spw: float, spa: float, spt: float):
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
    def get_default_passenger() -> Passenger:
        """
        to get passenger with default values
        :return: Passenger
        """
        return Passenger(4.0, 2.74, 5.48, 8.22, 16, 2.74, 5.48, 8.22, 16)
