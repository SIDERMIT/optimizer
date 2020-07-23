import unittest
from collections import defaultdict

from sidermit.city import Graph, Demand
from sidermit.publictransportsystem import TransportMode, TransportNetwork, Passenger
from sidermit.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.optimization import Constrains


class test_constrains(unittest.TestCase):

    def test_most_loaded_section_constrains(self):

        graph_obj = Graph.build_from_parameters(2, 10, 1, 2)
        demand_obj = Demand.build_from_parameters(graph_obj, 10000, 0.5, 1 / 3, 1 / 3)

        passenger_obj = Passenger.get_default_passenger()
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
        k = defaultdict(float)
        for route in network_obj.get_routes():
            f[route.id] = 28
            k[route.id] = 100

        extended_graph_obj = ExtendedGraph(graph_obj=graph_obj, routes=network_obj.get_routes(), sPTP=passenger_obj.spt,
                                           frequency_routes=None)
        hyperpath_obj = Hyperpath(extended_graph_obj=extended_graph_obj, passenger_obj=passenger_obj)

        hyperpaths, labels, successors, frequency, Vij = hyperpath_obj.get_all_hyperpaths(
            OD_matrix=demand_obj.get_matrix())

        OD_assignment = Assignment.get_assignment(hyperpaths=hyperpaths, labels=labels, p=2,
                                                  vp=passenger_obj.va, spa=passenger_obj.spa,
                                                  spv=passenger_obj.spv)

        z, v = Assignment.get_alighting_and_boarding(Vij=Vij, hyperpaths=hyperpaths, successors=successors,
                                                     assignment=OD_assignment, f=f)

        for route_id in z:
            for direction in z[route_id]:
                for stop_node in z[route_id][direction]:
                    z[route_id][direction][stop_node] = 10

        for route_id in v:
            for direction in v[route_id]:
                for stop_node in v[route_id][direction]:
                    v[route_id][direction][stop_node] = 10

        eq_k, ineq_k = Constrains.most_loaded_section_constrains(network_obj.get_routes(), z, v, k)

        self.assertEqual(len(eq_k), 6)
        self.assertEqual(len(ineq_k), 6)

        self.assertEqual(eq_k, [-90, -90, -90, -90, -90, -90])
        self.assertEqual(ineq_k, [-60, -60, -60, -60, -1340, -1340])

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
