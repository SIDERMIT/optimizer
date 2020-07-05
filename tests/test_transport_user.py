import unittest

from sidermit import exceptions
from sidermit.publictransportsystem import Passenger


class PassengerTest(unittest.TestCase):

    def test_create_passenger(self):
        """

        """
        va = 1
        pv = 2
        pw = 3
        pa = 4
        pt = 5
        spv = 6
        spw = 7
        spa = 8
        spt = 9

        passenger_obj = Passenger(va, pv, pw, pa, pt, spv, spw, spa, spt)

        self.assertEqual(passenger_obj.va, va)
        self.assertEqual(passenger_obj.pv, pv)
        self.assertEqual(passenger_obj.pw, pw)
        self.assertEqual(passenger_obj.pa, pa)
        self.assertEqual(passenger_obj.pt, pt)
        self.assertEqual(passenger_obj.spv, spv)
        self.assertEqual(passenger_obj.spw, spw)
        self.assertEqual(passenger_obj.spa, spa)
        self.assertEqual(passenger_obj.spt, spt)

    def test_raises_user_exceptions(self):
        """
        test user exceptions
        :return:
        """

        with self.assertRaises(exceptions.VaIsNotValidExceptions):
            Passenger(0, 1, 1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PvIsNotValidExceptions):
            Passenger(1, -1, 1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PwIsNotValidExceptions):
            Passenger(1, 1, -1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PaIsNotValidExceptions):
            Passenger(1, 1, 1, -1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PtIsNotValidExceptions):
            Passenger(1, 1, 1, 1, -1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.SpvIsNotValidExceptions):
            Passenger(1, 1, 1, 1, 1, -1, 1, 1, 1)
        with self.assertRaises(exceptions.SpwIsNotValidExceptions):
            Passenger(1, 1, 1, 1, 1, 1, -1, 1, 1)
        with self.assertRaises(exceptions.SpaIsNotValidExceptions):
            Passenger(1, 1, 1, 1, 1, 1, 1, -1, 1)
        with self.assertRaises(exceptions.SptIsNotValidExceptions):
            Passenger(1, 1, 1, 1, 1, 1, 1, 1, -1)

    def test_get_default_passenger(self):
        passenger_obj = Passenger.get_default_passenger()

        self.assertEqual(passenger_obj.va, 4.0)
        self.assertEqual(passenger_obj.pv, 2.74)
        self.assertEqual(passenger_obj.pw, 5.48)
        self.assertEqual(passenger_obj.pa, 8.22)
        self.assertEqual(passenger_obj.pt, 16)
        self.assertEqual(passenger_obj.spv, 2.74)
        self.assertEqual(passenger_obj.spw, 5.48)
        self.assertEqual(passenger_obj.spa, 8.22)
        self.assertEqual(passenger_obj.spt, 16)
