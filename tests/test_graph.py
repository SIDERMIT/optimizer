import os
import unittest
from pathlib import Path

from sidermit import exceptions
from sidermit import graph


class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'graph')
        self.test_0zone_path = os.path.join(self.data_path, 'test_0zone.PAJEK')
        self.test_1zone_path = os.path.join(self.data_path, 'test_1zone.PAJEK')
        self.test_2zone_path = os.path.join(self.data_path, 'test_2zone.PAJEK')
        self.test_3zone_path = os.path.join(self.data_path, 'test_3zone.PAJEK')
        self.test_formatPajekExceptions = os.path.join(self.data_path, 'test_formatPajekExceptions.PAJEK')
        self.test_NodeTypeExceptions = os.path.join(self.data_path, 'test_NodeTypeExceptions.PAJEK')
        self.test_NumberOfLinesExceptions = os.path.join(self.data_path, 'test_NumberOfLinesExceptions.PAJEK')
        self.test_NumberNodesForZoneExceptions = os.path.join(self.data_path, 'test_NumberNodesForZoneExceptions.PAJEK')
        self.test_needCbdExceptions = os.path.join(self.data_path, 'test_needCbdExceptions.PAJEK')
        self.test_nodeIdExceptions = os.path.join(self.data_path, 'test_nodeIdExceptions.PAJEK')

    def test_get_method(self):
        """
        test methods get class graph
        :return:
        """
        g = graph.Graph.build_from_file(self.test_3zone_path)

        self.assertTrue(isinstance(g.get_cbd(), graph.CBD))
        self.assertEqual(g.get_n(), 3)
        self.assertEqual(len(g.get_zones()), 3)
        self.assertEqual(len(g.get_nodes()), 7)
        self.assertEqual(len(g.get_edges()), 18)

    def test_Node_Exceptions(self):
        """
        to test exceptions class Node
        :return:
        """
        node_id = 0
        x = 0
        y = 0
        radius = 0
        angle = 0
        width = 0
        zone_id = 0
        name = "CBD"
        with self.assertRaises(exceptions.NameIsNotDefinedException):
            graph.Node(node_id, x, y, radius, angle, width, zone_id, None)
        with self.assertRaises(exceptions.NodeIdIsNotValidException):
            graph.Node(None, x, y, radius, angle, width, zone_id, name)
        with self.assertRaises(exceptions.ZoneIdIsNotValidException):
            graph.Node(node_id, x, y, radius, angle, width, None, name)
        with self.assertRaises(exceptions.NodeRadiusIsNotValidException):
            graph.Node(node_id, x, y, -2, angle, width, zone_id, name)
        with self.assertRaises(exceptions.NodeAngleIsNotValidException):
            graph.Node(node_id, x, y, radius, -10, width, zone_id, name)
        with self.assertRaises(exceptions.NodeWidthIsNotValidException):
            graph.Node(node_id, x, y, radius, angle, -2, zone_id, name)

    def test_CBD_Exceptions(self):
        """
        to test exceptions class CBD
        :return:
        """
        node_id = 0
        x = 0
        y = 0
        radius = 0
        angle = 0
        width = 0
        name = "CBD"
        with self.assertRaises(exceptions.ZoneIdIsNotValidException):
            graph.CBD(node_id, x, y, radius, angle, width, 2, name)

    def test_Zone_Exceptions(self):
        """
        to test exceptions class zone
        :return:
        """
        with self.assertRaises(exceptions.ZoneIdIsNotValidException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            sc = graph.Subcenter(2, 1, 1, 1, 1, 1, 1, "sc")
            graph.Zone(-1, p, sc)
        with self.assertRaises(exceptions.ZoneIdIsNotValidException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            sc = graph.Subcenter(2, 1, 1, 1, 1, 1, 1, "sc")
            graph.Zone(None, p, sc)
        with self.assertRaises(exceptions.PeripheryNodeTypeIsNotValidException):
            sc = graph.Subcenter(2, 1, 1, 1, 1, 1, 1, "sc")
            graph.Zone(1, sc, sc)
        with self.assertRaises(exceptions.SubcenterNodeTypeIsNotValidException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            graph.Zone(1, p, p)
        with self.assertRaises(exceptions.ZoneIdIsNotValidException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            sc = graph.Subcenter(2, 1, 1, 1, 1, 1, 1, "sc")
            graph.Zone(2, p, sc)

    def test_Edge_Exceptions(self):
        """
        to test exceptions class Edge
        :return:
        """
        with self.assertRaises(exceptions.EdgeIdIsNotValidException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            sc = graph.Subcenter(2, 1, 1, 1, 1, 1, 1, "sc")
            graph.Edge(None, p, sc)
        with self.assertRaises(exceptions.EdgeIsNotAvailableException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            graph.Edge(1, p, p)
        with self.assertRaises(exceptions.EdgeIsNotAvailableException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            cbd = graph.CBD(0, 0, 0, 0, 0, 0, 0, "CBD")
            graph.Edge(1, p, cbd)
        with self.assertRaises(exceptions.EdgeIsNotAvailableException):
            p = graph.Periphery(1, 1, 1, 1, 1, 1, 1, "p")
            cbd = graph.CBD(0, 0, 0, 0, 0, 0, 0, "CBD")
            graph.Edge(1, cbd, p)

    def test_build_from_pajek_file(self):
        """
        to test reading pajek file
        :return:
        """
        g = graph.Graph.build_from_file(self.test_0zone_path)

        self.assertEqual(len(g.get_nodes()), 1)
        self.assertEqual(len(g.get_edges()), 0)
        self.assertEqual(len(g.get_zones()), 0)

        g = graph.Graph.build_from_file(self.test_1zone_path)

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_file(self.test_2zone_path)

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

        g = graph.Graph.build_from_file(self.test_3zone_path)

        self.assertEqual(len(g.get_nodes()), 7)
        self.assertEqual(len(g.get_edges()), 18)
        self.assertEqual(len(g.get_zones()), 3)

    def test_build_from_parameters(self):
        """
        to test construction from parameters
        :return:
        """
        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0)

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, angles=[10])

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[10, 50])

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Gi=[2])

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[2, 0.5])

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, Hi=[2])

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[2, 0.5])

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1)

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=2)

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

        g = graph.Graph.build_from_parameters(1, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10], Gi=[2], Hi=[2])

        self.assertEqual(len(g.get_nodes()), 3)
        self.assertEqual(len(g.get_edges()), 4)
        self.assertEqual(len(g.get_zones()), 1)

        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10, 50], Gi=[2, 0.5],
                                              Hi=[2, 0.5])

        self.assertEqual(len(g.get_nodes()), 5)
        self.assertEqual(len(g.get_edges()), 10)
        self.assertEqual(len(g.get_zones()), 2)

    def test_raises_fileformat(self):
        """
        to test pajek file exceptions, should have 7 columns separated by white space
        :return:
        """
        with self.assertRaises(exceptions.FileFormatIsNotValidException):
            graph.Graph.build_from_file(self.test_2zone_path, file_format="CSV")

    def test_raises_payekformat(self):
        """
        to test pajek format exceptions: file must have 7 columns, separator for " "
        :return:
        """
        with self.assertRaises(exceptions.PajekFormatIsNotValidException):
            graph.Graph.build_from_file(self.test_formatPajekExceptions)

    def test_symmetric_parameters_exceptions(self):
        """
        to test symmetric parameters exceptions n, l, g, p
        :return:
        """
        with self.assertRaises(exceptions.NIsNotValidNumberException):
            graph.Graph.build_from_parameters(-1, 1000, 0.5, 0)
        with self.assertRaises(exceptions.LIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, -1000, 0.5, 0)
        with self.assertRaises(exceptions.GIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, 1000, -0.5, 0)
        with self.assertRaises(exceptions.PIsNotValidNumberException):
            graph.Graph.build_from_parameters(1, 1000, 0.5, -1)

    def test_asymmetric_parameters_exceptions(self):
        """
        to test asymmetric parameters exceptions etha, etha_zone, angles, Gi, Hi
        :return:
        """
        with self.assertRaises(exceptions.EthaValueRequiredException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha_zone=2)
        with self.assertRaises(exceptions.EthaZoneValueRequiredException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5)
        with self.assertRaises(exceptions.EthaValueIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=-1, etha_zone=2)
        with self.assertRaises(exceptions.EthaZoneValueIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=3)
        with self.assertRaises(exceptions.AngleListLengthIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[20])
        with self.assertRaises(exceptions.AngleValueIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, angles=[20, 370])
        with self.assertRaises(exceptions.GiListLengthIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[0.5])
        with self.assertRaises(exceptions.GiValueIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Gi=[0.5, -2])
        with self.assertRaises(exceptions.HiListLengthIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[0.5])
        with self.assertRaises(exceptions.HiValueIsNotValidException):
            graph.Graph.build_from_parameters(2, 1000, 0.5, 0, Hi=[0.5, -2])

    def test_graph_to_pajek(self):
        """
        to test file writing
        :return:
        """
        filename = 'write1_test.PAJEK'
        # build graph
        g = graph.Graph.build_from_parameters(2, 1000, 0.5, 0, etha=0.5, etha_zone=1, angles=[10, 50], Gi=[2, 0.5],
                                              Hi=[2, 0.5])
        # write file
        g.graph_to_pajek(os.path.join(self.data_path, filename))
        file_obj = Path(os.path.join(self.data_path, filename))

        # test
        self.assertTrue(file_obj.is_file())

        # TODO: validate format
        # import filecmp
        # self.assertTrue(filecmp.cmp(created_file_path, expected_file_path))

        # remove file
        os.remove(os.path.join(self.data_path, filename))

    def test_obtain_angle(self):
        """
        to test assistant method Graph.obtain_angle(x, y)
        :return:
        """
        g = graph.Graph()
        self.assertEqual(int(g.get_angle(1, 0)), 0)
        self.assertEqual(int(g.get_angle(0, 1)), 90)
        self.assertEqual(int(g.get_angle(-1, 0)), 180)
        self.assertEqual(int(g.get_angle(0, -1)), 270)
        self.assertEqual(int(g.get_angle(1, 1)), 45)
        self.assertEqual(int(g.get_angle(-1, 1)), 135)
        self.assertEqual(int(g.get_angle(-1, -1)), 225)
        self.assertEqual(int(g.get_angle(1, -1)), 315)

    def test_pajekfile_to_dataframe_exceptions(self):
        """
        to test exception of node type in pajek file
        :return:
        """
        with self.assertRaises(exceptions.NodeTypeIsNotValidException):
            graph.Graph.build_from_file(self.test_NodeTypeExceptions)

    def test_build_from_file_exceptions(self):
        """
        to test exception of number of lines in pajek file
        :return:
        """
        with self.assertRaises(exceptions.LineNumberInFileIsNotValidException):
            graph.Graph.build_from_file(self.test_NumberOfLinesExceptions)

        with self.assertRaises(exceptions.PeripherySubcenterNumberForZoneException):
            graph.Graph.build_from_file(self.test_NumberNodesForZoneExceptions)

    def test_add_zone_exceptions(self):
        """
        to check exceptions __add_zones method
        :return:
        """
        with self.assertRaises(exceptions.CBDDoesNotExistException):
            graph.Graph.build_from_file(self.test_needCbdExceptions)

    def test_add_nodes_exceptions(self):
        """
        to check exceptions __add_nodes method
        :return:
        """
        with self.assertRaises(exceptions.NodeIdDuplicatedException):
            graph.Graph.build_from_file(self.test_nodeIdExceptions)


if __name__ == '__main__':
    unittest.main()
