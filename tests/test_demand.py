import os
import unittest
from pathlib import Path

from sidermit import demand
from sidermit import exceptions
from sidermit import graph


class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'demand')

    def test_symmetric_parameters_exceptions(self):
        """
        to test symmetric parameters exceptions y, a, alpha, beta
        :return:
        """

        g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)

        with self.assertRaises(exceptions.YIsNotValidExceptions):
            demand.Demand.build_from_parameters(g, None, 0.5, 1 / 3, 1 / 3)
        with self.assertRaises(exceptions.AIsNotValidExceptions):
            demand.Demand.build_from_parameters(g, 1000, None, 1 / 3, 1 / 3)
        with self.assertRaises(exceptions.AlphaIsNotValidExceptions):
            demand.Demand.build_from_parameters(g, 1000, 0.5, None, 1 / 3)
        with self.assertRaises(exceptions.BetaIsNotValidExceptions):
            demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, None)

        with self.assertRaises(exceptions.YOutRangeExceptions):
            demand.Demand.build_from_parameters(g, -100, 0.5, 1 / 3, 1 / 3)
        with self.assertRaises(exceptions.AOutRangeExceptions):
            demand.Demand.build_from_parameters(g, 1000, 2, 1 / 3, 1 / 3)
        with self.assertRaises(exceptions.AlphaOutRangeExceptions):
            demand.Demand.build_from_parameters(g, 1000, 0.5, 2, 1 / 3)
        with self.assertRaises(exceptions.BetaOutRangeExceptions):
            demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, 2)
        with self.assertRaises(exceptions.AlphaBetaOutRangeExceptions):
            demand.Demand.build_from_parameters(g, 1000, 0.5, 0.8, 0.8)

    def test_build_from_parameters(self):
        """
        to test build_from_parameters method
        :return:
        """
        g = graph.Graph.build_from_parameters(0, 1000, 0.5, 2)

        d = demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, 1 / 3)

        self.assertEqual(len(d.get_matrix()), 1)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 2)

        d = demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, 1 / 3)

        self.assertEqual(len(d.get_matrix()), 3)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 2)

        d = demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, 1 / 3)

        self.assertEqual(len(d.get_matrix()), 5)

    def test_build_from_file(self):
        """
        to test build_from_file method
        :return:
        """
        g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)
        d = demand.Demand.build_from_file(g, os.path.join(self.data_path, 'test_matrix.csv'))

        self.assertEqual(len(d.get_matrix()), 7)

    def test_matrix_to_file(self):
        """
        to test matrix_to_file method
        :return:
        """

        # build graph
        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 2)
        d = demand.Demand.build_from_parameters(g, 1000, 0.5, 1 / 3, 1 / 3)
        # write file
        d.matrix_to_file(os.path.join(self.data_path, 'write1_test.csv'))
        fileObj = Path(os.path.join(self.data_path, 'write1_test.csv'))
        # test
        self.assertTrue(fileObj.is_file())
        # remove file
        os.remove(os.path.join(self.data_path, 'write1_test.csv'))

    def test_change_vij_exceptions(self):
        """
        to test exceptions of change_vij method
        :return:
        """

        with self.assertRaises(exceptions.tripsValueIsNotValidExceptions):
            g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)
            demand.Demand.build_from_file(g, os.path.join(self.data_path, 'test_raisesVijNegativeExceptions.csv'))

        with self.assertRaises(exceptions.IdDestinationnDoesNotFoundExceptions):
            g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)
            demand.Demand.build_from_file(g,
                                          os.path.join(self.data_path, 'test_raisesDestinationNotFoundExceptions.csv'))

        with self.assertRaises(exceptions.IdOriginDoesNotFoundExceptions):
            g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)
            demand.Demand.build_from_file(g, os.path.join(self.data_path, 'test_raisesOriginNotFoundExceptions.csv'))

    def test_build_from_file_exceptions(self):
        """
        to test exceptions of build_from_file method
        :return:
        """

        with self.assertRaises(exceptions.FileFormatIsNotValidExceptions):
            g = graph.Graph.build_from_parameters(3, 1000, 0.5, 2)
            demand.Demand.build_from_file(g, os.path.join(self.data_path, 'test_raisesFormatExceptions.csv'))


if __name__ == '__main__':
    unittest.main()
