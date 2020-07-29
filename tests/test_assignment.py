import unittest
from collections import defaultdict

from sidermit.city import Graph, Demand
from sidermit.optimization.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.publictransportsystem import Passenger, TransportMode, TransportNetwork


class test_graph(unittest.TestCase):

    def test_assignment(self):
        """
        test assignment method of class Assignment
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

        nodes = extended_graph_obj.get_extended_graph_nodes()

        P1 = None
        SC1 = None
        CBD = None

        stop_bus_p1 = None
        stop_metro_p1 = None

        for city_node in nodes:
            if city_node.graph_node.name == "P_1":
                P1 = city_node
            if city_node.graph_node.name == "SC_1":
                SC1 = city_node
            if city_node.graph_node.name == "CBD":
                CBD = city_node

            for stop_node in nodes[city_node]:
                if stop_node.mode.name == "bus":
                    if city_node.graph_node.name == "P_1":
                        stop_bus_p1 = stop_node

                if stop_node.mode.name == "metro":
                    if city_node.graph_node.name == "P_1":
                        stop_metro_p1 = stop_node

        self.assertEqual(round(OD_assignment[P1][CBD][stop_bus_p1], 2), 100)
        self.assertEqual(round(OD_assignment[P1][SC1][stop_bus_p1], 2), 49.88)
        self.assertEqual(round(OD_assignment[P1][SC1][stop_metro_p1], 2), 50.12)

    def test_get_alighting_and_boarding(self):
        """
        to test get_alighting_and_boarding of class get_alighting_and_boarding
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

        nodes = extended_graph_obj.get_extended_graph_nodes()

        stop_bus_p1 = None
        stop_bus_sc1 = None
        stop_bus_cbd = None

        stop_metro_p1 = None
        stop_metro_sc1 = None

        for city_node in nodes:
            for stop_node in nodes[city_node]:
                if stop_node.mode.name == "bus":
                    if city_node.graph_node.name == "P_1":
                        stop_bus_p1 = stop_node
                    if city_node.graph_node.name == "SC_1":
                        stop_bus_sc1 = stop_node
                    if city_node.graph_node.name == "CBD":
                        stop_bus_cbd = stop_node
                if stop_node.mode.name == "metro":
                    if city_node.graph_node.name == "P_1":
                        stop_metro_p1 = stop_node
                    if city_node.graph_node.name == "SC_1":
                        stop_metro_sc1 = stop_node

        self.assertEqual(round(z["R_bus_1"]["I"][stop_bus_p1], 2), 0.74)
        self.assertEqual(round(z["R_bus_1"]["I"][stop_bus_sc1], 2), 0.89)
        self.assertEqual(round(z["R_bus_1"]["R"][stop_bus_cbd], 2), 0.74)
        self.assertEqual(round(v["R_bus_1"]["I"][stop_bus_cbd], 2), 1.49)
        self.assertEqual(round(v["R_bus_1"]["I"][stop_bus_sc1], 2), 0.15)
        self.assertEqual(round(v["R_bus_1"]["R"][stop_bus_sc1], 2), 0.74)
        self.assertEqual(round(z["F_metro_1"]["I"][stop_metro_p1], 2), 0.15)
        self.assertEqual(round(v["F_metro_1"]["I"][stop_metro_sc1], 2), 0.15)
        self.assertEqual(round(z["F_metro_1"]["R"][stop_metro_sc1], 2), 0)
