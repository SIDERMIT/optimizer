from collections import defaultdict

from sidermit.extended_graph import CityNode, StopNode, RouteNode, ExtendedEdgesType


class Hyperpath:

    def __str__(self, successor, successor_inf, labels, labels_inf, frequencies):
        line = ""
        for node in labels:

            line_frequency = frequencies[node]

            infinite = False

            if labels_inf[node] < labels[node]:
                infinite = True

            line_successor = ""
            if infinite:
                suc = successor_inf[node]

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
            else:
                for suc in successor[node]:
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
                line += "City_node\n\t-Graph_node_name: {}\n\t-label: {}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.graph_node.name, min(labels_inf[node], labels[node]), line_successor, line_frequency)
            if isinstance(node, StopNode):
                line += "Stop_node\n\t-Mode_name: {}\n\t-Graph_node_name: {}\n\t-label: {}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.mode.name, node.city_node.graph_node.name, min(labels_inf[node], labels[node]), line_successor,
                    line_frequency)
            if isinstance(node, RouteNode):
                line += "Route_node\n\t-route_id: {}\n\t-direction: {}\n\t-Graph_node_name: {}\n\t-label: {}\n\t-Successor: {}\n\t-Frequencies: {}\n".format(
                    node.route.id, node.direction, node.stop_node.city_node.graph_node.name,
                    min(labels_inf[node], labels[node]),
                    line_successor, line_frequency)
        return line

    @staticmethod
    def get_hyperpath(extended_graph_obj, node_graph_origin_id, node_graph_destination_id):
        nodes = extended_graph_obj.get_extended_graph_nodes()
        edges = extended_graph_obj.get_extended_graph_edges()

        # quitaremos los arcos de acceso al city_graph de origen
        for edge in edges:
            if isinstance(edge.nodei, CityNode):
                if str(edge.nodei.graph_node.id) == str(node_graph_origin_id):
                    edges.remove(edge)
            if isinstance(edge.nodej, CityNode):
                if str(edge.nodej.graph_node.id) == str(node_graph_origin_id):
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

        n_nodes = 0
        for city_node in nodes:
            # print(city_node.graph_node.id)
            if str(city_node.graph_node.id) == str(node_graph_destination_id):
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

        # mientras heap tenga nodos por procesar
        while len(S) != n_nodes:
            # encontramos nodo con label minimo y que no pertenezca a S
            min_label_node = None
            min_label = float('inf')
            for node in labels:
                if node not in S:
                    if min(labels[node], labels_inf[node]) < min_label:
                        min_label = min(labels[node], labels_inf[node])
                        min_label_node = node
            # actualizamos S
            S.append(min_label_node)

            # en un principio es igual al destino
            j = min_label_node
            # print(j)
            # print(min_label)

            # debemos encontrar todos los arcos que finalizan en j y cuyo inicio no este en S:
            edge_j = []
            for edge in edges:
                if edge.nodei not in S and edge.nodej == j:
                    edge_j.append(edge)
            # print(len(edge_j))

            # para los arcos actualizamos el label del nodo de origen como: labeli = labelj + time_arco ij
            for edge in edge_j:

                # para no considerar penalida de transbordo en el origen
                edge_t = edge.t
                if edge.type == ExtendedEdgesType.ALIGHTING:
                    if str(edge.nodej.city_node.graph_node.id) == str(node_graph_origin_id):
                        edge_t = 0
                # equivalente a t_a cola de chancho en pseudo codigo del paper
                t_i = edge_t + min(labels[j], labels_inf[j])
                i = edge.nodei

                # print(t_i)
                # print(edge.type)

                # actualizamos a nodos distintos de los de rutas
                if edge.f == float('inf') and t_i < labels_inf[i]:
                    # print("hola")
                    successor_inf[i] = edge
                    labels_inf[i] = t_i
                    # print(labels[i])

                # actualizamos nodos de rutas
                if edge.f < float('inf') and t_i < labels[i]:
                    # caso inicial de actualizacion
                    if frequencies[i] == 0 and labels[i] == float('inf'):
                        # print(edge.type)
                        successor[i].append(edge)
                        labels[i] = (1 + edge.f * t_i) / (frequencies[i] + edge.f)
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
                        if str(edge.nodej.city_node.graph_node.id) == str(node_graph_origin_id):
                            edge_b_t = 0

                    # equivalente a t_b cola de chancho
                    t_ib = labels[edge_b.nodej] + edge_b_t

                    if t_ib >= labels[i]:
                        successor[i].remove(edge_b)
                        labels[i] = (frequencies[i] * labels[i] - edge_b.f * t_ib) / (frequencies[i] - edge_b.f)
                        frequencies[i] = frequencies[i] - edge_b.f

        return successor, successor_inf, labels, labels_inf, frequencies
