import unittest
from sidermit import graph
from sidermit import exceptions
import os


class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file_tests')
        self.test_0zone_path = os.path.join(self.data_path, 'test_0zone.PAJEK')
        self.test_1zone_path = os.path.join(self.data_path, 'test_1zone.PAJEK')
        self.test_2zone_path = os.path.join(self.data_path, 'test_2zone.PAJEK')
        self.test_formatPajekExceptions = os.path.join(self.data_path, 'test_formatPajekExceptions.PAJEK')

    # to test validator
    def test_is_valid(self):
        g = graph.Graph.build_from_file(self.test_0zone_path)

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_file(self.test_1zone_path)

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_file(self.test_2zone_path)

        self.assertTrue(g.is_valid())

        # to test with parameters of assymetry

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, angles=[10])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[10, 50])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Gi=[2])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[2, 0.5])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Hi=[2])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[2, 0.5])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1)

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=2)

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10], Gi=[2], Hi=[2])

        self.assertTrue(g.is_valid())

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10, 50], Gi=[2, 0.5],
                                              Hi=[2, 0.5])

        self.assertTrue(g.is_valid())

    # to test read a pajek file
    def test_read_pajek_file(self):
        g = graph.Graph.build_from_file(self.test_0zone_path)

        self.assertEqual(len(g.nodes), 1)
        self.assertEqual(len(g.edges), 0)
        self.assertEqual(len(g.zones), 0)

        g = graph.Graph.build_from_file(self.test_1zone_path)

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_file(self.test_2zone_path)

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

    # to test verified that len of nodes, zones y edges builded is correct
    def test_build_from_parameters(self):
        g = graph.Graph.build_from_parameters(0, 1000, 0.5, 0)

        self.assertEqual(len(g.nodes), 1)
        self.assertEqual(len(g.edges), 0)
        self.assertEqual(len(g.zones), 0)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0)

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0)

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

    # to test parameters Exceptions n, l, g, p
    def test_parameters_exceptions(self):
        with self.assertRaises(exceptions.NIsNotValidNumberException):
            graph.Graph.build_from_parameters(-1, 1000, 0.5, 0)
        with self.assertRaises(exceptions.LIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, -1000, 0.5, 0)
        with self.assertRaises(exceptions.GIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, 1000, -0.5, 0)
        with self.assertRaises(exceptions.PIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, 1000, 0.5, -1)

    # to test build with parameters of assymetry
    def test_asymmetry_parameters(self):
        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, angles=[10])

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[10, 50])

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Gi=[2])

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[2, 0.5])

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Hi=[2])

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[2, 0.5])

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1)

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=2)

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10], Gi=[2], Hi=[2])

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.zones), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10, 50], Gi=[2, 0.5],
                                              Hi=[2, 0.5])

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 10)
        self.assertEqual(len(g.zones), 2)



    def test_asymmetric_parameters_exceptions(self):
        '''
        # to test asymmetric parameters Exceptions n, l, g, p
        :return:
        '''
        with self.assertRaises(exceptions.EthaValueRequiredExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha_zone=2)
        with self.assertRaises(exceptions.EthaZoneValueRequiredExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5)
        with self.assertRaises(exceptions.EthaValueIsNotValidExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=-1, etha_zone=2)
        with self.assertRaises(exceptions.EthaZoneValueIsNotValidExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=3)
        with self.assertRaises(exceptions.LenAnglesIsNotValidExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[20])
        with self.assertRaises(exceptions.AngleValueIsNotValidEceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[20, 370])
        with self.assertRaises(exceptions.LenGiIsNotValidExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[0.5])
        with self.assertRaises(exceptions.GiValueIsNotValidEceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[0.5, -2])
        with self.assertRaises(exceptions.LenHiIsNotValidExceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[0.5])
        with self.assertRaises(exceptions.HiValueIsNotValidEceptions):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[0.5, -2])

    # to test write pajek file
    def test_graph_to_pajek(self):
        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10, 50], Gi=[2, 0.5],
                                              Hi=[2, 0.5])

        self.assertTrue(g.graph_to_pajek(os.path.join(self.data_path, 'write1_test.PAJEK')))



    # to test Graph.obtain_angle(x, y)
    def test_obtain_angle(self):
        g = graph.Graph()
        self.assertEqual(int(g.obtain_angle(1, 0)), 0)
        self.assertEqual(int(g.obtain_angle(0, 1)), 90)
        self.assertEqual(int(g.obtain_angle(-1, 0)), 180)
        self.assertEqual(int(g.obtain_angle(0, -1)), 270)
        self.assertEqual(int(g.obtain_angle(1, 1)), 45)
        self.assertEqual(int(g.obtain_angle(-1, 1)), 135)
        self.assertEqual(int(g.obtain_angle(-1, -1)), 225)
        self.assertEqual(int(g.obtain_angle(1, -1)), 315)

    def test_raises_fileformat(self):
        with self.assertRaises(exceptions.FileFormatIsNotValidExceptions):
            graph.Graph.build_from_file(self.test_2zone_path, file_format="CSV")

    def test_raises_payekformat(self):
        with self.assertRaises(exceptions.PajekFormatIsNotValidExceptions):
            graph.Graph.build_from_file(self.test_formatPajekExceptions)

    def test_zone_exceptions(self):


if __name__ == '__main__':
    unittest.main()
