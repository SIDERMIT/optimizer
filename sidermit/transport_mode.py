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
            raise NameIsNotValidExceptions("You must give a name")
        if bya is None or bya not in [0, 1]:
            raise ByaIsNotValidExceptions("You must give a value for bya")
        if co is None or co < 0:
            raise CoIsNotValidExceptions("You must give a value >=0 for co")
        if c1 is None or c1 < 0:
            raise C1IsNotValidExceptions("You must give a value >=0 for c1")
        if c2 is None or c2 < 0:
            raise C2IsNotValidExceptions("You must give a value >=0 for c2")
        if v is None or v <= 0:
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


class TransportMode:
    def __init__(self, add_default_mode=True):

        self.__list_name = []
        self.__modes = []
        if add_default_mode:
            # default bus
            bus = Mode("bus", 1, 8.61, 0.15, 0, 20, 2.5, 150, 160, 0.7, 0, 6)
            # default metro
            metro = Mode("metro", 0, 80.91, 0.3, 933.15, 40, 0.33, 40, 1440, 0.5, 1, 1)
            self.__modes.append(bus)
            self.__list_name.append("bus")
            self.__modes.append(metro)
            self.__list_name.append("metro")

    def update_mode(self, name, bya=None, co=None, c1=None, c2=None, v=None, t=None, fmax=None, kmax=None, theta=None,
                    tat=None, d=None):
        """
        to update information about a mode
        :param v:
        :param theta:
        :param t:
        :param kmax:
        :param fmax:
        :param co:
        :param c2:
        :param c1:
        :param tat:
        :param d:
        :param bya:
        :param name:
        :return:
        """

        if name not in self.__list_name:
            raise ModeDoesNotExistExceptions("mode name does not exist")
        else:
            i = self.__list_name.index(name)
            mode = self.__modes[i]

            if bya is None:
                bya = mode.bya
            if co is None:
                co = mode.co
            if c1 is None:
                c1 = mode.c1
            if c2 is None:
                c2 = mode.c2
            if v is None:
                v = mode.v
            if t is None:
                t = mode.t
            if fmax is None:
                fmax = mode.fmax
            if kmax is None:
                kmax = mode.kmax
            if theta is None:
                theta = mode.theta
            if tat is None:
                tat = mode.tat
            if d is None:
                d = mode.d

            m = Mode(mode.name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d)
            self.__modes[i] = m

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
