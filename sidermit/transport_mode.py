from sidermit.exceptions import *


class Mode:
    def __init__(self, name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d):

        if self.parameters_validator(name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d):
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
    def parameters_validator(name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d):
        """
        to validate parameters
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

        if name is None:
            raise nameIsNotValidExceptions("You must give a name")
        if bya is None:
            raise ByaIsNotValidExceptions("You must give a value for bya")
        if co is None or co < 0:
            raise CoIsNotValidExceptions("You must give a value >=0 for co")
        if c1 is None or c1 < 0:
            raise C1IsNotValidExceptions("You must give a value >=0 for c1")
        if c2 is None or c2 < 0:
            raise C2IsNotValidExceptions("You must give a value >=0 for c2")
        if v is None or v < 0:
            raise VIsNotValidExceptions("You must give a value >=0 for v")
        if t is None or t < 0:
            raise TIsNotValidExceptions("You must give a value >=0 for t")
        if fmax is None or fmax < 0:
            raise FmaxIsNotValidExceptions("You must give a value >=0 for fmax")
        if kmax is None or kmax < 0:
            raise KmaxIsNotValidExceptions("You must give a vale >=0 for kmax")
        if theta is None or theta < 0 or theta > 1:
            raise ThetaIsNotValidExceptions("You must give a value between [0-1] for theta")
        if tat is None or tat < 0:
            raise TatIsNotValidExceptions("You must give a value >=0 for tat")
        if d is None or d < 0:
            raise DIsNotValidExceptions("You must give a value >=0 for d")
        return True


class Transport_mode:
    def __init__(self):
        self.__list_name = []
        self.__modes = []
        # default bus
        bus = Mode("bus", 1, 8.61, 0.15, 0, 20, 2.5, 150, 160, 0.7, 0, 6)
        # default metro
        metro = Mode("metro", 0, 80.91, 0.3, 933.15, 40, 0.33, 40, 1440, 0.5, 1, 1)

        self.__modes.append(bus)
        self.__list_name.append("bus")
        self.__modes.append(metro)
        self.__list_name.append("metro")

    def is_valid(self):
        """
        to check that there is at least one way
        :return:
        """
        if len(self.__modes) >= 1:
            return True
        else:
            return False

    def get_mode(self, name):
        """
        to get a specific mode
        :param name:
        :return:
        """

    def get_modes(self):
        """
        to get modes
        :return:
        """
        return self.__modes

    def get_names_modes(self):
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

        mode = Mode(name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d)
        self.__modes.append(mode)

    def delete_mode(self, name):
        """
        to delete a mode
        :param name:
        :return:
        """
        if name in self.__list_name:
            self.__list_name.remove(name)
            modes = []
            for mode in self.__modes:
                if mode.name == name:
                    continue
                else:
                    modes.append(mode)
            self.__modes = modes
        else:
            raise ModeDoesNotExistExceptions("Mode does not exist")
