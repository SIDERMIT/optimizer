import unittest
from collections import defaultdict

from sidermit.city import Graph
from sidermit.optimization import Constrains
from sidermit.publictransportsystem import TransportMode, TransportNetwork


class test_constrains(unittest.TestCase):

    def test_most_loaded_section_constrains(self):

        graph_obj = Graph.build_from_parameters(2, 10, 1, 2)

        network_obj = TransportNetwork(graph_obj)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()
        radial_bus = network_obj.get_radial_routes(bus_obj)
        feeder_bus = network_obj.get_feeder_routes(bus_obj)
        radial_metro = network_obj.get_radial_routes(metro_obj, short=True)

        for route in radial_bus:
            network_obj.add_route(route)

        for route in feeder_bus:
            network_obj.add_route(route)

        for route in radial_metro:
            network_obj.add_route(route)

        most_loaded_section = defaultdict(float)

        for route in network_obj.get_routes():
            most_loaded_section[route.id] = 10

        ineq_k = Constrains.most_loaded_section_constrains(network_obj.get_routes(), most_loaded_section)

        self.assertEqual(len(ineq_k), 6)

        self.assertEqual(ineq_k, [-150, -150, -150, -150, -1430, -1430])

    def test_fmax_constrains(self):

        graph_obj = Graph.build_from_parameters(2, 10, 1, 2)

        network_obj = TransportNetwork(graph_obj)
        [bus_obj, metro_obj] = TransportMode.get_default_modes()
        radial_bus = network_obj.get_radial_routes(bus_obj)
        feeder_bus = network_obj.get_feeder_routes(bus_obj)
        radial_metro = network_obj.get_radial_routes(metro_obj, short=True)

        for route in radial_bus:
            network_obj.add_route(route)

        for route in feeder_bus:
            network_obj.add_route(route)

        for route in radial_metro:
            network_obj.add_route(route)

        f = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28

        ineq_f = Constrains.fmax_constrains(graph_obj, network_obj.get_routes(), network_obj.get_modes(), f)

        self.assertEqual(ineq_f,
                         [-136.0, -40, -136.0, -40, -143.0, -12.0, -143.0, -12.0, -150, -40, -150, -40, -136.0, -40,
                          -136.0, -40, -143.0, -12.0, -143.0, -12.0])
