import unittest

from sidermit import exceptions
from sidermit.transport_mode import TransportMode, TransportModeManager


class test_graph(unittest.TestCase):

    def test_is_valid(self):
        """
        test is_valid method
        :return:
        """

        m = TransportModeManager()

        self.assertTrue(m.is_valid())

        m.delete_mode("bus")

        self.assertTrue(m.is_valid())

        m.delete_mode("metro")

        self.assertTrue(not m.is_valid())

    def test_raises_mode_exceptions(self):
        """
        to test mode class exceptions
        :return:
        """
        name = "bus"
        bya = 1
        co = 1
        c1 = 1
        c2 = 1
        v = 20
        t = 0.2
        fmax = 100
        kmax = 50
        theta = 0.5
        tat = 1
        d = 1

        with self.assertRaises(exceptions.NameIsNotValidExceptions):
            TransportMode(None, bya, co, c1, c2, v, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.ByaIsNotValidExceptions):
            TransportMode(name, -1, co, c1, c2, v, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.CoIsNotValidExceptions):
            TransportMode(name, bya, -2, c1, c2, v, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.C1IsNotValidExceptions):
            TransportMode(name, bya, co, None, c2, v, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.C2IsNotValidExceptions):
            TransportMode(name, bya, co, c1, -3, v, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.VIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, None, t, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.TIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, -3, fmax,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.FmaxIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, t, -200,
                                         kmax, theta, tat, d)
        with self.assertRaises(exceptions.KmaxIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, t, fmax,
                                         -100, theta, tat, d)
        with self.assertRaises(exceptions.ThetaIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, t, fmax,
                                         kmax, 2, tat, d)
        with self.assertRaises(exceptions.TatIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, t, fmax,
                                         kmax, theta, None, d)
        with self.assertRaises(exceptions.DIsNotValidExceptions):
            TransportMode(name, bya, co, c1, c2, v, t, fmax,
                                         kmax, theta, tat, -1)

    def test_get(self):
        """
        to test get methods
        :return:
        """
        m = TransportModeManager()

        self.assertEqual(len(m.get_modes()), 2)
        self.assertEqual(len(m.get_modes_names()), 2)
        self.assertTrue(
            isinstance(m.get_mode("bus"), TransportMode))

        with self.assertRaises(exceptions.ModeNotFoundExceptions):
            m.get_mode("train")

    def test_add_mode(self):
        """
        to test add_mode method
        :return:
        """
        m = TransportModeManager()

        name = "train"
        bya = 1
        co = 1
        c1 = 1
        c2 = 1
        v = 20
        t = 0.2
        fmax = 100
        kmax = 50
        theta = 0.5
        tat = 1
        d = 1

        m.add_mode(name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d)

        self.assertEqual(len(m.get_modes()), 3)

        with self.assertRaises(exceptions.AddModeExceptions):
            m.add_mode("bus", bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d)

    def test_delete_mode(self):
        """
        to test delete_mode method
        :return:
        """

        m = TransportModeManager()

        m.delete_mode("bus")
        self.assertEqual(len(m.get_modes()), 1)

        with self.assertRaises(exceptions.ModeDoesNotExistExceptions):
            m.delete_mode("train")

    def test_update_mode(self):
        """
        to test update_mode method
        :return:
        """
        m = TransportModeManager()

        m.update_mode("bus", v=1, theta=1, t=1, kmax=1, fmax=1, co=1, c1=1,
                      c2=1, tat=1, d=1, bya=1)
        self.assertEqual(len(m.get_modes()), 2)

        m.update_mode("metro")
        self.assertEqual(len(m.get_modes()), 2)

        with self.assertRaises(exceptions.ModeDoesNotExistExceptions):
            m.update_mode("train")


if __name__ == '__main__':
    unittest.main()
