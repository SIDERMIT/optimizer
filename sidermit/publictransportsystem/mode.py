# from __future__ import annotations

import operator

from sidermit.exceptions import CoIsNotValidExceptions, \
    C1IsNotValidExceptions, C2IsNotValidExceptions, VIsNotValidExceptions, \
    TIsNotValidExceptions, FmaxIsNotValidExceptions, \
    NameIsNotValidExceptions, KmaxIsNotValidExceptions, \
    TatIsNotValidExceptions, DIsNotValidExceptions, ByaIsNotValidExceptions, \
    ThetaIsNotValidExceptions, ModeDoesNotExistExceptions, \
    ModeNotFoundExceptions, AddModeExceptions, ModeIsNotValidException


# from typing import List


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
    name = property(operator.attrgetter('_name'), doc="Name transport mode")
    bya = property(operator.attrgetter('_bya'),
                   doc="1 if passengers simultaneously get on and off the means of transport. 0 if they do it sequentially")
    co = mode_property('_co', operator.lt, CoIsNotValidExceptions(
        "You must give a value >=0 for co"), docstring="Unitary cost per vehicle per period of time [US$/h-veh]")
    c1 = mode_property('_c1', operator.lt, C1IsNotValidExceptions(
        "You must give a value >=0 for c1"), docstring="Unitary cost per seat per period of time [US$/h-veh]")
    c2 = mode_property('_c2', operator.lt, C2IsNotValidExceptions(
        "You must give a value >=0 for c2"), docstring="Unitary cost per vehicle per km of time [US$/h-veh]")
    v = mode_property('_v', operator.le, VIsNotValidExceptions(
        "You must give a value >=0 for v"), docstring="Cruise speed [km/h]")
    t = mode_property('_t', operator.lt, TIsNotValidExceptions(
        "You must give a value >=0 for t"), docstring="Boarding and alighting time [s/pax]")
    fmax = mode_property('_fmax', operator.lt, FmaxIsNotValidExceptions(
        "You must give a value >=0 for fmax"), docstring="Maximum frequency [veh/h]")
    kmax = mode_property('_kmax', operator.lt, KmaxIsNotValidExceptions(
        "You must give a vale >=0 for kmax"), docstring="Maximum vehicle size [pax/veh]")
    theta = property(operator.attrgetter('_theta'), doc="regularity of arrival of the mode of transport at the stops")
    tat = mode_property('_tat', operator.lt, TatIsNotValidExceptions(
        "You must give a value >=0 for tat"), docstring="Technological access time [min]")
    d = mode_property('_d', operator.lt, DIsNotValidExceptions(
        "You must give a value >=0 for d"), docstring="Parallel lines")

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

    def __init__(self, name: str, bya: int, co: float, c1: float, c2: float,
                 v: float, t: float, fmax: float, kmax: float, theta: float,
                 tat: float, d: int):
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
    def get_default_modes():  # -> List[TransportMode]:
        """
        to get bus and metro mode of transport with default values
        :return: List[TransportMode]
        """
        bus_transport_mode = TransportMode("bus", 1, 8.61, 0.15, 0, 20, 2.5,
                                           150, 160, 0.7, 0, 6)
        metro_transport_mode = TransportMode("metro", 0, 80.91, 0.3, 933.15,
                                             40, 0.33, 40, 1440, 0.5, 1, 1)

        return [bus_transport_mode, metro_transport_mode]


class TransportModeManager:
    def __init__(self, add_default_mode=True):
        """
        transport mode manager
        :param add_default_mode: (default: True) True to initialize list of modes with bus and metro with
         default values. False to initialize list of modes empty
        """

        self.__list_name = []
        self.__modes = []
        if add_default_mode:
            bus_obj, metro_obj = TransportMode.get_default_modes()
            self.__modes.append(bus_obj)
            self.__list_name.append(bus_obj.name)
            self.__modes.append(metro_obj)
            self.__list_name.append(metro_obj.name)

    def is_valid_to_assignment_step(self):
        """
        to check that list of modes is valid to optimization. There should be only one or two transport mode.
        If there are two transport mode, one of them must have parameter d equal to 1
        :return: True if list of mode is valid to assignment step, False if not.
        """
        if len(self.__modes) == 1:
            return True

        if len(self.__modes) == 2:
            for mode in self.__modes:
                if mode.d == 1:
                    return True
        return False

    def get_mode(self, name):
        """
        to get a specific mode by name
        :param name: mode name
        :return: TransportMode
        """
        if name not in self.__list_name:
            raise ModeNotFoundExceptions("name mode not found")
        else:
            i = self.__list_name.index(name)
            mode = self.__modes[i]
            return mode

    def get_modes(self):
        """
        to get all modes
        :return: List[TransportMode]
        """
        return self.__modes

    def get_modes_names(self):
        """
        to get list_name of modes
        :return: List[names]
        """
        return self.__list_name

    def add_mode(self, mode_obj):
        """
        to add a new mode
        :param mode_obj: TransportMode
        :return:
        """
        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode_obj is not valid")

        if mode_obj.name in self.__list_name:
            raise AddModeExceptions("mode name exists, try with other name")

        self.__modes.append(mode_obj)
        self.__list_name.append(mode_obj.name)

    def remove_mode(self, name):
        """
        to delete a mode by name
        :param name: mode name
        :return:
        """

        if name in self.__list_name:
            i = self.__list_name.index(name)
            self.__list_name.pop(i)
            self.__modes.pop(i)
        else:
            raise ModeDoesNotExistExceptions("Mode does not exist")
