import unittest
from collections import defaultdict

from sidermit.city import Demand
from sidermit.city import Graph
from sidermit.optimization import UsersCost
from sidermit.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.publictransportsystem import TransportMode, TransportNetwork, Passenger


class test_users_cost(unittest.TestCase):

    def test_resources_consumer(self):

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

        CU_obj = UsersCost()
        ta, te, tv, t = CU_obj.resources_consumer(hyperpaths, Vij, OD_assignment, successors, extended_graph_obj, f)

        self.assertEqual(round(ta, 4), 0.1726)
        self.assertEqual(round(te, 4), 3.4820)
        self.assertEqual(round(tv, 4), 73.9559)
        self.assertEqual(round(t, 4), 41.6667)

    def test_user_cost(self):
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

        CU_obj = UsersCost()
        CU = CU_obj.get_users_cost(hyperpaths, Vij, OD_assignment, successors, extended_graph_obj, f, passenger_obj)

        self.assertEqual(round(CU, 4), 889.8055)
