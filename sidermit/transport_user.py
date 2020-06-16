from sidermit.exceptions import *


class User:
    def __init__(self, va, pv, pw, pa, pt, spv, spw, spa, spt):

        if self.parameters_validator(va, pv, pw, pa, pt, spv, spw, spa, spt):
            self.va = va
            self.pv = pv
            self.pw = pw
            self.pa = pa
            self.pt = pa
            self.spv = spv
            self.spw = spw
            self.spa = spa
            self.spt = spt

    @staticmethod
    def parameters_validator(va, pv, pw, pa, pt, spv, spw, spa, spt):
        """
        to validate parameters
        :param spw:
        :param spv:
        :param spt:
        :param spa:
        :param pw:
        :param pv:
        :param pt:
        :param pa:
        :param va:
        :return:
        """

        if va is None or va <= 0:
            raise VaIsNotValidExceptions("You must give a value > 0 for va")
        if pv is None or pv < 0:
            raise PvIsNotValidExceptions("You must give a value >= 0 for pv")
        if pw is None or pw < 0:
            raise PwIsNotValidExceptions("You must give a value >= 0 for pw")
        if pa is None or pa < 0:
            raise PaIsNotValidExceptions("You must give a value >= 0 for pa")
        if pt is None or pt < 0:
            raise PtIsNotValidExceptions("You must give a value >= 0 for pt")
        if spv is None or spv < 0:
            raise SpvIsNotValidExceptions("You must give a value >= 0 for spv")
        if spw is None or spw < 0:
            raise SpwIsNotValidExceptions("You must give a value >= 0 for spw")
        if spa is None or spa < 0:
            raise SpaIsNotValidExceptions("You must give a value >= 0 for spa")
        if spt is None or spt < 0:
            raise SptIsNotValidExceptions("You must give a value >= 0 for spt")

        return True


class TransportUser:

    def __init__(self, add_default_user=True):
        self.__user = None
        if add_default_user:
            # default user
            self.__user = User(4.0, 2.74, 5.48, 8.22, 0.73, 2.74, 5.48, 8.22, 0.73)

    def get_user(self):
        """
        to get user
        :return:
        """
        return self.__user

    def update_user(self, va=None, pv=None, pw=None, pa=None, pt=None, spv=None, spw=None, spa=None, spt=None):
        """
        to update user information
        :param va:
        :param pv:
        :param pw:
        :param pa:
        :param pt:
        :param spv:
        :param spw:
        :param spa:
        :param spt:
        :return:
        """
        if va is None:
            va = self.__user.va
        if pv is None:
            pv = self.__user.pv
        if pw is None:
            pw = self.__user.pw
        if pa is None:
            pa = self.__user.pa
        if pt is None:
            pt = self.__user.pt
        if spv is None:
            spv = self.__user.spv
        if spw is None:
            spw = self.__user.spw
        if spa is None:
            spa = self.__user.spa
        if spt is None:
            spt = self.__user.spt

        u = User(va, pv, pw, pa, pt, spv, spw, spa, spt)

        self.__user = u
