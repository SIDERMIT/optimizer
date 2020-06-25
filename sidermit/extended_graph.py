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
        self.__city_nodes = []
        # to add city_nodes
        self.__add_city_nodes()

        # assistant dictionary to build stop_nodes and routes_nodes: dic[city_node][mode_obj] = [list of routes]
        self.__tree_graph = defaultdict(lambda: defaultdict(list))
        # build assistant dictionary
        self.__build_tree_graph()

        # list with all stop nodes, there are 1 stop_node for each mode transiting in a city_node
        self.__stop_nodes = []
        # list with tuples (mode_obj, city_node) to not duplicated more of a stop for each mode in a city_node
        self.__mode_city = []
        # to add stop_nodes
        self.__add_stop_nodes()

        # list with all route_nodes, there are 1 route_node connected to a stop_node for each route in a city_node
        self.__route_nodes = []
        # to add routes_nodes
        self.__add_route_nodes()

        # extended graph nodes like as a dictionary: dic[city_node][stop_node] = [list route_nodes]

        self.__access_edges = []
        self.__boarding_edges = []
        self.__alighting_edges = []
        self.__routes_edges = []

    def get_tree_graph(self):
        return self.__tree_graph

    def get_city_nodes(self):
        return self.__city_nodes

    def get_stop_nodes(self):
        return self.__stop_nodes

    def get_route_nodes(self):
        return self.__route_nodes

    def __add_city_nodes(self):
        for node in self.__graph_obj.get_nodes():
            city_node = CityNode(len(self.__city_nodes), node)
            self.__city_nodes.append(city_node)

    def __build_tree_graph(self):

        for city_node in self.__city_nodes:
            node_graph_id = city_node.graph_node.id

            routes = self.__network_obj.get_routes()
            for route in routes:
                mode_obj = route.mode
                stops_i = route.stops_sequence_i
                stops_r = route.stops_sequence_r

                for stop in stops_i:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED:
                            if (route, "I") not in self.__tree_graph[city_node][mode_obj]:
                                self.__tree_graph[city_node][mode_obj].append((route, "I"))
                        else:
                            self.__tree_graph[city_node][mode_obj].append((route, "I"))

                for stop in stops_r:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED:
                            if (route, "R") not in self.__tree_graph[city_node][mode_obj]:
                                self.__tree_graph[city_node][mode_obj].append((route, "R"))
                        else:
                            self.__tree_graph[city_node][mode_obj].append((route, "R"))

    def __add_stop_nodes(self):

        for city_node in self.__tree_graph:
            for mode_obj in self.__tree_graph[city_node]:
                if (mode_obj, city_node) not in self.__mode_city:
                    self.__mode_city.append((mode_obj, city_node))
                    stop_node = StopNode(len(self.__stop_nodes), mode_obj, city_node)
                    self.__stop_nodes.append(stop_node)

    def __add_route_nodes(self):

        for city_node in self.__tree_graph:
            for mode_obj in self.__tree_graph[city_node]:
                stop_node = None
                # to get stop node
                for stop in self.__stop_nodes:
                    if stop.city_node == city_node and stop.mode == mode_obj:
                        stop_node = stop
                        break
                for route, direction in self.__tree_graph[city_node][mode_obj]:
                    route_node = RouteNode(len(self.__route_nodes), route, direction, stop_node)
                    self.__route_nodes.append(route_node)
