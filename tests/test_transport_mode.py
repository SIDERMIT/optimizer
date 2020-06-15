import os
import unittest

from sidermit import transport_mode
from sidermit import exceptions


class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'transport_mode')

    def test_is_valid(self):
        """
        test is_valid method
        :return:
        """

        m = transport_mode.Transport_mode()

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
            transport_mode.Mode(None, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.ByaIsNotValidExceptions):
            transport_mode.Mode(name, -1, co, c1, c2, v, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.CoIsNotValidExceptions):
            transport_mode.Mode(name, bya, -2, c1, c2, v, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.C1IsNotValidExceptions):
            transport_mode.Mode(name, bya, co, None, c2, v, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.C2IsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, -3, v, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.VIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, None, t, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.TIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, -3, fmax, kmax, theta, tat, d)
        with self.assertRaises(exceptions.FmaxIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, t, -200, kmax, theta, tat, d)
        with self.assertRaises(exceptions.KmaxIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, t, fmax, -100, theta, tat, d)
        with self.assertRaises(exceptions.ThetaIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, t, fmax, kmax, 2, tat, d)
        with self.assertRaises(exceptions.TatIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, t, fmax, kmax, theta, None, d)
        with self.assertRaises(exceptions.DIsNotValidExceptions):
            transport_mode.Mode(name, bya, co, c1, c2, v, t, fmax, kmax, theta, tat, -1)

    def test_get(self):
        """
        to test get methods
        :return:
        """
        m = transport_mode.Transport_mode()

        self.assertEqual(len(m.get_modes()), 2)
        self.assertEqual(len(m.get_names_modes()), 2)
        self.assertTrue(isinstance(m.get_mode("bus"), transport_mode.Mode))

        with self.assertRaises(exceptions.ModeNotFoundExceptions):
            m.get_mode("train")

    def test_add_mode(self):
        """
        to test add_mode method
        :return:
        """
        m = transport_mode.Transport_mode()

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

        m = transport_mode.Transport_mode()

        m.delete_mode("bus")
        self.assertEqual(len(m.get_modes()), 1)

        with self.assertRaises(exceptions.ModeDoesNotExistExceptions):
            m.delete_mode("train")


if __name__ == '__main__':
    unittest.main()
