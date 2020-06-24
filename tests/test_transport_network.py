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

        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")

        r = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(isinstance(r, Route))

    def test_raises_routes_exceptions(self):
        """
        to check route class exceptions
        :return:
        """

        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")

        with self.assertRaises(exceptions.RouteIdIsNotValidException):
            Route(None, bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                  "3,0,1")

        with self.assertRaises(exceptions.ModeIsNotValidException):
            Route("r1", "train", "1,2,0,4,3", "3,4,0,2,1",
                  "1,0,3", "3,0,1")

        with self.assertRaises(exceptions.StopsSequencesException):
            Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,5,3",
                  "3,0,1")

        with self.assertRaises(exceptions.FirstStopIsNotValidException):
            Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "2,0,3",
                  "3,0,1")

        with self.assertRaises(exceptions.LastStopIsNotValidException):
            Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,2",
                  "3,0,1")

        with self.assertRaises(exceptions.NotCycleException):
            Route("r1", bus_obj, "1,2,0,4,3", "4,0,2,1", "1,0,3",
                  "4,0,1")

    def test_add_route_transport_network(self):
        """
        to test add_route method of transport_network class
        :return:
        """
        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        network = TransportNetwork(graph_obj)
        route = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        network.add_route(route)

        self.assertTrue(isinstance(network.get_route("r1"), Route))
        self.assertEqual(len(network.get_routes()), 1)

        with self.assertRaises(exceptions.RouteIsNotvalidException):
            network.add_route("route")

        with self.assertRaises(exceptions.NodeSequencesIsNotValidException):
            route = Route("r2", bus_obj, "1,3,0,4,3", "3,4,0,2,1", "1,0,3",
                          "3,0,1")
            network.add_route(route)

        with self.assertRaises(exceptions.RouteIdDuplicatedException):
            route = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3",
                          "3,0,1")
            network.add_route(route)

    def test_delete_route_transport_network(self):
        """
        to test delete_route method of class transport_network class
        :return:
        """

        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        network = TransportNetwork(graph_obj)
        route = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        network.add_route(route)
        network.delete_route("r1")
        self.assertEqual(len(network.get_routes()), 0)

        with self.assertRaises(exceptions.RouteIdNotFoundException):
            network.delete_route("r1")

    def test_network_to_file(self):
        """
        to test method to write a file with network information
        :return:
        """

        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        metro = mode_manager.get_mode("metro")
        network = TransportNetwork(graph_obj)
        route1 = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        route2 = Route("r2", metro, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        network.add_route(route1)
        network.add_route(route2)
        # write file
        network.routes_to_file(os.path.join(self.data_path, 'write_test.csv'))
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

        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        network = TransportNetwork(graph_obj)
        route = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        network.add_route(route)

        self.assertTrue(network.is_valid())

        network.delete_route("r1")

        self.assertTrue(not network.is_valid())

    def test_raises_get_route_exceptions(self):
        """
        raises get_route exceptions from transport network class
        :return:
        """
        with self.assertRaises(exceptions.RouteIdNotFoundException):
            graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            network = TransportNetwork(graph_obj)
            network.get_route("r1")

    def test_update_route(self):
        """
        to test update_route method from transport_network class
        :return:
        """
        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        metro_obj = mode_manager.get_mode("metro")
        network = TransportNetwork(graph_obj)
        route = Route("r1", bus_obj, "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        network.add_route(route)

        network.update_route("r1", mode=metro_obj)
        self.assertEqual(network.get_route("r1").mode, metro_obj)

        network.update_route("r1")
        self.assertEqual(network.get_route("r1").mode, metro_obj)

        with self.assertRaises(exceptions.RouteIdNotFoundException):
            network.update_route("r3")

    def test_get_feeder_routes(self):
        """
        to test add feeder routes
        :return:
        """
        graph_obj = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        network = TransportNetwork(graph_obj)

        routes = network.get_feeder_routes(bus_obj)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2"])
        self.assertEqual(routes[0].nodes_sequence_r, ["2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "2"])
        self.assertEqual(routes[0].stops_sequence_r, ["2", "1"])
        self.assertEqual(routes[1].nodes_sequence_i, ["3", "4"])
        self.assertEqual(routes[1].nodes_sequence_r, ["4", "3"])
        self.assertEqual(routes[1].stops_sequence_i, ["3", "4"])
        self.assertEqual(routes[1].stops_sequence_r, ["4", "3"])

        with self.assertRaises(exceptions.ModeIsNotValidException):
            network.get_feeder_routes("bus_obj")

    def test_get_circular_routes(self):
        """
        to test add circular routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        network = TransportNetwork(g)

        routes = network.get_circular_routes(bus_obj)

        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "4", "6", "8", "10", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "4", "6", "8", "10", "2"])
        self.assertEqual(routes[0].nodes_sequence_r, [])
        self.assertEqual(routes[0].stops_sequence_r, [])

        self.assertEqual(routes[1].nodes_sequence_i, [])
        self.assertEqual(routes[1].stops_sequence_i, [])
        self.assertEqual(routes[1].nodes_sequence_r, ["10", "8", "6", "4", "2", "10"])
        self.assertEqual(routes[1].stops_sequence_r, ["10", "8", "6", "4", "2", "10"])

        with self.assertRaises(exceptions.ModeIsNotValidException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            network = TransportNetwork(g)
            network.get_circular_routes("bus_obj")

        with self.assertRaises(exceptions.CircularRouteIsNotValidException):
            g = graph.Graph.build_from_parameters(1, 1000, 0.5, 2)
            mode_manager = TransportModeManager()
            bus_obj = mode_manager.get_mode("bus")
            network = TransportNetwork(g)
            network.get_circular_routes(bus_obj)

    def test_get_radial_routes(self):
        """
        to test add radial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        metro_obj = mode_manager.get_mode("metro")
        network = TransportNetwork(g)

        routes = network.get_radial_routes(mode_obj=bus_obj, short=False, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(routes[0].nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "2", "0"])
        self.assertEqual(routes[0].stops_sequence_r, ["0", "2", "1"])
        self.assertEqual(routes[1].nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(routes[1].nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(routes[1].stops_sequence_i, ["3", "4", "0"])
        self.assertEqual(routes[1].stops_sequence_r, ["0", "4", "3"])

        routes = network.get_radial_routes(mode_obj=bus_obj, short=True, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "0"])
        self.assertEqual(routes[0].nodes_sequence_r, ["0", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "0"])
        self.assertEqual(routes[0].stops_sequence_r, ["0", "2"])
        self.assertEqual(routes[1].nodes_sequence_i, ["4", "0"])
        self.assertEqual(routes[1].nodes_sequence_r, ["0", "4"])
        self.assertEqual(routes[1].stops_sequence_i, ["4", "0"])
        self.assertEqual(routes[1].stops_sequence_r, ["0", "4"])

        routes = network.get_radial_routes(mode_obj=bus_obj, short=False, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(routes[0].nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "0"])
        self.assertEqual(routes[0].stops_sequence_r, ["0", "1"])
        self.assertEqual(routes[1].nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(routes[1].nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(routes[1].stops_sequence_i, ["3", "0"])
        self.assertEqual(routes[1].stops_sequence_r, ["0", "3"])

        routes = network.get_radial_routes(mode_obj=metro_obj, short=True, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "0"])
        self.assertEqual(routes[0].nodes_sequence_r, ["0", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "0"])
        self.assertEqual(routes[0].stops_sequence_r, ["0", "2"])
        self.assertEqual(routes[1].nodes_sequence_i, ["4", "0"])
        self.assertEqual(routes[1].nodes_sequence_r, ["0", "4"])
        self.assertEqual(routes[1].stops_sequence_i, ["4", "0"])
        self.assertEqual(routes[1].stops_sequence_r, ["0", "4"])

        with self.assertRaises(exceptions.ModeIsNotValidException):
            network.get_radial_routes("bus_obj")

    def test_get_diametral_routes(self):
        """
        to test add diametral routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        bus_obj = m.get_mode("bus")
        network = TransportNetwork(g)

        routes = network.get_diametral_routes(mode_obj=bus_obj, jump=2, short=False, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(routes[0].nodes_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(routes[0].stops_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["3", "4", "0", "10", "9"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["3", "4", "0", "10", "9"])

        routes = network.get_diametral_routes(mode_obj=bus_obj, jump=2, short=True, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "0", "6"])
        self.assertEqual(routes[0].nodes_sequence_r, ["6", "0", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "0", "6"])
        self.assertEqual(routes[0].stops_sequence_r, ["6", "0", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "0", "4"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["4", "0", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "0", "4"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["4", "0", "10"])

        routes = network.get_diametral_routes(mode_obj=bus_obj, jump=2, short=False, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "0", "6", "5"])
        self.assertEqual(routes[0].nodes_sequence_r, ["5", "6", "0", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "5"])
        self.assertEqual(routes[0].stops_sequence_r, ["5", "1"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["9", "10", "0", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["3", "4", "0", "10", "9"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["9", "3"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["3", "9"])

        routes = network.get_diametral_routes(mode_obj=bus_obj, jump=2, short=True, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "0", "6"])
        self.assertEqual(routes[0].nodes_sequence_r, ["6", "0", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "6"])
        self.assertEqual(routes[0].stops_sequence_r, ["6", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "0", "4"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["4", "0", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "4"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["4", "10"])

        routes = network.get_diametral_routes(mode_obj=bus_obj, jump=1, short=True, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "0", "4"])
        self.assertEqual(routes[0].nodes_sequence_r, ["4", "0", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "4"])
        self.assertEqual(routes[0].stops_sequence_r, ["4", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "0", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["2", "0", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "2"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["2", "10"])

        with self.assertRaises(exceptions.JumpIsNotValidException):
            network.get_diametral_routes(mode_obj=bus_obj, jump=6, short=True, express=True)

        with self.assertRaises(exceptions.ModeIsNotValidException):
            network.get_diametral_routes(mode_obj="bus_obj", jump=6, short=True, express=True)

    def test_get_tangencial_routes(self):
        """
        to test add tangencial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = TransportModeManager()
        bus = m.get_mode("bus")
        t = TransportNetwork(g)

        routes = t.get_tangencial_routes(mode_obj=bus, jump=2, short=False, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(routes[0].nodes_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(routes[0].stops_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["3", "4", "2", "10", "9"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["3", "4", "2", "10", "9"])

        routes = t.get_tangencial_routes(mode_obj=bus, jump=2, short=True, express=False)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "4", "6"])
        self.assertEqual(routes[0].nodes_sequence_r, ["6", "4", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "4", "6"])
        self.assertEqual(routes[0].stops_sequence_r, ["6", "4", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "2", "4"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["4", "2", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "2", "4"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["4", "2", "10"])

        routes = t.get_tangencial_routes(mode_obj=bus, jump=2, short=False, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["1", "2", "4", "6", "5"])
        self.assertEqual(routes[0].nodes_sequence_r, ["5", "6", "4", "2", "1"])
        self.assertEqual(routes[0].stops_sequence_i, ["1", "5"])
        self.assertEqual(routes[0].stops_sequence_r, ["5", "1"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["9", "10", "2", "4", "3"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["3", "4", "2", "10", "9"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["9", "3"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["3", "9"])

        routes = t.get_tangencial_routes(mode_obj=bus, jump=2, short=True, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "4", "6"])
        self.assertEqual(routes[0].nodes_sequence_r, ["6", "4", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "6"])
        self.assertEqual(routes[0].stops_sequence_r, ["6", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "2", "4"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["4", "2", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "4"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["4", "10"])

        routes = t.get_tangencial_routes(mode_obj=bus, jump=1, short=True, express=True)

        self.assertEqual(len(routes), 5)
        self.assertEqual(routes[0].nodes_sequence_i, ["2", "4"])
        self.assertEqual(routes[0].nodes_sequence_r, ["4", "2"])
        self.assertEqual(routes[0].stops_sequence_i, ["2", "4"])
        self.assertEqual(routes[0].stops_sequence_r, ["4", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_i, ["10", "2"])
        self.assertEqual(routes[len(routes) - 1].nodes_sequence_r, ["2", "10"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_i, ["10", "2"])
        self.assertEqual(routes[len(routes) - 1].stops_sequence_r, ["2", "10"])

        with self.assertRaises(exceptions.JumpIsNotValidException):
            t.get_tangencial_routes(mode_obj=bus, jump=6, short=True, express=True)

        with self.assertRaises(exceptions.ModeIsNotValidException):
            t.get_tangencial_routes(mode_obj="bus", jump=6, short=True, express=True)

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

        t = TransportNetwork(g)
        m = TransportModeManager()
        bus = m.get_mode("bus")
        routes = t.get_radial_routes(bus)

        for route in routes:
            t.add_route(route)

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
