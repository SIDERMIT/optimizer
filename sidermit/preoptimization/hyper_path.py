from collections import defaultdict

import networkx as nx
from matplotlib import pyplot as plt

from sidermit.publictransportsystem import Passenger
from sidermit.preoptimization import ExtendedGraph, CityNode, StopNode, RouteNode, ExtendedEdgesType


class Hyperpath:

    def __init__(self, extended_graph_obj: ExtendedGraph, passenger_obj: Passenger):
        """
        class to Hyperpath algorithm
        :param extended_graph_obj: ExtendedGraph object
        :param passenger_obj: Passenger object
        """
        self.extended_graph_obj = extended_graph_obj
        self.passenger_obj = passenger_obj

    def network_validator(self, matrixOD):
        """
        to check if Transport network is well defined for all pairs OD with trips.
        :param matrixOD: OD matrix get from Demand object
        :return: True if all OD pairs with trips have at least one path between origin and destination. False if not.
        """

        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        for origin_id in matrixOD:
            for destination_id in matrixOD[origin_id]:
                vij = matrixOD[origin_id][destination_id]
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
                        return False
        return True

    def build_hyperpath_graph(self, node_city_origin: CityNode, node_city_destination: CityNode):
        """
        build the entire graph to connect the origin and destination with the hyperpath algorithm
        :param node_city_origin: origin CityNode
        :param node_city_destination: destination CityNode
        :return: successors, label, frequencies
        """

        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        edges = self.extended_graph_obj.get_extended_graph_edges()

        # we will remove the edges of access to the CityNode of origin
        # because each StopNode in origin must have its own hyperpath
        for edge in edges:

            if edge.nodei == node_city_origin:
                edges.remove(edge)

            if edge.nodej == node_city_origin:
                edges.remove(edge)

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
                if edge.nodei not in S and edge.nodej == j:
                    edge_j.append(edge)

            # for edges we update the label of the origin node as: labeli = labelj + time_arco ij
            for edge in edge_j:
                # not to consider transfer penalty at origin and include a penalty of access time
                edge_t = edge.t
                if edge.type == ExtendedEdgesType.ALIGHTING:
                    if edge.nodej.city_node == node_city_origin:
                        edge_t = 0
                if edge.type == ExtendedEdgesType.ACCESS:
                    edge_t = edge.t * self.passenger_obj.spa / self.passenger_obj.spv

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
                    if frequencies[i] == 0 and labels[i] == float('inf'):
                        # print(edge.type)
                        successor[i].append(edge)
                        labels[i] = (theta * self.passenger_obj.spw / self.passenger_obj.spv + edge.f * t_i) / (edge.f)
                        frequencies[i] = frequencies[i] + edge.f
                    # previously assigned label
                    else:
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
                        if edge.nodej.city_node == node_city_origin:
                            edge_b_t = 0
                    if edge_b.type == ExtendedEdgesType.ACCESS:
                        edge_b_t = edge_b.t * self.passenger_obj.spa / self.passenger_obj.spv

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
                    for suc in successor[stop_node]:
                        successors[stop_node].append(suc)
                else:
                    label[stop_node] = labels_inf[stop_node]
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
    def string_hyperpath_graph(successors, label, frequencies):
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
                line += "City_node\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.graph_node.name, label[node], line_successor, line_frequency)
            if isinstance(node, StopNode):
                line += "Stop_node\n\t-Mode_name: {}\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.mode.name, node.city_node.graph_node.name, label[node], line_successor, line_frequency)
            if isinstance(node, RouteNode):
                line += "Route_node\n\t-route_id: {}\n\t-direction: {}\n\t-Graph_node_name: {}\n\t-label: {:.2f}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.route.id, node.direction, node.stop_node.city_node.graph_node.name,
                    label[node], line_successor, line_frequency)
        return line

    def get_hyperpath_OD(self, origin, destination):
        """
        to get all elemental path for each StopNode in Origin
        :param origin: CityNode origin
        :param destination: CityNode destination
        :return: List[List[List[ExtendedNodes]]]. Each List[ExtendedNodes] represent a elemental path to connect
        origin and destination and List[List[ExtendedNodes]] represent a hyperpath in a StopNode of the origin.
        """
        # we run hyperpath algorithm
        successors, label, frequencies = self.build_hyperpath_graph(origin, destination)

        nodes = self.extended_graph_obj.get_extended_graph_nodes()

        # list with hyperpath of each StopNode in the origin
        hyperpaths = []

        # for each StopNode in Origin
        for stop in nodes[origin]:
            # hyperpath in the StopNode
            hyperpath_stop = []
            # we initialize hyperpath
            hyperpath_stop.append([origin, stop])

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
                            for n in path:
                                new_path.append(n)
                            new_path.append(suc.nodej)
                            new_hyperpath_stop.append(new_path)
                    # path that arrived at destination
                    else:
                        new_hyperpath_stop.append(path)
                hyperpath_stop = new_hyperpath_stop
            hyperpaths.append(hyperpath_stop)

        return hyperpaths

    @staticmethod
    def string_hyperpaths_OD(hyperpaths_od, label):
        """
        String with the representation of the hyperpath for a OD pair
        :param hyperpaths_od: List[List[List[ExtendedNodes]]]. Each List[ExtendedNodes] represent a elemental path to
        connect origin and destination and List[List[ExtendedNodes]] represent a hyperpath in a StopNode of the origin.
        :param label: dic[ExtendedNode] = label. Dictionary that gives the label for each ExtendedNode in hours
        with weight equivalent to the travel time
        :return: String with the representation of the hyperpath for a OD pair
        """
        line = ""
        for hyperpath_stop in hyperpaths_od:
            line += "\n{} stop\n".format(hyperpath_stop[0][1].mode.name)
            for path in hyperpath_stop:
                line += "\n\tNew Path:\n\t\t"
                for node in path:
                    if isinstance(node, CityNode):
                        line += "[City_node {}: {:.2f}]\n\t\t".format(node.graph_node.name, label[node])
                    if isinstance(node, StopNode):
                        line += "[Stop_node {} - {}: {:.2f}]\n\t\t".format(node.mode.name,
                                                                           node.city_node.graph_node.name, label[node])
                    if isinstance(node, RouteNode):
                        line += "[Route_node {} {} - {}: {:.2f}]\n\t\t".format(node.route.id, node.direction,
                                                                               node.stop_node.city_node.graph_node.name,
                                                                               label[node])
        return line

    @staticmethod
    def plot(hyperpaths_od):
        """
        plot alls hyperpaths for a OD pair
        :param hyperpaths_od: List[List[List[ExtendedNodes]]]. Each List[ExtendedNodes] represent a elemental path to
        connect origin and destination and List[List[ExtendedNodes]] represent a hyperpath in a StopNode of the origin.
        :return:
        """
        city_nodes = []
        stop_nodes = []
        route_nodes = []
        edges_graph = []
        for hyperpath_stop in hyperpaths_od:
            for path in hyperpath_stop:
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
