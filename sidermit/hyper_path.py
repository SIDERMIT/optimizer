from collections import defaultdict

import networkx as nx
from matplotlib import pyplot as plt

from sidermit.extended_graph import CityNode, StopNode, RouteNode, ExtendedEdgesType


class Hyperpath:

    def __init__(self, extended_graph_obj, passenger_obj):
        self.extended_graph_obj = extended_graph_obj
        self.passenger_obj = passenger_obj

    def network_validator(self, matrixOD):

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

                    # si hay una parada con etiqueta distinta de infinito se puede llegar desde el origen al destino
                    conection = False
                    for stop in nodes[origin]:
                        if label[stop] != float('inf'):
                            conection = True
                            break
                    if conection is False:
                        return False
        return True

    @staticmethod
    def string_hyperpath_graph(successors, label, frequencies):
        line = "HyperPath\n"
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

    def build_hyperpath_graph(self, node_city_origin, node_city_destination):

        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        edges = self.extended_graph_obj.get_extended_graph_edges()

        # quitaremos los arcos de acceso al city_graph de origen
        for edge in edges:

            if edge.nodei == node_city_origin:
                edges.remove(edge)

            if edge.nodej == node_city_origin:
                edges.remove(edge)

        # inicializamos etiquetas de nodos en infinito salvo para el destino que queda con etiqueta 0 y en lista heap
        # diccionario de etiquetas de todos los nodes: dic[node] = label
        labels = defaultdict(float)
        labels_inf = defaultdict(float)
        # diccionario que para cada nodo tiene el listado de arcos que lo llevan a su sucesor: dic[node] = list arcos
        successor = defaultdict(list)
        successor_inf = defaultdict(None)
        # diccionario con la frecuencia acumulada de los arcos sucesores: dic[node] = frecuencia acumuladaq
        frequencies = defaultdict(float)
        # lista de nodos procesados (con estrategia calculada)
        S = []

        # inicializamos parámetros
        # numero de nodos en el grafo extendido
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

        # mientras existan nodos que no han sido procesador
        while len(S) != n_nodes:
            # encontramos nodo con label minimo y que no pertenezca a S
            min_label_node = None
            min_label = float('inf')
            for node in labels:
                if node not in S:
                    if min(labels[node], labels_inf[node]) < min_label:
                        min_label = min(labels[node], labels_inf[node])
                        min_label_node = node
            # nodo que se procesara, en un principio es igual al destino
            j = min_label_node
            # actualizamos S
            S.append(j)
            # debemos encontrar todos los arcos que finalizan en j y cuyo inicio no este en S:
            edge_j = []
            for edge in edges:
                if edge.nodei not in S and edge.nodej == j:
                    edge_j.append(edge)

            # para los arcos actualizamos el label del nodo de origen como: labeli = labelj + time_arco ij
            for edge in edge_j:

                # para no considerar penalidad de transbordo en el origen
                edge_t = edge.t
                if edge.type == ExtendedEdgesType.ALIGHTING:
                    if edge.nodej.city_node == node_city_origin:
                        edge_t = 0
                if edge.type == ExtendedEdgesType.ACCESS:
                    edge_t = edge.t * self.passenger_obj.spa / self.passenger_obj.spv

                # equivalente a t_a cola de chancho en pseudo codigo del paper
                t_i = edge_t + min(labels[j], labels_inf[j])
                i = edge.nodei

                # para to do tipo de arcos menos de boarding
                if edge.f == float('inf') and t_i < labels_inf[i]:
                    successor_inf[i] = edge
                    labels_inf[i] = t_i

                # para arcos de boarding
                if edge.f < float('inf') and t_i < labels[i]:
                    theta = i.mode.theta

                    # caso inicial de actualizacion
                    if frequencies[i] == 0 and labels[i] == float('inf'):
                        # print(edge.type)
                        successor[i].append(edge)
                        labels[i] = (theta * self.passenger_obj.spw / self.passenger_obj.spv + edge.f * t_i) / (edge.f)
                        frequencies[i] = frequencies[i] + edge.f
                    # etiqueta anteriormente asignada
                    else:
                        successor[i].append(edge)
                        labels[i] = (frequencies[i] * labels[i] + edge.f * t_i) / (frequencies[i] + edge.f)
                        frequencies[i] = frequencies[i] + edge.f

                # verificamos que todos los sucessores previo de i se mantengan siendo optimos
                for edge_b in successor[i]:
                    if edge_b == edge:
                        continue
                    # para no considerar penalida de transbordo en el origen
                    edge_b_t = edge_b.t
                    if edge_b.type == ExtendedEdgesType.ALIGHTING:
                        if edge.nodej.city_node == node_city_origin:
                            edge_b_t = 0
                    if edge_b.type == ExtendedEdgesType.ACCESS:
                        edge_b_t = edge_b.t * self.passenger_obj.spa / self.passenger_obj.spv

                    # equivalente a t_b cola de chancho
                    t_ib = min(labels[edge_b.nodej], labels_inf[edge_b.nodej]) + edge_b_t

                    if t_ib >= labels[i]:
                        successor[i].remove(edge_b)
                        labels[i] = (frequencies[i] * labels[i] - edge_b.f * t_ib) / (frequencies[i] - edge_b.f)
                        frequencies[i] = frequencies[i] - edge_b.f

        # reducimos listados de sucesores y labels a una unica lista

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

    def get_hyperpath_OD(self, origin, destination):

        successors, label, frequencies = self.build_hyperpath_graph(origin, destination)

        nodes = self.extended_graph_obj.get_extended_graph_nodes()
        # edges = extended_graph_obj.get_extended_graph_edges()

        # print(successors)
        # tantas hiperrutas por modo que tenga el origen
        hyperpaths = []

        # para cada paradero del origen
        for stop in nodes[origin]:
            # hiperruta individual de la parada
            hyperpath_stop = []
            # inicializamos la hiperruta con el nodo del paradero
            hyperpath_stop.append([stop])

            while True:
                # condicion de parada que cada path individual haya llegado a destino
                end = True
                for path in hyperpath_stop:
                    # existe un path que no ha llegado al destino
                    if path[len(path) - 1] != destination:
                        end = False
                        break
                if end:
                    break

                new_hyperpath_stop = []
                # agregamos sucesores de auqellos path que no han llegado al destino
                for path in hyperpath_stop:
                    # path que no ha llegado a destino
                    if path[len(path) - 1] != destination:
                        # hyperpath_stop.remove(path)
                        # agregamos tantos nuevos path como sucesores tenga el ultimo nodo del path analizado
                        for suc in successors[path[len(path) - 1]]:

                            new_path = []
                            for n in path:
                                new_path.append(n)
                            new_path.append(suc.nodej)

                            new_hyperpath_stop.append(new_path)
                        # sacamos el camino evakuado
                    # path que llego a destino
                    else:
                        new_hyperpath_stop.append(path)
                hyperpath_stop = new_hyperpath_stop
            hyperpaths.append(hyperpath_stop)

        return hyperpaths

    @staticmethod
    def string_hyperpaths_OD(hyperpaths_od, label):
        line = ""
        for hyperpath_stop in hyperpaths_od:
            line += "\nNew stop\n"
            for path in hyperpath_stop:
                line += "\n\tNew Path:\n\t\t"
                for node in path:
                    if isinstance(node, CityNode):
                        line += "[city_node {}: {:.2f}]\n\t\t".format(node.graph_node.name, label[node])
                    if isinstance(node, StopNode):
                        line += "[stop_node {} - {}: {:.2f}]\n\t\t".format(node.mode.name,
                                                                           node.city_node.graph_node.name, label[node])
                    if isinstance(node, RouteNode):
                        line += "[Route_node {} {} - {}: {:.2f}]\n\t\t".format(node.route.id, node.direction,
                                                                               node.stop_node.city_node.graph_node.name,
                                                                               label[node])
        return line

    @staticmethod
    def plot(hyperpaths_od, origin):
        """
        to plot hyperpaths
        :return:
        """
        city_nodes = [origin.graph_node.name]
        stop_nodes = []
        route_nodes = []
        edges_graph = []
        for hyperpath_stop in hyperpaths_od:
            for path in hyperpath_stop:
                prev_node = origin.graph_node.name
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
