import unittest
from collections import defaultdict

from sidermit.city import Graph
from sidermit.optimization import InfrastructureCost
from sidermit.publictransportsystem import TransportMode, TransportNetwork


class test_infrastructure_cost(unittest.TestCase):

    def test_get_mode_network_distance(self):

        graph_obj = Graph.build_from_parameters(2, 10, 1, 2)
        network_obj = TransportNetwork(graph_obj)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        CI_obj = InfrastructureCost()

        circular = network_obj.get_circular_routes(mode_obj=metro_obj)
        radial = network_obj.get_radial_routes(mode_obj=bus_obj)

        for route in circular:
            network_obj.add_route(route)

        for route in radial:
            network_obj.add_route(route)

        f = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28

        mode_distance = CI_obj.get_mode_network_distance(graph_obj, network_obj, f=f)

        self.assertEqual(mode_distance[bus_obj], 160)
        self.assertEqual(mode_distance[metro_obj], 20)

    def test_get_infrastruture_cost(self):

        graph_obj = Graph.build_from_parameters(2, 10, 1, 2)
        network_obj = TransportNetwork(graph_obj)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()

        CI_obj = InfrastructureCost()

        circular = network_obj.get_circular_routes(mode_obj=metro_obj)
        radial = network_obj.get_radial_routes(mode_obj=bus_obj)

        for route in circular:
            network_obj.add_route(route)

        for route in radial:
            network_obj.add_route(route)

        f = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28

        CI = CI_obj.get_infrastruture_cost(graph_obj, network_obj, f=f)

        self.assertEqual(CI, 18663.0)
