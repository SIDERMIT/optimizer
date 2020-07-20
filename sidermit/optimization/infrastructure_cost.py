from collections import defaultdict

from sidermit.city import Graph
from sidermit.publictransportsystem import TransportNetwork


class InfrastructureCost:
    @staticmethod
    def get_mode_network_distance(graph_obj: Graph, network_obj: TransportNetwork, f):
        """
        to get total distance builded in each transport mode
        :param network_obj:
        :param graph_obj:
        :param f:
        :return:
        """
        edges = graph_obj.get_edges()
        edges_distance = graph_obj.get_edges_distance()

        routes = network_obj.get_routes()
        list_modes = network_obj.get_modes()

        mode_distance = defaultdict(float)

        for edge in edges:
            d_e = edges_distance[str(edge.node1)][str(edge.node2)]
            for mode in list_modes:
                for route in routes:
                    if route.mode == mode:
                        if f[route.id] != 0:
                            mode_distance[mode] += d_e * mode.d
                            break

        return mode_distance

    @staticmethod
    def get_infrastruture_cost(graph_obj: Graph, network_obj: TransportNetwork, f):
        """
        to get infrastruture cost
        :param f:
        :param graph_obj:
        :param network_obj:
        :return:
        """

        infrastruture_cost_obj = InfrastructureCost()

        mode_distance = infrastruture_cost_obj.get_mode_network_distance(graph_obj, network_obj, f)

        CI = 0

        for mode in mode_distance:
            CI += mode.c2 * mode_distance[mode]
        return CI
