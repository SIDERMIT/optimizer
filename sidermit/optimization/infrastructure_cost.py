from collections import defaultdict

from sidermit.city import Graph
from sidermit.publictransportsystem import TransportNetwork

defaultdict_float = defaultdict(float)


class InfrastructureCost:
    @staticmethod
    def get_mode_network_distance(graph_obj: Graph, network_obj: TransportNetwork,
                                  f: defaultdict_float) -> defaultdict_float:
        """
        to get total distance builded in each transport mode
        :param network_obj: TransportNetwork object
        :param graph_obj: Graph object
        :param f: dict with frequency for each route_id
        :return: ddict with total distance for each mode in transport network
        """
        edges = graph_obj.get_edges()
        edges_distance = graph_obj.get_edges_distance()

        routes = network_obj.get_routes()
        list_modes = network_obj.get_modes()

        mode_distance = defaultdict(float)

        edge_list = []

        for edge in edges:
            d_e = edges_distance[edge.node1.id][edge.node2.id]
            for mode in list_modes:
                for route in routes:
                    if route.mode == mode:
                        if f[route.id] != 0:
                            node_sequence_i = route.nodes_sequence_i
                            node_sequence_r = route.nodes_sequence_r

                            ver_sum = False
                            for i in range(len(node_sequence_i) - 1):
                                j = i + 1
                                if node_sequence_i[i] == edge.node1.id and node_sequence_i[j] == edge.node2.id and (
                                edge.node1.id, edge.node2.id) not in edge_list:
                                    mode_distance[mode] += d_e * mode.d
                                    edge_list.append((edge.node1.id, edge.node2.id))
                                    edge_list.append((edge.node2.id, edge.node1.id))
                                    ver_sum = True
                                    break
                            if ver_sum is True:
                                break
                            for i in range(len(node_sequence_r) - 1):
                                j = i + 1
                                if node_sequence_r[i] == edge.node1.id and node_sequence_r[j] == edge.node2.id and (
                                edge.node1.id, edge.node2.id) not in edge_list:
                                    mode_distance[mode] += d_e * mode.d
                                    edge_list.append((edge.node1.id, edge.node2.id))
                                    edge_list.append((edge.node2.id, edge.node1.id))
                                    ver_sum = True
                                    break
                            if ver_sum is True:
                                break

        return mode_distance

    @staticmethod
    def get_infrastruture_cost(graph_obj: Graph, network_obj: TransportNetwork, f: defaultdict_float) -> float:
        """
        to get infrastruture cost
        :param network_obj: TransportNetwork object
        :param graph_obj: Graph object
        :param f: dict with frequency for each route_id
        :return: infrastruture cost
        """

        infrastruture_cost_obj = InfrastructureCost()

        mode_distance = infrastruture_cost_obj.get_mode_network_distance(graph_obj, network_obj, f)

        CI = 0

        for mode in mode_distance:
            CI += mode.c2 * mode_distance[mode]
        return CI
