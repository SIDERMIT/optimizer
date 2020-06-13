import os
import unittest
from pathlib import Path

from sidermit import exceptions
from sidermit import demand


class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'demand')

    def test_get_method(self):
        """
        test methods get class graph
        :return:
        """



if __name__ == '__main__':
    unittest.main()