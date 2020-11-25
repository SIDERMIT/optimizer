from collections import defaultdict
from typing import List

import networkx as nx
from matplotlib import pyplot as plt

from sidermit.exceptions import *
from sidermit.optimization.preoptimization import ExtendedGraph, CityNode, StopNode, RouteNode, ExtendedEdgesType, \
    ExtendedEdge, ExtendedNode
from sidermit.publictransportsystem import Passenger, TransportModeManager

defaultdict2_float = defaultdict(lambda: defaultdict(float))
list_suc = defaultdict(List[ExtendedEdge])
list_lab = defaultdict(float)
list_f = defaultdict(float)
list_elemental_path = List[ExtendedNode]
defaultdict_elemental_path = defaultdict(List[list_elemental_path])

dic_hyperpaths = defaultdict(lambda: defaultdict(lambda: defaultdict(List[list_elemental_path])))
dic_labels = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_successors = defaultdict(lambda: defaultdict(lambda: defaultdict(List[ExtendedEdge])))
dic_frequency = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_Vij = defaultdict(lambda: defaultdict(float))


class Hyperpath:

    def __init__(self, extended_graph_obj: ExtendedGraph, passenger_obj: Passenger):
        """
        class to Hyperpath algorithm
        :param extended_graph_obj: ExtendedGraph object
        :param passenger_obj: Passenger object
        """
        self.extended_graph_obj = extended_graph_obj
        self.passenger_obj = passenger_obj

    def network_validator(self, OD_matrix: defaultdict2_float) -> bool:
        """
        to check if Transport network is well defined for all pairs OD with trips. This must has at least a route for
        each OD pair with trips. Also this must has until 2 TransportMode and at least one has parameter d=1.
        :param OD_matrix: OD matrix get from Demand object
        :return: True if all OD pairs with trips have at least one path between origin and destination. False if not.
        """
        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        # to check a path between all OD pair with trips
        for origin_id in OD_matrix:
            for destination_id in OD_matrix[origin_id]:
                vij = OD_matrix[origin_id][destination_id]
                if vij != 0:
                    origin = None
                    destination = None
                    for city_node in nodes:
                        if str(origin_id) == str(city_node.graph_node.id):
                            origin = city_node
                        if str(destination_id) == str(city_node.graph_node.id):
                            destination = city_node

                    _, label, _ = self.build_hyperpath_graph(origin, destination)

                    # if there is a stop with a label != infinity, you can get from the origin to the destination
                    conection = False
                    for stop in nodes[origin]:
                        if label[stop] != float('inf'):
                            conection = True
                            break
                    if conection is False:
                        raise TransportNetworkException(
                            "par OD {}-{} without connection".format(origin_id, destination_id))
        # to check network must has until 2 TransportMode
        list_mode = []
        for city_node in nodes:
            for stop in nodes[city_node]:
                if stop.mode not in list_mode:
                    list_mode.append(stop.mode)

        mode_manager = TransportModeManager(add_default_mode=False)

        for mode in list_mode:
            mode_manager.add_mode(mode)

        return mode_manager.is_valid_to_assignment_step()

    def build_hyperpath_graph(self, node_city_origin: CityNode, node_city_destination: CityNode) -> (
            list_suc, list_lab, list_f):
        """
        build the entire graph to connect the origin and destination with the hyperpath algorithm
        :param node_city_origin: origin CityNode
        :param node_city_destination: destination CityNode
        :return: successors , label, frequencies
        """

        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        edges = self.extended_graph_obj.get_extended_graph_edges()

        # we initialize node labels at infinity except for the destination with label 0
        labels = defaultdict(float)
        labels_inf = defaultdict(float)
        # successors will be initialized empty
        successor = defaultdict(list)
        successor_inf = defaultdict(None)
        # frequency will be initialized to zero
        frequencies = defaultdict(float)
        # list of processed nodes (with calculated strategy)
        S = []

        # we initialize parameters
        # number of nodes in the extended graph
        n_nodes = 0
        for city_node in nodes:
            if city_node == node_city_destination:
                labels[city_node] = 0
                labels_inf[city_node] = 0
                frequencies[city_node] = 0
                n_nodes = n_nodes + 1
            else:
                labels[city_node] = float('inf')
                labels_inf[city_node] = float('inf')
                frequencies[city_node] = 0
                n_nodes = n_nodes + 1
            for stop_node in nodes[city_node]:
                labels[stop_node] = float('inf')
                labels_inf[stop_node] = float('inf')
                frequencies[stop_node] = 0
                n_nodes = n_nodes + 1
                for route_node in nodes[city_node][stop_node]:
                    labels[route_node] = float('inf')
                    labels_inf[route_node] = float('inf')
                    frequencies[route_node] = 0
                    n_nodes = n_nodes + 1

        # while there are nodes that have not been processed
        while len(S) != n_nodes:
            # we find node with minimum label and that does not belong to S
            min_label_node = None
            min_label = float('inf')
            for node in labels:
                if node not in S:
                    if min(labels[node], labels_inf[node]) < min_label:
                        min_label = min(labels[node], labels_inf[node])
                        min_label_node = node
            # node to be processed, initially equals destination
            j = min_label_node
            # update S
            S.append(j)
            # we must find all edges that end in j and whose beginning is not in S
            edge_j = []
            for edge in edges:
                # we will remove the edges of access to the CityNode of origin
                # because each StopNode in origin must have its own hyperpath
                if edge.nodei == node_city_origin:
                    continue
                if edge.nodej == node_city_origin:
                    continue
                if edge.nodei not in S and edge.nodej == j:
                    edge_j.append(edge)

            # for edges we update the label of the origin node as: labeli = labelj + time_arco ij
            for edge in edge_j:
                # not to consider transfer penalty at origin and include a penalty of access time
                edge_t = edge.t
                if edge.type == ExtendedEdgesType.ALIGHTING:
                    if edge.nodej.city_node == node_city_destination:
                        edge_t = 0
                if edge.type == ExtendedEdgesType.ACCESS:
                    edge_t = edge.t * self.passenger_obj.pa / self.passenger_obj.pv

                # equivalent to ~t_a
                t_i = edge_t + min(labels[j], labels_inf[j])
                i = edge.nodei

                # for all types of edges except boarding
                if edge.f == float('inf') and t_i < labels_inf[i]:
                    successor_inf[i] = edge
                    labels_inf[i] = t_i

                # for  boarding edges
                if edge.f < float('inf') and t_i < labels[i]:
                    theta = i.mode.theta

                    # initial case
                    if frequencies[i] == 0 and labels[i] == float('inf') and edge.f != 0:
                        # print(edge.type)
                        successor[i].append(edge)
                        labels[i] = (theta * self.passenger_obj.pw / self.passenger_obj.pv + edge.f * t_i) / edge.f
                        frequencies[i] = frequencies[i] + edge.f
                    # previously assigned label
                    else:
                        if edge.f != 0:
                            successor[i].append(edge)
                            labels[i] = (frequencies[i] * labels[i] + edge.f * t_i) / (frequencies[i] + edge.f)
                            frequencies[i] = frequencies[i] + edge.f

                # we verify that all the successors of i remain optimal
                for edge_b in successor[i]:
                    if edge_b == edge:
                        continue
                    # not to consider transfer penalty at origin and include a penalty of access time
                    edge_b_t = edge_b.t
                    if edge_b.type == ExtendedEdgesType.ALIGHTING:
                        if edge.nodej.city_node == node_city_destination:
                            edge_b_t = 0
                    if edge_b.type == ExtendedEdgesType.ACCESS:
                        edge_b_t = edge_b.t * self.passenger_obj.pa / self.passenger_obj.pv

                    # equivalent to ~t_b
                    t_ib = min(labels[edge_b.nodej], labels_inf[edge_b.nodej]) + edge_b_t

                    # remove sub optimal edge in the successors list
                    if t_ib >= labels[i]:
                        successor[i].remove(edge_b)
                        labels[i] = (frequencies[i] * labels[i] - edge_b.f * t_ib) / (frequencies[i] - edge_b.f)
                        frequencies[i] = frequencies[i] - edge_b.f

        # we reduce successor lists and labels to a single list
        successors = defaultdict(list)
        label = defaultdict(float)

        for city_node in nodes:
            if labels[city_node] < labels_inf[city_node]:
                label[city_node] = labels[city_node]
                for suc in successor[city_node]:
                    successors[city_node].append(suc)
            else:
                label[city_node] = labels_inf[city_node]

                if successor_inf.get(city_node):
                    successors[city_node].append(successor_inf[city_node])

            for stop_node in nodes[city_node]:
                if labels[stop_node] < labels_inf[stop_node]:
                    label[stop_node] = labels[stop_node]
                    if city_node == node_city_origin:
                        label[stop_node] = labels[
                                               stop_node] + stop_node.mode.tat / 60 * self.passenger_obj.pa / self.passenger_obj.pv
                    for suc in successor[stop_node]:
                        successors[stop_node].append(suc)
                else:
                    label[stop_node] = labels_inf[stop_node]
                    if city_node == node_city_origin:
                        label[stop_node] = labels_inf[
                                               stop_node] + stop_node.mode.tat / 60 * self.passenger_obj.pa / self.passenger_obj.pv

                    if successor_inf.get(stop_node):
                        successors[stop_node].append(successor_inf[stop_node])
                for route_node in nodes[city_node][stop_node]:
                    if labels[route_node] < labels_inf[route_node]:
                        label[route_node] = labels[route_node]
                        for suc in successor[route_node]:
                            successors[route_node].append(suc)
                    else:
                        label[route_node] = labels_inf[route_node]
                        if successor_inf.get(route_node):
                            successors[route_node].append(successor_inf[route_node])

        return successors, label, frequencies

    @staticmethod
    def string_hyperpath_graph(successors: list_suc, label: list_lab, frequencies: list_f) -> str:
        """
        String with the representation of the hyperpath graph
        :param successors: dic[ExtendedNode] = List[ExtendedNode]. Dictionary that gives the relation of successor
        nodes in the hyperpath
        :param label: dic[ExtendedNode] = label. Dictionary that gives the label for each ExtendedNode in hours
        with weight equivalent to the travel time
        :param frequencies: dic[ExtendedNode] = frequency. Dictionary that gives the cumulative frequency of all
        successors for each ExtendedNode
        :return: String with the representation of the hyperpath graph
        """
        line = "HyperPath Graph\n"
        for node in label:

            line_frequency = frequencies[node]

            line_successor = ""

            for suc in successors[node]:
                nodei = suc.nodei
                nodej = suc.nodej
                linei = ""
                linej = ""
                if isinstance(nodei, CityNode):
                    linei += "Citynode: {}".format(nodei.graph_node.name)
                if isinstance(nodei, StopNode):
                    linei += "Stopnode {}: {}".format(nodei.mode.name, nodei.city_node.graph_node.name)
                if isinstance(nodei, RouteNode):
                    linei += "Routenode {} {}: {}".format(nodei.route.id, nodei.direction,
                                                          nodei.stop_node.city_node.graph_node.name)
                if isinstance(nodej, CityNode):
                    linej += "Citynode: {}".format(nodej.graph_node.name)
                if isinstance(nodej, StopNode):
                    linej += "Stopnode {}: {}".format(nodej.mode.name, nodej.city_node.graph_node.name)
                if isinstance(nodej, RouteNode):
                    linej += "Routenode {} {}: {}".format(nodej.route.id, nodej.direction,
                                                          nodej.stop_node.city_node.graph_node.name)

                line_successor += "[{}: {} - {}] ".format(suc.type, linei, linej)

            if isinstance(node, CityNode):
                line += "City_node\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {:.2f}\n".format(
                    node.graph_node.name, label[node], line_successor, line_frequency)
            if isinstance(node, StopNode):
                line += "Stop_node\n\t-Mode_name: {}\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {:.2f}\n".format(
                    node.mode.name, node.city_node.graph_node.name, label[node], line_successor, line_frequency)
            if isinstance(node, RouteNode):
                line += "Route_node\n\t-route_id: {}\n\t-direction: {}\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {:.2f}\n".format(
                    node.route.id, node.direction, node.stop_node.city_node.graph_node.name,
                    label[node], line_successor, line_frequency)
        return line

    def get_hyperpath_OD(self, origin: CityNode, destination: CityNode) -> (
            defaultdict_elemental_path, list_lab, list_suc):
        """
        to get all elemental path for each StopNode in Origin
        :param origin: CityNode origin
        :param destination: CityNode destination
        :return: (Dic[TransportMode] = List[List[ExtendedNodes]], dic[ExtendedNode] = Label, dic[ExtendedNode] =
        List[ExtendedEdge]). Each List[ExtendedNodes] represent a elemental path to connect origin and destination.
        List[ExtendedEdge] represent all successors edge for each ExtendedNode.
        """
        # we run hyperpath algorithm
        successors, label, frequencies = self.build_hyperpath_graph(origin, destination)

        nodes = self.extended_graph_obj.get_extended_graph_nodes()

        # dictionary with key: TransportMode and value all elemental path associated
        hyperpaths_od = defaultdict(list)

        # for each StopNode in Origin
        for stop in nodes[origin]:
            # hyperpath in the StopNode
            hyperpath_stop = [[origin, stop]]
            # we initialize hyperpath

            while True:
                # stop condition that each elemental path has reached the destination
                end = True
                for path in hyperpath_stop:
                    # there is a elemental path that has not reached the destination
                    if path[len(path) - 1] != destination:
                        end = False
                        break
                if end:
                    break

                new_hyperpath_stop = []
                # we add successors of those paths that have not reached the destination
                for path in hyperpath_stop:
                    # elemental path that has not reached the destination
                    if path[len(path) - 1] != destination:
                        # we add new elemental path as successors have the last node of the path analyzed
                        for suc in successors[path[len(path) - 1]]:
                            new_path = []
                            new_path.extend(path)
                            new_path.append(suc.nodej)
                            new_hyperpath_stop.append(new_path)
                    # path that arrived at destination
                    else:
                        new_hyperpath_stop.append(path)
                hyperpath_stop = new_hyperpath_stop

            for elemental_path in hyperpath_stop:
                hyperpaths_od[stop].append(elemental_path)

        return hyperpaths_od, label, successors, frequencies

    @staticmethod
    def string_hyperpaths_OD(hyperpaths_od: defaultdict_elemental_path, label: list_lab) -> str:
        """
        String with the representation of the hyperpath for a OD pair
        :param hyperpaths_od: Dic[TransportMode] = List[List[ExtendedNodes]]. Each List[ExtendedNodes] represent a elemental
        path to connect a origin and destination.
        :param label: dic[ExtendedNode] = label. Dictionary that gives the label for each ExtendedNode in hours
        with weight equivalent to the travel time
        :return: String with the representation of the hyperpath for a OD pair
        """
        line = ""
        for stop in hyperpaths_od:
            line += "\n{} stop\n".format(stop.mode.name)
            for path in hyperpaths_od[stop]:
                line += "\n\tNew Path:\n\t\t"
                for node in path:
                    if isinstance(node, CityNode):
                        line += "[City_node {}: {:.4f}]\n\t\t".format(node.graph_node.name, label[node])
                    if isinstance(node, StopNode):
                        line += "[Stop_node {} - {}: {:.4f}]\n\t\t".format(node.mode.name,
                                                                           node.city_node.graph_node.name, label[node])
                    if isinstance(node, RouteNode):
                        line += "[Route_node {} {} - {}: {:.4f}]\n\t\t".format(node.route.id, node.direction,
                                                                               node.stop_node.city_node.graph_node.name,
                                                                               label[node])
        return line

    def get_all_hyperpaths(self, OD_matrix: defaultdict2_float) -> (
            dic_hyperpaths, dic_labels, dic_successors, dic_frequency, dic_Vij):
        """
        get information about all hyperpath and label for all OD pair with trips in OD matrix
        :param OD_matrix:  OD matrix get from Demand object
        :return: (Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]],
        dic[origin: CityNode][destination: CityNode][ExtendedNode] = Label, dic[origin: CityNode][destination: CityNode]
        [ExtendedNode] = List[ExtendedEdge], dic[origin: CityNode][destination: CityNode][ExtendedNode] = float [veh/hr]
        , dic[origin][destination] = vij). Each List[ExtendedNodes] represent a elemental path to connect a origin
        and destination. List[ExtendedEdge] represent all successors edge for each ExtendedNode in a OD pair.
        """
        hyperpaths = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        labels = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        successors = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        frequency = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        Vij = defaultdict(lambda: defaultdict(list))

        nodes = self.extended_graph_obj.get_extended_graph_nodes()

        if self.network_validator(OD_matrix):
            for origin_id in OD_matrix:
                for destination_id in OD_matrix[origin_id]:
                    vij = OD_matrix[origin_id][destination_id]
                    if vij != 0:
                        origin = None
                        destination = None
                        for city_node in nodes:
                            if str(origin_id) == str(city_node.graph_node.id):
                                origin = city_node
                            if str(destination_id) == str(city_node.graph_node.id):
                                destination = city_node

                        hyperpaths_od, label, successor, frequencies = self.get_hyperpath_OD(origin, destination)

                        for city_node in nodes:
                            labels[origin][destination][city_node] = label[city_node]
                            for stop_node in nodes[city_node]:
                                labels[origin][destination][stop_node] = label[stop_node]
                                for route_node in nodes[city_node][stop_node]:
                                    labels[origin][destination][route_node] = label[route_node]

                        for city_node in nodes:
                            for suc in successor[city_node]:
                                successors[origin][destination][city_node].append(suc)
                            for stop_node in nodes[city_node]:
                                for suc in successor[stop_node]:
                                    successors[origin][destination][stop_node].append(suc)
                                for route_node in nodes[city_node][stop_node]:
                                    for suc in successor[route_node]:
                                        successors[origin][destination][route_node].append(suc)

                        for city_node in nodes:
                            frequency[origin][destination][city_node] = frequencies[city_node]
                            for stop_node in nodes[city_node]:
                                frequency[origin][destination][stop_node] = frequencies[stop_node]
                                for route_node in nodes[city_node][stop_node]:
                                    frequency[origin][destination][route_node] = frequencies[route_node]

                        for stop in hyperpaths_od:
                            for elemental_path in hyperpaths_od[stop]:
                                hyperpaths[origin][destination][stop].append(elemental_path)

                        Vij[origin][destination] = vij

        else:
            raise TransportNetworkIsNotValidException("Network is not valid")

        return hyperpaths, labels, successors, frequency, Vij

    @staticmethod
    def string_all_hyperpaths(hyperpaths: dic_hyperpaths, labels: dic_labels, successors: dic_successors,
                              vij: dic_Vij) -> str:
        """
        to get a string with a summary of the all hyperpaths for all OD pair with trips.
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]]
        :param labels: dic[origin: CityNode][destination: CityNode][ExtendedNode] = Label
        :param successors: dic[origin: CityNode][destination: CityNode][ExtendedNode] = List[ExtendedEdge]
        :param vij: dic[origin: CityNode][destination: CityNode] = vij
        :return: string with a summary of the all hyperpaths for all OD pair with trips.
        """

        line = "\n"

        for origin in hyperpaths:
            for destination in hyperpaths[origin]:
                for stop in hyperpaths[origin][destination]:
                    line += "origin: {}, destination: {}, vij: {:.2f}\n\t mode: {}, label: {:.2f} [EIV], n° elemental paths: {}, n° elemental paths (successors): {}\n".format(
                        origin.graph_node.name,
                        destination.graph_node.name,
                        vij[origin][destination],
                        stop.mode.name, labels[origin][destination][stop],
                        len(hyperpaths[origin][
                                destination][stop]), len(successors[origin][destination][stop]))

        return line

    @staticmethod
    def plot(hyperpaths_od: defaultdict_elemental_path):
        """
        plot alls hyperpaths for a OD pair
        :param hyperpaths_od: Dic[TransportMode] = List[List[ExtendedNodes]]. Each List[ExtendedNodes] represent a
        elemental path to connect origin and destination.
        :return:
        """
        city_nodes = []
        stop_nodes = []
        route_nodes = []
        edges_graph = []
        for stop in hyperpaths_od:
            for path in hyperpaths_od[stop]:
                prev_node = None
                for node in path:
                    if isinstance(node, CityNode):
                        city_nodes.append(node.graph_node.name)
                        if prev_node is None:
                            prev_node = node.graph_node.name
                        else:
                            edges_graph.append((prev_node, node.graph_node.name))
                            prev_node = node.graph_node.name
                    if isinstance(node, StopNode):
                        stop_nodes.append("{} - {}".format(node.mode.name, node.city_node.graph_node.name))
                        if prev_node is None:
                            prev_node = "{} - {}".format(node.mode.name, node.city_node.graph_node.name)
                        else:
                            edges_graph.append(
                                (prev_node, "{} - {}".format(node.mode.name, node.city_node.graph_node.name)))
                            prev_node = "{} - {}".format(node.mode.name, node.city_node.graph_node.name)

                    if isinstance(node, RouteNode):
                        route_nodes.append("{} {} - {}".format(node.route.id, node.direction,
                                                               node.stop_node.city_node.graph_node.name))
                        if prev_node is None:
                            prev_node = "{} {} - {}".format(node.route.id, node.direction,
                                                            node.stop_node.city_node.graph_node.name)
                        else:
                            edges_graph.append((prev_node, "{} {} - {}".format(node.route.id, node.direction,
                                                                               node.stop_node.city_node.graph_node.name)))
                            prev_node = "{} {} - {}".format(node.route.id, node.direction,
                                                            node.stop_node.city_node.graph_node.name)

        G = nx.DiGraph()
        G.add_nodes_from(city_nodes)
        G.add_nodes_from(stop_nodes)
        G.add_nodes_from(route_nodes)
        G.add_edges_from(edges_graph)
        pos = nx.spring_layout(G, scale=10)  # positions for all nodes

        # nx.draw(G)
        # # separate calls to draw labels, nodes and edges
        # # plot p, Sc and CBD
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('Set2'), nodelist=city_nodes, node_color='yellow',
                               node_size=200)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('Set2'), nodelist=stop_nodes, node_color='red',
                               node_size=200)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('Set2'), nodelist=route_nodes, node_color='green',
                               node_size=200)
        # # plot labels
        nx.draw_networkx_labels(G, pos, font_size=6)
        # # plot edges city
        nx.draw_networkx_edges(G, pos, edgelist=edges_graph, edge_color='orange', arrows=True)

        plt.title("City graph")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().set_aspect('equal')
        plt.show()
        # plt.savefig(file_path)
