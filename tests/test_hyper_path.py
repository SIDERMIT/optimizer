import unittest

from sidermit.city import Graph, Demand
from sidermit.optimization.preoptimization import ExtendedGraph, Hyperpath
from sidermit.publictransportsystem import *


class test_hyper_path(unittest.TestCase):

    def test_network_validator(self):
        """
        to test network_validator method in class Hyperpath
        :return:
        """

        graph_obj = Graph.build_from_parameters(n=2, l=10000, g=0.5, p=2000)

        demand_obj = Demand.build_from_parameters(graph_obj, y=1000, a=0.5, alpha=1 / 3, beta=1 / 3)
        OD_matrix = demand_obj.get_matrix()

        [bus_obj, _] = TransportMode.get_default_modes()

        passenger_obj = Passenger.get_default_passenger()

        network_obj = TransportNetwork(graph_obj)
        radial = network_obj.get_radial_routes(bus_obj)

        extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

        hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

        self.assertTrue(not hyper_path_obj.network_validator(OD_matrix))

        for route in radial:
            network_obj.add_route(route)

        extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

        hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

        self.assertTrue(hyper_path_obj.network_validator(OD_matrix))

    def test_build_hyperpath_graph(self):
        """
        to test build_hyperpath_graph method of class Hyperpath
        :return:
        """

        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)

        [bus_obj, _] = TransportMode.get_default_modes()

        passenger_obj = Passenger.get_default_passenger()

        network_obj = TransportNetwork(graph_obj)
        radial = network_obj.get_radial_routes(bus_obj)
        diametral = network_obj.get_diametral_routes(bus_obj, jump=1)

        for route in radial:
            network_obj.add_route(route)
        for route in diametral:
            network_obj.add_route(route)

        extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

        nodes = extended_graph_obj.get_extended_graph_nodes()

        P1 = None
        P2 = None
        stop = None
        for city_node in nodes:
            if city_node.graph_node.name == str("P_1"):
                P1 = city_node
                stop = None
                for stop_node in nodes[city_node]:
                    stop = stop_node
            if city_node.graph_node.name == str("P_2"):
                P2 = city_node

        hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

        successors, label, frequencies = hyper_path_obj.build_hyperpath_graph(P1, P2)

        self.assertEqual(label[P1], float("inf"))
        self.assertEqual(label[P2], 0)
        self.assertEqual(label[stop], 1.7)

    def test_get_hyperpath_OD(self):

        """
        to test get_hyperpath_OD method of class Hyperpath
        :return:
        """

        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)

        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        passenger_obj = Passenger.get_default_passenger()

        network_obj = TransportNetwork(graph_obj)
        radial = network_obj.get_radial_routes(bus_obj)
        diametral = network_obj.get_diametral_routes(bus_obj, jump=1)
        diametral_metro = network_obj.get_diametral_routes(metro_obj, jump=1)

        for route in radial:
            network_obj.add_route(route)
        for route in diametral:
            network_obj.add_route(route)
        for route in diametral_metro:
            network_obj.add_route(route)

        extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

        nodes = extended_graph_obj.get_extended_graph_nodes()

        P1 = None
        P2 = None
        stop_bus = None
        stop_metro = None
        for city_node in nodes:
            if city_node.graph_node.name == str("P_1"):
                P1 = city_node
                for stop_node in nodes[city_node]:
                    if stop_node.mode.name == "bus":
                        stop_bus = stop_node
                    if stop_node.mode.name == "metro":
                        stop_metro = stop_node
            if city_node.graph_node.name == str("P_2"):
                P2 = city_node

        hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

        hyperpaths_od, label, successors, frequencies = hyper_path_obj.get_hyperpath_OD(P1, P2)

        self.assertEqual(label[P1], float("inf"))
        self.assertEqual(label[P2], 0)
        self.assertEqual(round(label[stop_bus], 5), 1.37738)
        self.assertEqual(round(label[stop_metro], 5), 0.83571 + 0.05)
        self.assertEqual(len(hyperpaths_od), 2)
        self.assertEqual(len(hyperpaths_od[stop_bus]), 2)
        self.assertEqual(len(hyperpaths_od[stop_metro]), 1)

    def test_get_all_hyperpaths(self):

        """
        to test get_all_hyperpaths method of class Hyperpath
        :return:
        """

        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)

        demand_obj = Demand.build_from_parameters(graph_obj, y=1000, a=0.5, alpha=1 / 3, beta=1 / 3)
        OD_matrix = demand_obj.get_matrix()

        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        passenger_obj = Passenger.get_default_passenger()

        network_obj = TransportNetwork(graph_obj)
        radial = network_obj.get_radial_routes(bus_obj)
        diametral = network_obj.get_diametral_routes(bus_obj, jump=1)
        diametral_metro = network_obj.get_diametral_routes(metro_obj, jump=1)

        for route in radial:
            network_obj.add_route(route)
        for route in diametral:
            network_obj.add_route(route)
        for route in diametral_metro:
            network_obj.add_route(route)

        extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

        nodes = extended_graph_obj.get_extended_graph_nodes()

        P1 = None
        SC2 = None
        stop_bus = None
        stop_metro = None
        for city_node in nodes:
            if city_node.graph_node.name == str("P_1"):
                P1 = city_node
                for stop in nodes[city_node]:
                    if stop.mode.name == "bus":
                        stop_bus = stop
                    if stop.mode.name == "metro":
                        stop_metro = stop
            if city_node.graph_node.name == str("SC_2"):
                SC2 = city_node

        hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

        hyperpaths, labels, successors, frequencies, vij = hyper_path_obj.get_all_hyperpaths(OD_matrix)

        self.assertEqual(round(labels[P1][SC2][stop_bus], 5), 1.25238)
        self.assertEqual(round(labels[P1][SC2][stop_metro], 5), 0.71071 + 0.05)

        self.assertEqual(len(hyperpaths), 4)
        self.assertEqual(len(hyperpaths[P1]), 3)
        self.assertEqual(len(hyperpaths[SC2]), 2)
