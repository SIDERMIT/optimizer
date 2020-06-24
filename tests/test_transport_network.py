import filecmp
import os
import unittest
from pathlib import Path

from sidermit import exceptions
from sidermit.city import graph
from sidermit.publictransportsystem import TransportModeManager, \
    TransportNetwork, Route


class TransportNetworkTest(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'transport_network')

    def test_routes(self):
        """
        test Route class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()

        r = Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                  "3,0,1")

        self.assertTrue(isinstance(r, Route))

    def test_raises_routes_exceptions(self):
        """
        to check route class exceptions
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()

        with self.assertRaises(exceptions.RouteIdIsNotValidException):
            Route(g, m, None, "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                  "3,0,1")

        with self.assertRaises(exceptions.ModeNameIsNotValidException):
            Route(g, m, "r1", "train", "1,2,0,4,3", "3,4,0,2,1",
                  "1,0,3", "3,0,1")

        with self.assertRaises(exceptions.StopsSequencesException):
            Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,5,3",
                  "3,0,1")

        with self.assertRaises(exceptions.FirstStopIsNotValidException):
            Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "2,0,3",
                  "3,0,1")

        with self.assertRaises(exceptions.LastStopIsNotValidException):
            Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,2",
                  "3,0,1")

        with self.assertRaises(exceptions.NotCycleException):
            Route(g, m, "r1", "bus", "1,2,0,4,3", "4,0,2,1", "1,0,3",
                  "4,0,1")

        with self.assertRaises(exceptions.NodeSequencesIsNotValidException):
            Route(g, m, "r1", "bus", "1,3,0,4,3", "3,4,0,2,1", "1,0,3",
                  "3,0,1")

    def test_add_route_transport_network(self):
        """
        to test add_route method of transport_network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(isinstance(t.get_route("r1"), Route))
        self.assertEqual(len(t.get_routes()), 1)

        with self.assertRaises(exceptions.RouteIdDuplicatedException):
            t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                        "3,0,1")

        with self.assertRaises(exceptions.BanRouteIdException):
            t.add_route("CIR_I_train", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                        "3,0,1")

    def test_delete_route_transport_network(self):
        """
        to test delete_route method of class transport_network class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        t.delete_route("r1")
        self.assertEqual(len(t.get_routes()), 0)

        with self.assertRaises(exceptions.RouteIdNotFoundException):
            t.delete_route("r1")

    def test_network_to_file(self):
        """
        to test method to write a file with network information
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        t.add_route("r2", "metro", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        # write file
        t.routes_to_file(os.path.join(self.data_path, 'write_test.csv'))
        file_obj = Path(os.path.join(self.data_path, 'write_test.csv'))
        # test
        self.assertTrue(file_obj.is_file())
        # to compare file with a test file
        self.assertTrue(
            filecmp.cmp(os.path.join(self.data_path, 'write1_test.csv'),
                        os.path.join(self.data_path, "write_test.csv")))
        # remove file
        os.remove(os.path.join(self.data_path, 'write_test.csv'))

    def test_is_valid(self):
        """
        to test is_Valid method from transport network class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(t.is_valid())

        t.delete_route("r1")

        self.assertTrue(not t.is_valid())

    def test_raises_get_route_exceptions(self):
        """
        raises get_route exceptions from transport network class
        :return:
        """
        with self.assertRaises(exceptions.RouteIdNotFoundException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = TransportModeManager()
            t = TransportNetwork(g, m)
            t.get_route("r1")

    def test_build_from_file(self):
        """
        to test method build_from_file transport network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork.build_from_file(g, m, os.path.join(
            self.data_path, 'write1_test.csv'))

        self.assertEqual(len(t.get_routes()), 2)

    def test_raises_build_from_file_exceptions(self):
        """
        raises build_from_file exceptions from transport network class
        :return:
        """
        with self.assertRaises(exceptions.FileFormatIsNotValidException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = TransportModeManager()
            TransportNetwork.build_from_file(g, m, os.path.join(
                self.data_path,
                'test_fileformatExceptions.csv'))

    def test_update_route(self):
        """
        to test update_route method from transport_network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork.build_from_file(g, m, os.path.join(
            self.data_path, 'write1_test.csv'))

        t.update_route("r1", mode_name="metro")
        self.assertEqual(t.get_route("r1").mode, "metro")

        t.update_route("r1")
        self.assertEqual(t.get_route("r1").mode, "metro")

        with self.assertRaises(exceptions.RouteIdNotFoundException):
            t.update_route("r3")

    def test_add_feeder_routes(self):
        """
        to test add feeder routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)

        t.add_feeder_routes("bus")

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("F_bus_1").nodes_sequence_i, ["1", "2"])
        self.assertEqual(t.get_route("F_bus_1").nodes_sequence_r, ["2", "1"])
        self.assertEqual(t.get_route("F_bus_1").stops_sequence_i, ["1", "2"])
        self.assertEqual(t.get_route("F_bus_1").stops_sequence_r, ["2", "1"])
        self.assertEqual(t.get_route("F_bus_2").nodes_sequence_i, ["3", "4"])
        self.assertEqual(t.get_route("F_bus_2").nodes_sequence_r, ["4", "3"])
        self.assertEqual(t.get_route("F_bus_2").stops_sequence_i, ["3", "4"])
        self.assertEqual(t.get_route("F_bus_2").stops_sequence_r, ["4", "3"])

        with self.assertRaises(exceptions.ModeNameNotFoundException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = TransportModeManager()
            t = TransportNetwork(g, m)
            t.add_feeder_routes("train")

    def test_add_circular_routes(self):
        """
        to test add circular routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)

        t.add_circular_routes("bus")

        self.assertEqual(len(t.get_routes()), 2)
        self.assertEqual(t.get_route("CIR_I_bus").nodes_sequence_i, ["2", "4", "6", "8", "10", "2"])
        self.assertEqual(t.get_route("CIR_I_bus").stops_sequence_i, ["2", "4", "6", "8", "10", "2"])
        self.assertEqual(t.get_route("CIR_I_bus").nodes_sequence_r, [])
        self.assertEqual(t.get_route("CIR_I_bus").stops_sequence_r, [])

        self.assertEqual(t.get_route("CIR_R_bus").nodes_sequence_i, [])
        self.assertEqual(t.get_route("CIR_R_bus").stops_sequence_i, [])
        self.assertEqual(t.get_route("CIR_R_bus").nodes_sequence_r, ["10", "8", "6", "4", "2", "10"])
        self.assertEqual(t.get_route("CIR_R_bus").stops_sequence_r, ["10", "8", "6", "4", "2", "10"])

        with self.assertRaises(exceptions.CircularRouteIsNotValidException):
            g = graph.Graph.build_from_parameters(1, 1000, 0.5, 2)
            m = TransportModeManager()
            t = TransportNetwork(g, m)
            t.add_circular_routes("bus")

        with self.assertRaises(exceptions.ModeNameNotFoundException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = TransportModeManager()
            t = TransportNetwork(g, m)
            t.add_circular_routes("train")


    def test_add_radial_routes(self):
        """
        to test add radial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)

        t.add_radial_routes(mode_name="bus", short=False, express=False)

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("R_bus_1").nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("R_bus_1").nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("R_bus_1").stops_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("R_bus_1").stops_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("R_bus_2").nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("R_bus_2").nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(t.get_route("R_bus_2").stops_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("R_bus_2").stops_sequence_r, ["0", "4", "3"])

        t.add_radial_routes(mode_name="bus", short=True, express=False)

        self.assertEqual(len(t.get_routes()), 10)
        self.assertEqual(t.get_route("RS_bus_1").nodes_sequence_i, ["2", "0"])
        self.assertEqual(t.get_route("RS_bus_1").nodes_sequence_r, ["0", "2"])
        self.assertEqual(t.get_route("RS_bus_1").stops_sequence_i, ["2", "0"])
        self.assertEqual(t.get_route("RS_bus_1").stops_sequence_r, ["0", "2"])
        self.assertEqual(t.get_route("RS_bus_2").nodes_sequence_i, ["4", "0"])
        self.assertEqual(t.get_route("RS_bus_2").nodes_sequence_r, ["0", "4"])
        self.assertEqual(t.get_route("RS_bus_2").stops_sequence_i, ["4", "0"])
        self.assertEqual(t.get_route("RS_bus_2").stops_sequence_r, ["0", "4"])

        t.add_radial_routes(mode_name="bus", short=False, express=True)

        self.assertEqual(len(t.get_routes()), 15)
        self.assertEqual(t.get_route("RE_bus_1").nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("RE_bus_1").nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("RE_bus_1").stops_sequence_i, ["1", "0"])
        self.assertEqual(t.get_route("RE_bus_1").stops_sequence_r, ["0", "1"])
        self.assertEqual(t.get_route("RE_bus_2").nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("RE_bus_2").nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(t.get_route("RE_bus_2").stops_sequence_i, ["3", "0"])
        self.assertEqual(t.get_route("RE_bus_2").stops_sequence_r, ["0", "3"])

        t.add_radial_routes(mode_name="metro", short=True, express=True)

        self.assertEqual(len(t.get_routes()), 20)
        self.assertEqual(t.get_route("RS_metro_1").nodes_sequence_i, ["2", "0"])
        self.assertEqual(t.get_route("RS_metro_1").nodes_sequence_r, ["0", "2"])
        self.assertEqual(t.get_route("RS_metro_1").stops_sequence_i, ["2", "0"])
        self.assertEqual(t.get_route("RS_metro_1").stops_sequence_r, ["0", "2"])
        self.assertEqual(t.get_route("RS_metro_2").nodes_sequence_i, ["4", "0"])
        self.assertEqual(t.get_route("RS_metro_2").nodes_sequence_r, ["0", "4"])
        self.assertEqual(t.get_route("RS_metro_2").stops_sequence_i, ["4", "0"])
        self.assertEqual(t.get_route("RS_metro_2").stops_sequence_r, ["0", "4"])

        with self.assertRaises(exceptions.RouteIdDuplicatedException):
            t.add_radial_routes(mode_name="metro", short=True, express=True)

        with self.assertRaises(exceptions.ModeNameNotFoundException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = TransportModeManager()
            t = TransportNetwork(g, m)
            t.add_radial_routes("train")


    def test_add_diametral_routes(self):
        """
        to test add diametral routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)

        t.add_diametral_routes(mode_name="bus", jump=2, short=False, express=False)

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("D2_bus_1").nodes_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(t.get_route("D2_bus_1").nodes_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(t.get_route("D2_bus_1").stops_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(t.get_route("D2_bus_1").stops_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(t.get_route("D2_bus_5").nodes_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(t.get_route("D2_bus_5").nodes_sequence_r, ["3", "4", "0", "10", "9"])
        self.assertEqual(t.get_route("D2_bus_5").stops_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(t.get_route("D2_bus_5").stops_sequence_r, ["3", "4", "0", "10", "9"])

        t.add_diametral_routes(mode_name="bus", jump=2, short=True, express=False)

        self.assertEqual(len(t.get_routes()), 10)
        self.assertEqual(t.get_route("DS2_bus_1").nodes_sequence_i, ["2", "0", "6"])
        self.assertEqual(t.get_route("DS2_bus_1").nodes_sequence_r, ["6", "0", "2"])
        self.assertEqual(t.get_route("DS2_bus_1").stops_sequence_i, ["2", "0", "6"])
        self.assertEqual(t.get_route("DS2_bus_1").stops_sequence_r, ["6", "0", "2"])
        self.assertEqual(t.get_route("DS2_bus_5").nodes_sequence_i, ["10", "0", "4"])
        self.assertEqual(t.get_route("DS2_bus_5").nodes_sequence_r, ["4", "0", "10"])
        self.assertEqual(t.get_route("DS2_bus_5").stops_sequence_i, ["10", "0", "4"])
        self.assertEqual(t.get_route("DS2_bus_5").stops_sequence_r, ["4", "0", "10"])

        t.add_diametral_routes(mode_name="bus", jump=2, short=False, express=True)

        self.assertEqual(len(t.get_routes()), 15)
        self.assertEqual(t.get_route("DE2_bus_1").nodes_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(t.get_route("DE2_bus_1").nodes_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(t.get_route("DE2_bus_1").stops_sequence_i, ["1", "5"])
        self.assertEqual(t.get_route("DE2_bus_1").stops_sequence_r, ["5", "1"])
        self.assertEqual(t.get_route("DE2_bus_5").nodes_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(t.get_route("DE2_bus_5").nodes_sequence_r, ["3", "4", "0", "10", "9"])
        self.assertEqual(t.get_route("DE2_bus_5").stops_sequence_i, ["9", "3"])
        self.assertEqual(t.get_route("DE2_bus_5").stops_sequence_r, ["3", "9"])

        t.add_diametral_routes(mode_name="bus", jump=2, short=True, express=True)

        self.assertEqual(len(t.get_routes()), 20)
        self.assertEqual(t.get_route("DSE2_bus_1").nodes_sequence_i, ["2", "0", "6"])
        self.assertEqual(t.get_route("DSE2_bus_1").nodes_sequence_r, ["6", "0", "2"])
        self.assertEqual(t.get_route("DSE2_bus_1").stops_sequence_i, ["2", "6"])
        self.assertEqual(t.get_route("DSE2_bus_1").stops_sequence_r, ["6", "2"])
        self.assertEqual(t.get_route("DSE2_bus_5").nodes_sequence_i, ["10", "0", "4"])
        self.assertEqual(t.get_route("DSE2_bus_5").nodes_sequence_r, ["4", "0", "10"])
        self.assertEqual(t.get_route("DSE2_bus_5").stops_sequence_i, ["10", "4"])
        self.assertEqual(t.get_route("DSE2_bus_5").stops_sequence_r, ["4", "10"])

        t.add_diametral_routes(mode_name="bus", jump=1, short=True, express=True)

        self.assertEqual(len(t.get_routes()), 25)
        self.assertEqual(t.get_route("DSE1_bus_1").nodes_sequence_i, ["2", "0", "4"])
        self.assertEqual(t.get_route("DSE1_bus_1").nodes_sequence_r, ["4", "0", "2"])
        self.assertEqual(t.get_route("DSE1_bus_1").stops_sequence_i, ["2", "4"])
        self.assertEqual(t.get_route("DSE1_bus_1").stops_sequence_r, ["4", "2"])
        self.assertEqual(t.get_route("DSE1_bus_5").nodes_sequence_i, ["10", "0", "2"])
        self.assertEqual(t.get_route("DSE1_bus_5").nodes_sequence_r, ["2", "0", "10"])
        self.assertEqual(t.get_route("DSE1_bus_5").stops_sequence_i, ["10", "2"])
        self.assertEqual(t.get_route("DSE1_bus_5").stops_sequence_r, ["2", "10"])

        with self.assertRaises(exceptions.JumpIsNotValidException):
            t.add_diametral_routes(mode_name="bus", jump=6, short=True, express=True)

        with self.assertRaises(exceptions.ModeNameNotFoundException):
            t.add_diametral_routes(mode_name="train", jump=4, short=True, express=True)

    def test_add_tangencial_routes(self):
        """
        to test add tangencial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        t = TransportNetwork(g, m)

        t.add_tangencial_routes(mode_name="bus", jump=2, short=False, express=False)

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("T2_bus_1").nodes_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(t.get_route("T2_bus_1").nodes_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(t.get_route("T2_bus_1").stops_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(t.get_route("T2_bus_1").stops_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(t.get_route("T2_bus_5").nodes_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(t.get_route("T2_bus_5").nodes_sequence_r, ["3", "4", "2", "10", "9"])
        self.assertEqual(t.get_route("T2_bus_5").stops_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(t.get_route("T2_bus_5").stops_sequence_r, ["3", "4", "2", "10", "9"])

        t.add_tangencial_routes(mode_name="bus", jump=2, short=True, express=False)

        self.assertEqual(len(t.get_routes()), 10)
        self.assertEqual(t.get_route("TS2_bus_1").nodes_sequence_i, ["2", "4", "6"])
        self.assertEqual(t.get_route("TS2_bus_1").nodes_sequence_r, ["6", "4", "2"])
        self.assertEqual(t.get_route("TS2_bus_1").stops_sequence_i, ["2", "4", "6"])
        self.assertEqual(t.get_route("TS2_bus_1").stops_sequence_r, ["6", "4", "2"])
        self.assertEqual(t.get_route("TS2_bus_5").nodes_sequence_i, ["10", "2", "4"])
        self.assertEqual(t.get_route("TS2_bus_5").nodes_sequence_r, ["4", "2", "10"])
        self.assertEqual(t.get_route("TS2_bus_5").stops_sequence_i, ["10", "2", "4"])
        self.assertEqual(t.get_route("TS2_bus_5").stops_sequence_r, ["4", "2", "10"])

        t.add_tangencial_routes(mode_name="bus", jump=2, short=False, express=True)

        self.assertEqual(len(t.get_routes()), 15)
        self.assertEqual(t.get_route("TE2_bus_1").nodes_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(t.get_route("TE2_bus_1").nodes_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(t.get_route("TE2_bus_1").stops_sequence_i, ["1", "5"])
        self.assertEqual(t.get_route("TE2_bus_1").stops_sequence_r, ["5", "1"])
        self.assertEqual(t.get_route("TE2_bus_5").nodes_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(t.get_route("TE2_bus_5").nodes_sequence_r, ["3", "4", "2", "10", "9"])
        self.assertEqual(t.get_route("TE2_bus_5").stops_sequence_i, ["9", "3"])
        self.assertEqual(t.get_route("TE2_bus_5").stops_sequence_r, ["3", "9"])

        t.add_tangencial_routes(mode_name="bus", jump=2, short=True, express=True)

        self.assertEqual(len(t.get_routes()), 20)
        self.assertEqual(t.get_route("TSE2_bus_1").nodes_sequence_i, ["2", "4", "6"])
        self.assertEqual(t.get_route("TSE2_bus_1").nodes_sequence_r, ["6", "4", "2"])
        self.assertEqual(t.get_route("TSE2_bus_1").stops_sequence_i, ["2", "6"])
        self.assertEqual(t.get_route("TSE2_bus_1").stops_sequence_r, ["6", "2"])
        self.assertEqual(t.get_route("TSE2_bus_5").nodes_sequence_i, ["10", "2", "4"])
        self.assertEqual(t.get_route("TSE2_bus_5").nodes_sequence_r, ["4", "2", "10"])
        self.assertEqual(t.get_route("TSE2_bus_5").stops_sequence_i, ["10", "4"])
        self.assertEqual(t.get_route("TSE2_bus_5").stops_sequence_r, ["4", "10"])

        t.add_tangencial_routes(mode_name="bus", jump=1, short=True, express=True)

        self.assertEqual(len(t.get_routes()), 25)
        self.assertEqual(t.get_route("TSE1_bus_1").nodes_sequence_i, ["2", "4"])
        self.assertEqual(t.get_route("TSE1_bus_1").nodes_sequence_r, ["4", "2"])
        self.assertEqual(t.get_route("TSE1_bus_1").stops_sequence_i, ["2", "4"])
        self.assertEqual(t.get_route("TSE1_bus_1").stops_sequence_r, ["4", "2"])
        self.assertEqual(t.get_route("TSE1_bus_5").nodes_sequence_i, ["10", "2"])
        self.assertEqual(t.get_route("TSE1_bus_5").nodes_sequence_r, ["2", "10"])
        self.assertEqual(t.get_route("TSE1_bus_5").stops_sequence_i, ["10", "2"])
        self.assertEqual(t.get_route("TSE1_bus_5").stops_sequence_r, ["2", "10"])

        with self.assertRaises(exceptions.JumpIsNotValidException):
            t.add_tangencial_routes(mode_name="bus", jump=6, short=True, express=True)

        with self.assertRaises(exceptions.ModeNameNotFoundException):
            t.add_tangencial_routes(mode_name="train", jump=4, short=True, express=True)

    def test_plot(self):
        """
        to test plot method
        :return: 
        """
        g = graph.Graph.build_from_parameters(7, 1000, 0.5, 0,
                                              angles=[10, 50, 150, 180, 270,
                                                      300, 320], etha=0.5,
                                              etha_zone=3,
                                              Hi=[1, 2, 1, 1, 1, 0.5, 3],
                                              Gi=[1, 2, 1, 1, 1, 3, 2])

        m = TransportModeManager(add_default_mode=True)

        t = TransportNetwork(g, m)
        t.add_radial_routes("bus")
        # save figure in path
        t.plot(os.path.join(self.data_path, 'figure2_test.png'))
        file_obj = Path(os.path.join(self.data_path, 'figure2_test.png'))
        # test
        self.assertTrue(file_obj.is_file())
        # to compare figure with a test figure
        self.assertTrue(
            filecmp.cmp(os.path.join(self.data_path, 'figure1_test.png'),
                        os.path.join(self.data_path, "figure2_test.png")))

        # remove file
        os.remove(os.path.join(self.data_path, 'figure2_test.png'))

        with self.assertRaises(exceptions.RouteIdNotFoundException):
            t.plot(os.path.join(self.data_path, 'figure_test2.png'),
                   list_routes=["506"])
            # remove file
            os.remove(os.path.join(self.data_path, 'figure2_test.png'))
