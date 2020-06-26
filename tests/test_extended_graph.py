
import unittest

from sidermit.city import graph
from sidermit.publictransportsystem import TransportNetwork, TransportModeManager, TransportMode
from sidermit.extended_graph import ExtendedGraph


class test_extended_graph(unittest.TestCase):

    def test_build_tree_graph(self):
        """
        test methods get_tree_graph
        :return:
        """
        graph_obj = graph.Graph.build_from_parameters(n=5, l=1000, g=0.5, p=2)
        network = TransportNetwork(graph_obj)

        mode_manager = TransportModeManager()
        bus_obj = mode_manager.get_mode("bus")
        metro_obj = mode_manager.get_mode("metro")
        train_obj = TransportMode("train", 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

        feeder_routes = network.get_feeder_routes(bus_obj)
        radial_routes = network.get_radial_routes(metro_obj)
        circular_routes = network.get_circular_routes(train_obj)

        for route in feeder_routes:
            network.add_route(route)

        for route in radial_routes:
            network.add_route(route)

        for route in circular_routes:
            network.add_route(route)

        city_nodes = ExtendedGraph.build_city_nodes(graph_obj)
        tree_graph = ExtendedGraph.build_tree_graph(network, city_nodes)

        one_stop = []
        two_stop = []
        three_stop = []

        four_route_city = 0
        six_route_city = 0
        ten_route_city = 0

        one_route_stop = 0
        two_route_stop = 0
        ten_route_stop = 0

        for city_node in tree_graph:
            if len(tree_graph[city_node]) == 1:
                one_stop.append(city_node)
            if len(tree_graph[city_node]) == 2:
                two_stop.append(city_node)
            if len(tree_graph[city_node]) == 3:
                three_stop.append(city_node)

            n_routes_city = 0
            for stop in tree_graph[city_node]:
                n_routes_stop = 0
                for _ in tree_graph[city_node][stop]:
                    n_routes_stop = n_routes_stop + 1
                    n_routes_city = n_routes_city + 1

                if n_routes_stop == 1:
                    one_route_stop = one_route_stop + 1
                if n_routes_stop == 2:
                    two_route_stop = two_route_stop + 1
                if n_routes_stop == 10:
                    ten_route_stop = ten_route_stop + 1

            if n_routes_city == 4:
                four_route_city = four_route_city + 1
            if n_routes_city == 6:
                six_route_city = six_route_city + 1
            if n_routes_city == 10:
                ten_route_city = ten_route_city + 1

        self.assertEqual(len(one_stop), 1)
        self.assertEqual(len(two_stop), 5)
        self.assertEqual(len(three_stop), 5)

        self.assertEqual(four_route_city, 5)
        self.assertEqual(six_route_city, 5)
        self.assertEqual(ten_route_city, 1)

        self.assertEqual(one_route_stop, 0)
        self.assertEqual(two_route_stop, 25)
        self.assertEqual(ten_route_stop, 1)
