from collections import defaultdict


class Hyperpath:
    @staticmethod
    def obtain_hyperpath(extended_graph_obj, node_graph_destination_id):
        nodes = extended_graph_obj.get_extended_graph_nodes()
        edges = extended_graph_obj.get_extended_graph_edges()

        # inicializamos etiquetas de nodos en infinito salvo para el destino que queda con etiqueta 0 y en lista heap
        # diccionario de etiquetas de todos los nodes: dic[node] = label
        labels = defaultdict(float)
        # diccionario que para cada nodo tiene el listado de arcos que lo llevan a su sucesor: dic[node] = list arcos
        successor = defaultdict(list)
        # diccionario con la frecuencia acumulada de los arcos sucesores: dic[node] = frecuencia acumuladaq
        frequencies = defaultdict(float)
        # lista de nodos procesados (con estrategia calculada)
        S = []

        n_nodes = 0
        for city_node in nodes:
            if str(city_node.graph_node.id) == str(node_graph_destination_id):
                labels[city_node] = 0
                n_nodes = n_nodes + 1
            else:
                labels[city_node] = 0
                frequencies[city_node] = 0
                n_nodes = n_nodes + 1
            for stop_node in nodes[city_node]:
                labels[stop_node] = float('inf')
                frequencies[stop_node] = 0
                n_nodes = n_nodes + 1
                for route_node in nodes[city_node][stop_node]:
                    labels[route_node] = float('inf')
                    frequencies[route_node] = 0
                    n_nodes = n_nodes + 1

        # mientras heap tenga nodos por procesar
        while len(S) != n_nodes:
            # encontramos nodo con label minimo y que no pertenezca a S
            min_label_node = None
            min_label = float('inf')
            for node in labels:
                if node not in S:
                    if labels[node] < min_label:
                        min_label = labels[node]
                        min_label_node = node
            # actualizamos S
            S.append(min_label_node)

            # en un principio es igual al destino
            j = min_label_node

            # debemos encontrar todos los arcos que finalizan en j y cuyo inicio no este en S:
            edge_j = []
            for edge in edges:
                if edge.nodei not in S and edge.nodej == j:
                    edge_j.append(edge)

            # para los arcos actualizamos el label del nodo de origen como: labeli = labelj + time_arco ij
            for edge in edge_j:
                # equivalente a t_a cola de chancho en pseudo codigo del paper
                t_i = labels[j] + edge.t
                i = edge.nodei

                # actualizamos a nodos distintos de los de rutas
                if edge.f == float('inf') and t_i < labels[i]:
                    successor[i].append(edge)
                    labels[i] = t_i

                # actualizamos nodos de rutas
                if edge.f < float('inf') and t_i < labels[i]:
                    # caso inicial de actualizacion
                    if frequencies[i] == 0 and labels[i] == float('inf'):
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
                    # equivalente a t_b cola de chancho
                    t_ib = labels[edge_b.nodej] + edge_b.t

                    if t_ib >= labels[i]:
                        successor[i].remove(edge_b)
                        labels[i] = (frequencies[i] * labels[i] - edge_b.f * t_ib) / (frequencies[i] - edge_b.f)
                        frequencies[i] = frequencies[i] - edge_b.f

        return successor, labels, frequencies
