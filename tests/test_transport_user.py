import unittest

from sidermit import exceptions
from sidermit import transport_user


class test_graph(unittest.TestCase):

    def test_user(self):
        """
        test user class method
        :return:
        """

        transport_user.User(1, 1, 1, 1, 1, 1, 1, 1, 1)

    def test_raises_user_exceptions(self):
        """
        test user exceptions
        :return:
        """

        with self.assertRaises(exceptions.VaIsNotValidExceptions):
            transport_user.User(0, 1, 1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PvIsNotValidExceptions):
            transport_user.User(1, -1, 1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PwIsNotValidExceptions):
            transport_user.User(1, 1, -1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PaIsNotValidExceptions):
            transport_user.User(1, 1, 1, -1, 1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.PtIsNotValidExceptions):
            transport_user.User(1, 1, 1, 1, -1, 1, 1, 1, 1)
        with self.assertRaises(exceptions.SpvIsNotValidExceptions):
            transport_user.User(1, 1, 1, 1, 1, -1, 1, 1, 1)
        with self.assertRaises(exceptions.SpwIsNotValidExceptions):
            transport_user.User(1, 1, 1, 1, 1, 1, -1, 1, 1)
        with self.assertRaises(exceptions.SpaIsNotValidExceptions):
            transport_user.User(1, 1, 1, 1, 1, 1, 1, -1, 1)
        with self.assertRaises(exceptions.SptIsNotValidExceptions):
            transport_user.User(1, 1, 1, 1, 1, 1, 1, 1, -1)

    def test_transport_user(self):
        """
        to test transport_user class
        :return:
        """

        u = transport_user.TransportUser()

        self.assertEqual(u.get_user().va, 4.0)

        u.update_user()

        self.assertEqual(u.get_user().va, 4.0)


if __name__ == '__main__':
    unittest.main()
