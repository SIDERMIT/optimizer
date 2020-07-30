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

        edge_list = []

        for edge in edges:
            d_e = edges_distance[str(edge.node1.id)][str(edge.node2.id)]
            for mode in list_modes:
                for route in routes:
                    if route.mode == mode:
                        if f[route.id] != 0:
                            node_sequence_i = route.nodes_sequence_i
                            node_sequence_r = route.nodes_sequence_r

                            sum = False
                            for i in range(len(node_sequence_i) - 1):
                                j = i + 1
                                if str(node_sequence_i[i]) == str(edge.node1.id) and str(node_sequence_i[j]) == str(
                                        edge.node2.id) and (str(edge.node1.id), str(edge.node2.id)) not in edge_list:
                                    mode_distance[mode] += d_e * mode.d
                                    edge_list.append((str(edge.node1.id), str(edge.node2.id)))
                                    edge_list.append((str(edge.node2.id), str(edge.node1.id)))
                                    sum = True
                                    break
                            if sum is True:
                                break
                            for i in range(len(node_sequence_r) - 1):
                                j = i + 1
                                if str(node_sequence_r[i]) == str(edge.node1.id) and str(node_sequence_r[j]) == str(
                                        edge.node2.id) and (str(edge.node1.id), str(edge.node2.id)) not in edge_list:
                                    mode_distance[mode] += d_e * mode.d
                                    edge_list.append((str(edge.node1.id), str(edge.node2.id)))
                                    edge_list.append((str(edge.node2.id), str(edge.node1.id)))
                                    sum = True
                                    break
                            if sum is True:
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
