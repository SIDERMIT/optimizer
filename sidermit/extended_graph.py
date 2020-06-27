from collections import defaultdict
from enum import Enum

from sidermit.publictransportsystem.network import RouteType


#                                    Representation extended graph
#
# for each p,sc y CBD:                _______________city_node_______________
#                                     ↑                  ↑                   ↑
#                                access_edge        access_edge          access_edge
#                                     ↓                  ↓                   ↓
# for each mode:                  stop_node (mode1)  stop_node (mode2)    stop_node (mode3)
#                                 |       ↑          |       ↑            |       ↑
#                             boarding alighting  boarding alighting   boarding alighting
#                               edge      edge      edge     edge        edge     edge
#                                 ↓       |          ↓       |            ↓       |
# for each route, direction      route_node           route_node          route_node
#                                     ↓                    ↓                   ↓
#                                route_edge             route_edge         route_edge
#                                     ↑                    ↑                   ↑
# relation with other city_node  route_node(i-1)      route_node(i-1)     route_node(i-1)

class ExtendedNode:
    def __init__(self, extendend_node_id):
        self.id = extendend_node_id


class CityNode(ExtendedNode):

    def __init__(self, city_node_id, graph_node):
        ExtendedNode.__init__(self, city_node_id)
        self.graph_node = graph_node


class StopNode(ExtendedNode):
    def __init__(self, stop_node_id, mode_obj, city_node):
        ExtendedNode.__init__(self, stop_node_id)
        self.mode = mode_obj
        self.city_node = city_node


class RouteNode(ExtendedNode):
    def __init__(self, route_node_id, route_obj, direction, stop_node, previous=None):
        ExtendedNode.__init__(self, route_node_id)
        self.route = route_obj
        self.direction = direction
        self.stop_node = stop_node
        self.prev_route_node = previous


class ExtendedEdge:
    def __init__(self, extended_edge_id, nodei, nodej, t, f, edge_type):
        self.id = extended_edge_id
        self.nodei = nodei
        self.nodej = nodej
        self.t = t
        self.f = f
        self.type = edge_type


class ExtendedEdgesType(Enum):
    ACCESS = 1
    BOARDING = 2
    ALIGHTING = 3
    ROUTE = 4


class ExtendedGraph:

    def __init__(self, graph_obj, network_obj, passenger_obj, initial_frequency=28):

        # list with all city_nodes
        city_nodes = self.build_city_nodes(graph_obj)

        # assistant dictionary to build stop_nodes and routes_nodes: dic[city_node][mode_obj] = [list of routes]
        tree_graph = self.build_tree_graph(network_obj, city_nodes)

        # list with all stop nodes, there are 1 stop_node for each mode transiting in a city_node
        stop_nodes = self.build_stop_nodes(tree_graph)

        # list with all route_nodes, there are 1 route_node connected to a stop_node for each route in a city_node
        route_nodes = self.build_route_nodes(network_obj, stop_nodes)

        # extended graph nodes like as a dictionary: dic[city_node][stop_node] = [list route_nodes]
        self.__extended_graph_nodes = self.build_extended_graph_nodes(route_nodes)

        # list with all access edges, edges between city_node<->stop_node
        access_edges = self.build_access_edges(self.__extended_graph_nodes)
        # list with all boarding edges, edges between stop_node->route_node
        boarding_edges = self.build_boarding_edges(self.__extended_graph_nodes, initial_frequency)
        # list with all alighting edges, edges between route_node->stop_node
        alighting_edges = self.build_alighting_edges(self.__extended_graph_nodes, passenger_obj)
        # list with all routes edges, edges between route_node(i-1)->route_node(i)
        routes_edges = self.build_route_nodes(network_obj, stop_nodes)

        self.__extended_graph_edges = []

        for edge in access_edges:
            self.__extended_graph_edges.append(edge)
        for edge in boarding_edges:
            self.__extended_graph_edges.append(edge)
        for edge in alighting_edges:
            self.__extended_graph_edges.append(edge)
        for edge in routes_edges:
            self.__extended_graph_edges.append(edge)

    def get_extended_graph_nodes(self):
        return self.__extended_graph_nodes

    @staticmethod
    def build_city_nodes(graph_obj):
        city_nodes = []
        for node in graph_obj.get_nodes():
            city_node = CityNode(len(city_nodes), node)
            city_nodes.append(city_node)
        return city_nodes

    @staticmethod
    def build_tree_graph(network_obj, city_nodes):

        tree_graph = defaultdict(lambda: defaultdict(list))
        for city_node in city_nodes:
            node_graph_id = city_node.graph_node.id

            routes = network_obj.get_routes()
            for route in routes:
                mode_obj = route.mode
                stops_i = route.stops_sequence_i
                stops_r = route.stops_sequence_r

                for stop in stops_i:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED:
                            if (route, "I") not in tree_graph[city_node][mode_obj]:
                                tree_graph[city_node][mode_obj].append((route, "I"))
                        else:
                            tree_graph[city_node][mode_obj].append((route, "I"))

                for stop in stops_r:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED:
                            if (route, "R") not in tree_graph[city_node][mode_obj]:
                                tree_graph[city_node][mode_obj].append((route, "R"))
                        else:
                            tree_graph[city_node][mode_obj].append((route, "R"))
        return tree_graph

    @staticmethod
    def build_stop_nodes(tree_graph):
        # list with tuples (mode_obj, city_node) to not duplicated more of a stop for each mode in a city_node
        mode_city = []
        stop_nodes = []
        for city_node in tree_graph:
            for mode_obj in tree_graph[city_node]:
                if (mode_obj, city_node) not in mode_city:
                    mode_city.append((mode_obj, city_node))
                    stop_node = StopNode(len(stop_nodes), mode_obj, city_node)
                    stop_nodes.append(stop_node)
        return stop_nodes

    @staticmethod
    def build_route_nodes(network_obj, stop_nodes):

        routes = network_obj.get_routes()
        route_nodes = []
        for route in routes:
            mode = route.mode
            stop_i = route.stops_sequence_i
            stop_r = route.stops_sequence_r

            prev_route_node = None
            for stop in stop_i:
                stop_node = None
                for s in stop_nodes:
                    if s.mode == mode and str(s.city_node.graph_node.id) == str(stop):
                        stop_node = s
                        break
                route_node = RouteNode(len(route_nodes), route, "I", stop_node, prev_route_node)
                prev_route_node = route_node
                route_nodes.append(route_node)

            prev_route_node = None
            for stop in stop_r:
                stop_node = None
                for s in stop_nodes:
                    if s.mode == mode and str(s.city_node.graph_node.id) == str(stop):
                        stop_node = s
                        break
                route_node = RouteNode(len(route_nodes), route, "R", stop_node, prev_route_node)
                prev_route_node = route_node
                route_nodes.append(route_node)

        return route_nodes

    @staticmethod
    def build_extended_graph_nodes(route_nodes):

        extended_graph_nodes = defaultdict(lambda: defaultdict(list))
        for route_node in route_nodes:
            # print(route_node)
            stop_node = route_node.stop_node
            city_node = stop_node.city_node
            extended_graph_nodes[city_node][stop_node].append(route_node)

        return extended_graph_nodes

    @staticmethod
    def build_access_edges(extended_graph_nodes):

        access_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                edge1 = ExtendedEdge(len(access_edges), city_node, stop_node,
                                     stop_node.mode.tat, -1, ExtendedEdgesType.ACCESS)
                edge2 = ExtendedEdge(len(access_edges), stop_node, city_node,
                                     stop_node.mode.tat, -1, ExtendedEdgesType.ACCESS)
                access_edges.append(edge1)
                access_edges.append(edge2)
        return access_edges

    @staticmethod
    def build_boarding_edges(extended_graph_nodes, initial_frequency):
        boarding_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                for route_node in extended_graph_nodes[city_node][stop_node]:
                    edge = ExtendedEdge(len(boarding_edges), stop_node, route_node,
                                        0, initial_frequency, ExtendedEdgesType.BOARDING)
                    boarding_edges.append(edge)
        return boarding_edges

    @staticmethod
    def build_alighting_edges(extended_graph_nodes, passenger_obj):
        pt = passenger_obj.pt
        alighting_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                for route_node in extended_graph_nodes[city_node][stop_node]:
                    edge = ExtendedEdge(len(alighting_edges), route_node, stop_node,
                                        pt, -1, ExtendedEdgesType.ALIGHTING)
                    alighting_edges.append(edge)
        return alighting_edges

    @staticmethod
    def build_route_edges(route_nodes):

        route_edges = []
        for route_node in route_nodes:
            if route_node.prev_route_node is not None:
                t = 0

                # falta agregar tiempo de recorrido


                edge = ExtendedEdge(len(route_edges), route_node.prev_route_node, route_node,
                                    t, -1, ExtendedEdgesType.ROUTE)
                route_edges.append(edge)
        return route_edges
