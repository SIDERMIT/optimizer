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
#                                     ↓                    ↓                   ↓
# relation with other city_node  route_node           route_node          route_node

class ExtendedNode:
    def __init__(self, extendend_node_id):
        self.id = extendend_node_id
        self.adjacencies = []

    def add_adjancencies(self, adjacencies):
        self.adjacencies = adjacencies


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
    def __init__(self, route_node_id, route_obj, direction, stop_node):
        ExtendedNode.__init__(self, route_node_id)
        self.route = route_obj
        self.direction = direction
        self.stop_node = stop_node


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

    def __init__(self, graph_obj, network_obj):

        self.__graph_obj = graph_obj
        self.__network_obj = network_obj

        # list with all city_nodes
        city_nodes = self.build_city_nodes(self.__graph_obj)

        # assistant dictionary to build stop_nodes and routes_nodes: dic[city_node][mode_obj] = [list of routes]
        tree_graph = self.build_tree_graph(self.__network_obj, city_nodes)

        # list with all stop nodes, there are 1 stop_node for each mode transiting in a city_node
        stop_nodes = self.build_stop_nodes(tree_graph)

        # list with all route_nodes, there are 1 route_node connected to a stop_node for each route in a city_node
        route_nodes = self.build_route_nodes(tree_graph, stop_nodes)

        # extended graph nodes like as a dictionary: dic[city_node][stop_node] = [list route_nodes]
        self.__extended_graph_nodes = self.build_extended_graph_nodes(route_nodes)

        self.__access_edges = []
        self.__boarding_edges = []
        self.__alighting_edges = []
        self.__routes_edges = []

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
    def build_route_nodes(tree_graph, stop_nodes):

        route_nodes = []
        for city_node in tree_graph:
            for mode_obj in tree_graph[city_node]:
                stop_node = None
                # to get stop node
                for stop in stop_nodes:
                    if stop.city_node == city_node and stop.mode == mode_obj:
                        stop_node = stop
                        break
                for route, direction in tree_graph[city_node][mode_obj]:
                    route_node = RouteNode(len(route_nodes), route, direction, stop_node)
                    route_nodes.append(route_node)
        return route_nodes

    @staticmethod
    def build_extended_graph_nodes(route_nodes):

        extended_graph_nodes = defaultdict(lambda: defaultdict(list))

        for route_node in route_nodes:
            stop_node = route_node.stop_node
            city_node = stop_node.city_node
            extended_graph_nodes[city_node][stop_node].append(route_node)

        return extended_graph_nodes
