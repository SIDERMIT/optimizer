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


if __name__ == '__main__':
    unittest.main()