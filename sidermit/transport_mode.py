from __future__ import annotations

import operator
from typing import List

from sidermit.exceptions import CoIsNotValidExceptions, \
    C1IsNotValidExceptions, C2IsNotValidExceptions, VIsNotValidExceptions, \
    TIsNotValidExceptions, FmaxIsNotValidExceptions, \
    NameIsNotValidExceptions, KmaxIsNotValidExceptions, \
    TatIsNotValidExceptions, DIsNotValidExceptions, ByaIsNotValidExceptions, \
    ThetaIsNotValidExceptions, ModeDoesNotExistExceptions, \
    ModeNotFoundExceptions, AddModeExceptions


def mode_property(property_name, comp_function, exception_instance,
                  docstring=None):
    def getter(self):
        return self.__getattribute__(property_name)

    def setter(self, new_value):
        if new_value is None or comp_function(new_value, 0):
            raise exception_instance
        self.__setattr__(property_name, new_value)

    return property(getter, setter, doc=docstring)


class TransportMode:
    name = property(operator.attrgetter('_name'))
    bya = property(operator.attrgetter('_bya'))
    co = mode_property('_co', operator.lt, CoIsNotValidExceptions(
        "You must give a value >=0 for co"))
    c1 = mode_property('_c1', operator.lt, C1IsNotValidExceptions(
        "You must give a value >=0 for c1"))
    c2 = mode_property('_c2', operator.lt, C2IsNotValidExceptions(
        "You must give a value >=0 for c2"))
    v = mode_property('_v', operator.le, VIsNotValidExceptions(
        "You must give a value >=0 for v"))
    t = mode_property('_t', operator.lt, TIsNotValidExceptions(
        "You must give a value >=0 for t"))
    fmax = mode_property('_fmax', operator.lt, FmaxIsNotValidExceptions(
        "You must give a value >=0 for fmax"))
    kmax = mode_property('_kmax', operator.lt, KmaxIsNotValidExceptions(
        "You must give a vale >=0 for kmax"))
    theta = property(operator.attrgetter('_theta'))
    tat = mode_property('_tat', operator.lt, TatIsNotValidExceptions(
        "You must give a value >=0 for tat"))
    d = mode_property('_d', operator.lt, DIsNotValidExceptions(
        "You must give a value >=0 for d"))

    @name.setter
    def name(self, value):
        if value is None:
            raise NameIsNotValidExceptions("You must give a name")
        self._name = value

    @bya.setter
    def bya(self, value):
        if value is None or value not in [0, 1]:
            raise ByaIsNotValidExceptions(
                "You must give a valid value for bya")
        self._bya = value

    @theta.setter
    def theta(self, value):
        if value is None or value < 0 or value > 1:
            raise ThetaIsNotValidExceptions(
                "You must give a value between [0-1] for theta")
        self._theta = value

    def __init__(self, name: str, bya: float, co: float, c1: float, c2: float,
                 v: float, t: float, fmax: float, kmax: float, theta: float,
                 tat: float, d: float):
        self.name = name
        self.bya = bya
        self.co = co
        self.c1 = c1
        self.c2 = c2
        self.v = v
        self.t = t
        self.fmax = fmax
        self.kmax = kmax
        self.theta = theta
        self.tat = tat
        self.d = d

    @staticmethod
    def get_default_modes() -> List[TransportMode]:
        bus_transport_mode = TransportMode("bus", 1, 8.61, 0.15, 0, 20, 2.5,
                                           150, 160, 0.7, 0, 6)
        metro_transport_mode = TransportMode("metro", 0, 80.91, 0.3, 933.15,
                                             40, 0.33, 40, 1440, 0.5, 1, 1)

        return [bus_transport_mode, metro_transport_mode]


class TransportModeManager:
    def __init__(self, add_default_mode=True):
        self.__list_name = []
        self.__modes = []
        if add_default_mode:
            bus_obj, metro_obj = TransportMode.get_default_modes()
            self.__modes.append(bus_obj)
            self.__list_name.append(bus_obj.name)
            self.__modes.append(metro_obj)
            self.__list_name.append(metro_obj.name)

    def update_mode(self, name, **kwargs):
        """
        to update mode attributes
        :param name:
        :return:
        """

        if name not in self.__list_name:
            raise ModeDoesNotExistExceptions("mode name does not exist")

        i = self.__list_name.index(name)
        mode_obj = self.__modes[i]
        for attr in kwargs:
            setattr(mode_obj, attr, kwargs[attr])

    def is_valid(self):
        """
        to check that there is at least one way
        :return:
        """
        return len(self.__modes) >= 1

    def get_mode(self, name):
        """
        to get a specific mode
        :param name:
        :return:
        """
        if name not in self.__list_name:
            raise ModeNotFoundExceptions("name mode not found")
        else:
            i = self.__list_name.index(name)
            mode = self.__modes[i]
            return mode

    def get_modes(self):
        """
        to get modes
        :return:
        """
        return self.__modes

    def get_modes_names(self):
        """
        to get list_name of modes
        :return:
        """
        return self.__list_name

    def add_mode(self, name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d):
        """
        to add a new mode
        :param name:
        :param bya:
        :param co:
        :param c1:
        :param c2:
        :param v:
        :param t:
        :param fmax:
        :param kmax:
        :param theta:
        :param tat:
        :param d:
        :return:
        """
        if name in self.__list_name:
            raise AddModeExceptions("mode name exists, try with other name")

        mode = TransportMode(name, bya, co, c1, c2, v, t, fmax, kmax, theta,
                             tat, d)
        self.__modes.append(mode)
        self.__list_name.append(name)

    def delete_mode(self, name):
        """
        to delete a mode
        :param name:
        :return:
        """

        if name in self.__list_name:
            i = self.__list_name.index(name)
            self.__list_name.pop(i)
            self.__modes.pop(i)
        else:
            raise ModeDoesNotExistExceptions("Mode does not exist")
