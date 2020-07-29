import unittest
from collections import defaultdict

from sidermit.city import Graph, Demand
from sidermit.optimization.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.publictransportsystem import Passenger, TransportMode, TransportNetwork
from sidermit.optimization import OperatorsCost


class test_operators_cost(unittest.TestCase):

    def test_lines_travel_time(self):
        """
        test lines_travel_time method of class operators_cost
        :return:
        """
        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        network_obj = TransportNetwork(graph_obj=graph_obj)

        feeder_routes_metro = network_obj.get_feeder_routes(mode_obj=metro_obj)
        radial_routes_bus = network_obj.get_radial_routes(mode_obj=bus_obj)

        for route in feeder_routes_metro:
            network_obj.add_route(route_obj=route)

        for route in radial_routes_bus:
            network_obj.add_route(route_obj=route)

        lines_travel_time = OperatorsCost.lines_travel_time(routes=network_obj.get_routes(),
                                                            edge_distance=graph_obj.get_edges_distance())

        self.assertEqual(lines_travel_time["R_bus_1"], 1.5)
        self.assertEqual(lines_travel_time["F_metro_1"], 0.25)

    def test_get_cycle_time(self):
        """
        test get_cycle_time method of class operators_cost
        :return:
        """
        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)
        demand_obj = Demand.build_from_parameters(graph_obj=graph_obj, y=100, a=0.5, alpha=1 / 3, beta=1 / 3)
        passenger_obj = Passenger.get_default_passenger()
        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        network_obj = TransportNetwork(graph_obj=graph_obj)

        feeder_routes_metro = network_obj.get_feeder_routes(mode_obj=metro_obj)
        radial_routes_bus = network_obj.get_radial_routes(mode_obj=bus_obj)

        for route in feeder_routes_metro:
            network_obj.add_route(route_obj=route)

        for route in radial_routes_bus:
            network_obj.add_route(route_obj=route)

        extended_graph_obj = ExtendedGraph(graph_obj=graph_obj, routes=network_obj.get_routes(), sPTP=passenger_obj.spt,
                                           frequency_routes=None)
        hyperpath_obj = Hyperpath(extended_graph_obj=extended_graph_obj, passenger_obj=passenger_obj)

        hyperpaths, labels, successors, frequency, Vij = hyperpath_obj.get_all_hyperpaths(
            OD_matrix=demand_obj.get_matrix())

        OD_assignment = Assignment.get_assignment(hyperpaths=hyperpaths, labels=labels, p=2,
                                                  vp=passenger_obj.va, spa=passenger_obj.spa,
                                                  spv=passenger_obj.spv)

        f = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28

        z, v = Assignment.get_alighting_and_boarding(Vij=Vij, hyperpaths=hyperpaths, successors=successors,
                                                     assignment=OD_assignment, f=f)

        lines_travel_time = OperatorsCost.lines_travel_time(routes=network_obj.get_routes(),
                                                            edge_distance=graph_obj.get_edges_distance())

        line_cycle_time = OperatorsCost.get_cycle_time(z, v, network_obj.get_routes(), lines_travel_time)

        self.assertEqual(round(line_cycle_time["F_metro_1"], 7), 0.2500273)
        self.assertEqual(round(line_cycle_time["R_bus_1"], 7), 1.5032033)
        self.assertEqual(line_cycle_time["l1"], 0)

    def test_get_operators_cost(self):
        """
        to test operators cost method
        :return:
        """

        graph_obj = Graph.build_from_parameters(n=2, l=10, g=0.5, p=2)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        network_obj = TransportNetwork(graph_obj=graph_obj)

        feeder_routes_metro = network_obj.get_feeder_routes(mode_obj=metro_obj)
        radial_routes_bus = network_obj.get_radial_routes(mode_obj=bus_obj)

        for route in feeder_routes_metro:
            network_obj.add_route(route)

        for route in radial_routes_bus:
            network_obj.add_route(route)

        f = defaultdict(float)
        k = defaultdict(float)

        line_cycle_time = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28
            k[route.id] = 100
            line_cycle_time[route.id] = 10

        cost = OperatorsCost.get_operators_cost(network_obj.get_routes(), line_cycle_time, f, k)

        self.assertEqual(cost, 75331.2)
