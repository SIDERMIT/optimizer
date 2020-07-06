from collections import defaultdict
from enum import Enum

from sidermit.city import Graph
from sidermit.publictransportsystem.network import RouteType
from sidermit.publictransportsystem import TransportMode, Route


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
#                                     ↑                    ↑                   ↑
#                                route_edge             route_edge         route_edge
#                                     ↑                    ↑                   ↑
# relation with other city_node  route_node(i-1)      route_node(i-1)     route_node(i-1)

class ExtendedNode:

    def __init__(self, extendend_node_id):
        """
        node to extended graph
        :param extendend_node_id: node id
        """
        self.id = extendend_node_id


class CityNode(ExtendedNode):

    def __init__(self, city_node_id, graph_node):
        """
        extended node with graph node information
        :param city_node_id: node id
        :param graph_node: CBD, Subcenter or Periphery node
        """
        ExtendedNode.__init__(self, city_node_id)
        self.graph_node = graph_node


class StopNode(ExtendedNode):
    def __init__(self, stop_node_id, mode_obj: TransportMode, city_node: CityNode):
        """
        extended node with Transport Mode information
        :param stop_node_id: node id
        :param mode_obj: TransportMode object
        :param city_node: CityNode object associated
        """
        ExtendedNode.__init__(self, stop_node_id)
        self.mode = mode_obj
        self.city_node = city_node


class RouteNode(ExtendedNode):
    def __init__(self, route_node_id, route_obj: Route, direction: str, stop_node: StopNode, previous=None):
        """
        extended node with route information
        :param route_node_id: node id
        :param route_obj: Route object
        :param direction: "I" if RouteNode represents forward direction, "R" if RouteNode represents return direction
        :param stop_node: StopNode object associated
        :param previous: previous RouteNode in stop sequences of the route associated
        """
        ExtendedNode.__init__(self, route_node_id)
        self.route = route_obj
        self.direction = direction
        self.stop_node = stop_node
        self.prev_route_node = previous


class ExtendedEdge:
    def __init__(self, extended_edge_id, nodei, nodej, t, f, edge_type):
        """
        edge to extended graph
        :param extended_edge_id: edge id
        :param nodei: edge origin node
        :param nodej: edge detination node
        :param t: edge time in hours
        :param f: edge frequency in [veh/hr]
        :param edge_type: edge type (ExtendedEdgesType)
        """
        self.id = extended_edge_id
        self.nodei = nodei
        self.nodej = nodej
        self.t = t
        self.f = f
        self.type = edge_type


class ExtendedEdgesType(Enum):
    """
    extended edges type. ACCESS edge to edges between CityNode and StopNode and vice versa, Boarding edge to edges
    between StopNode and RouteNode, ALIGHTING edge to edges between RouteNode and StopNode, Route edge to edges
    between RouteNode and RouteNode
    """
    ACCESS = 1
    BOARDING = 2
    ALIGHTING = 3
    ROUTE = 4


class ExtendedGraph:

    def __init__(self, graph_obj: Graph, routes, sPTP: float, frequency_routes=None):
        """
        class to create extended graph that agglomerates the city graph information and transport routes in the network.
        It incorporates the penalty of the transfer of the passenger and the frequencies of the routes for
        the construction of edges
        :param graph_obj: Graph object
        :param routes: list of routes in network associated
        :param sPTP: penalty of the transfer of the passenger in EIV
        :param frequency_routes: defauldict(float) with key: route_id and value: frequency [veh/hr] of the route_id.
        Default value is a a dictionary with a frequency of 28 [veh/hr] for all routes
        """

        if frequency_routes is None:
            frequency_routes = defaultdict(float)

            for route in routes:
                frequency_routes[route.id] = 28

        # list with all city_nodes
        city_nodes = self.build_city_nodes(graph_obj)

        # assistant dictionary to build stop_nodes and routes_nodes: dic[city_node][mode_obj] = [list of routes]
        tree_graph = self.build_tree_graph(routes, city_nodes)

        # list with all stop nodes, there are 1 stop_node for each mode transiting in a city_node
        stop_nodes = self.build_stop_nodes(tree_graph)

        # list with all route_nodes, there are 1 route_node connected to a stop_node for each route in a city_node
        route_nodes = self.build_route_nodes(routes, stop_nodes)

        # extended graph nodes like as a dictionary: dic[city_node][stop_node] = [list route_nodes]
        self.__extended_graph_nodes = self.build_extended_graph_nodes(route_nodes)

        # list with all access edges, edges between city_node<->stop_node
        access_edges = self.build_access_edges(self.__extended_graph_nodes)
        # list with all boarding edges, edges between stop_node->route_node
        boarding_edges = self.build_boarding_edges(self.__extended_graph_nodes, frequency_routes)
        # list with all alighting edges, edges between route_node->stop_node
        alighting_edges = self.build_alighting_edges(self.__extended_graph_nodes, sPTP)
        # list with all routes edges, edges between route_node(i-1)->route_node(i)
        routes_edges = self.build_route_edges(self.__extended_graph_nodes)

        self.__extended_graph_edges = []

        for edge in access_edges:
            self.__extended_graph_edges.append(edge)
        for edge in boarding_edges:
            self.__extended_graph_edges.append(edge)
        for edge in alighting_edges:
            self.__extended_graph_edges.append(edge)
        for edge in routes_edges:
            self.__extended_graph_edges.append(edge)

    def __str__(self):
        """
        to print extended graph
        :return: String with information of the extended graph
        """
        line = ""
        for city_node in self.__extended_graph_nodes:
            line += "City node\n-Graph node name: {}\n".format(city_node.graph_node.name)
            for stop_node in self.__extended_graph_nodes[city_node]:
                # information about access edge
                for edge in self.__extended_graph_edges:
                    if edge.nodei == city_node and edge.nodej == stop_node:
                        line += "\tAccess edge\n\t-Access time: {} [min]\n".format(edge.t)

                line += "\t\tStop node\n\t\t-Mode name: {}\n".format(stop_node.mode.name)

                for route_node in self.__extended_graph_nodes[city_node][stop_node]:
                    # information about boarding edge
                    for edge in self.__extended_graph_edges:
                        if edge.nodei == stop_node and edge.nodej == route_node:
                            line += "\t\t\tBoarding edge\n\t\t\t-Frequency: {} [veh/h]\n".format(edge.f)

                    # information about boarding edge
                    for edge in self.__extended_graph_edges:
                        if edge.nodei == route_node and edge.nodej == stop_node:
                            line += "\t\t\tAlighting edge\n\t\t\t-Penalty transfer: {} [min]\n".format(edge.t * 60)

                    # information about route node
                    if route_node.prev_route_node is None:
                        line += "\t\t\t\tRoute node\n\t\t\t\t-Route_id: {}\n\t\t\t\t-Direction: {}\n\t\t\t\t-Previous stop: {}\n\t\t\t\t-Time to previous stop: {} [min]\n".format(
                            route_node.route.id,
                            route_node.direction, "no data", 0)
                    else:
                        t = 0
                        for edge in self.__extended_graph_edges:
                            if edge.nodei == route_node.prev_route_node and edge.nodej == route_node:
                                t = edge.t
                                break
                        line += "\t\t\t\tRoute node\n\t\t\t\t-Route_id: {}\n\t\t\t\t-Direction: {}\n\t\t\t\t-Previous stop: {}\n\t\t\t\t-Time to previous stop: {} [min]\n".format(
                            route_node.route.id,
                            route_node.direction,
                            route_node.prev_route_node.stop_node.city_node.graph_node.name,
                            t)
        return line

    def get_extended_graph_nodes(self):
        """
        to get extended nodes associated to the graph
        :return: dictionary: dic[CityNode][StopNode] = List[RouteNode]
        """
        return self.__extended_graph_nodes

    def get_extended_graph_edges(self):
        """
        to get extended edges associated to the graph
        :return: List[ExtendedEdges]
        """
        return self.__extended_graph_edges

    @staticmethod
    def build_city_nodes(graph_obj: Graph):
        """
        to build CityNodes in the extended graph
        :param graph_obj: Graph object
        :return: List[CityNode]
        """
        city_nodes = []
        for node in graph_obj.get_nodes():
            city_node = CityNode(len(city_nodes), node)
            city_nodes.append(city_node)
        return city_nodes

    @staticmethod
    def build_tree_graph(routes, city_nodes):
        """
        to build auxiliary structure for construction of the extended graph
        :param routes: routes in the network associated
        :param city_nodes: List[CityNode]
        :return: dictionary: dic[CityNode][TransportMode] = List(Route, direction = "I" or "R")
        """

        tree_graph = defaultdict(lambda: defaultdict(list))
        for city_node in city_nodes:
            node_graph_id = city_node.graph_node.id

            for route in routes:
                mode_obj = route.mode
                stops_i = route.stops_sequence_i
                stops_r = route.stops_sequence_r

                for stop in stops_i:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED or route._type == RouteType.CIRCULAR:
                            if (route, "I") not in tree_graph[city_node][mode_obj]:
                                tree_graph[city_node][mode_obj].append((route, "I"))
                        else:
                            tree_graph[city_node][mode_obj].append((route, "I"))

                for stop in stops_r:
                    if str(node_graph_id) == str(stop):
                        # to avoid add twice first and last node in circular routes
                        if route._type == RouteType.PREDEFINED or route._type == RouteType.CIRCULAR:
                            if (route, "R") not in tree_graph[city_node][mode_obj]:
                                tree_graph[city_node][mode_obj].append((route, "R"))
                        else:
                            tree_graph[city_node][mode_obj].append((route, "R"))
        return tree_graph

    @staticmethod
    def build_stop_nodes(tree_graph):
        """
        to build StopNode in extended graph
        :param tree_graph: dic[CityNode][TransportMode] = List(Route, direction = "I" or "R")
        :return: List[StopNode]
        """
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
    def build_route_nodes(routes, stop_nodes):
        """
        to build route nodes in extended graph
        :param routes: list of routes in network associated
        :param stop_nodes: List[StopNode]
        :return: List[RouteNode]
        """
        # list with all route nodes
        route_nodes = []
        for route in routes:
            mode = route.mode
            stop_i = route.stops_sequence_i
            stop_r = route.stops_sequence_r
            # to circular exceptions
            _type = route._type

            # nodes for "I" direction
            nodes = []
            prev_route_node = None
            # look for a previous route node
            for stop in stop_i:
                stop_node = None
                for s in stop_nodes:
                    if s.mode == mode and str(s.city_node.graph_node.id) == str(stop):
                        stop_node = s
                        break
                route_node = RouteNode(len(route_nodes) + len(nodes), route, "I", stop_node, prev_route_node)
                prev_route_node = route_node
                nodes.append(route_node)
            # add previous node_route in circular routes
            if prev_route_node is not None and _type == RouteType.CIRCULAR:
                for i in range(len(nodes)):
                    if i == 0:
                        continue
                    n = nodes[i]
                    if i == 1:
                        n.prev_route_node = nodes[len(nodes) - 1]
                        route_nodes.append(n)
                        continue
                    n = nodes[i]
                    route_nodes.append(n)
            # add previous node_route
            if _type == RouteType.PREDEFINED or _type == RouteType.CUSTOM:
                for n in nodes:
                    route_nodes.append(n)
            # nodes for "R" direction
            nodes = []
            prev_route_node = None
            # look for a previous route node
            for stop in stop_r:
                stop_node = None
                for s in stop_nodes:
                    if s.mode == mode and str(s.city_node.graph_node.id) == str(stop):
                        stop_node = s
                        break
                route_node = RouteNode(len(route_nodes) + len(nodes), route, "R", stop_node, prev_route_node)
                prev_route_node = route_node
                nodes.append(route_node)
            # add previous node_route in circular routes
            if prev_route_node is not None and _type == RouteType.CIRCULAR:
                for i in range(len(nodes)):
                    if i == 0:
                        continue
                    n = nodes[i]
                    if i == 1:
                        n.prev_route_node = nodes[len(nodes) - 1]
                        route_nodes.append(n)
                        continue
                    n = nodes[i]
                    route_nodes.append(n)
            # add previous node_route
            if _type == RouteType.PREDEFINED or _type == RouteType.CUSTOM:
                for n in nodes:
                    route_nodes.append(n)

        return route_nodes

    @staticmethod
    def build_extended_graph_nodes(route_nodes):
        """
        to build extended graph node structure
        :param route_nodes: List[RouteNode]
        :return: dictionary: dic[CityNode][StopNode] = List[RouteNode]
        """

        extended_graph_nodes = defaultdict(lambda: defaultdict(list))
        for route_node in route_nodes:
            # print(route_node)
            stop_node = route_node.stop_node
            city_node = stop_node.city_node
            extended_graph_nodes[city_node][stop_node].append(route_node)

        return extended_graph_nodes

    @staticmethod
    def build_access_edges(extended_graph_nodes):
        """
        to build access edges in extended graph
        :param extended_graph_nodes: dictionary: dic[CityNode][StopNode] = List[RouteNode]
        :return: List[ExtendedEdge]
        """
        access_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                edge1 = ExtendedEdge(len(access_edges), city_node, stop_node,
                                     stop_node.mode.tat / 60, float('inf'), ExtendedEdgesType.ACCESS)
                access_edges.append(edge1)
                edge2 = ExtendedEdge(len(access_edges), stop_node, city_node,
                                     stop_node.mode.tat / 60, float('inf'), ExtendedEdgesType.ACCESS)
                access_edges.append(edge2)
        return access_edges

    @staticmethod
    def build_boarding_edges(extended_graph_nodes, frequency_routes):
        """
        to build boarding edges in extended graph
        :param extended_graph_nodes: dic[CityNode][StopNode] = List[RouteNode]
        :param frequency_routes: defauldict(float) with key: route_id and value: frequency [veh/hr] of the route_id.
        :return: List[ExtendedEdge]
        """
        boarding_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                for route_node in extended_graph_nodes[city_node][stop_node]:
                    route = route_node.route
                    direction = route_node.direction

                    if direction == "I":
                        node_sequence = route.nodes_sequence_i
                    else:
                        node_sequence = route.nodes_sequence_r
                    # if not be last stop of the route add boarding edges
                    if route._type != RouteType.CIRCULAR and str(route_node.stop_node.city_node.graph_node.id) != str(
                            node_sequence[len(node_sequence) - 1]):
                        edge = ExtendedEdge(len(boarding_edges), stop_node, route_node,
                                            0, frequency_routes[route.id] / route.mode.d, ExtendedEdgesType.BOARDING)
                        boarding_edges.append(edge)
                        continue
                    # but if route type is circular add always boarding edges
                    if route._type == RouteType.CIRCULAR:
                        edge = ExtendedEdge(len(boarding_edges), stop_node, route_node,
                                            0, frequency_routes[route.id] / route.mode.d, ExtendedEdgesType.BOARDING)
                        boarding_edges.append(edge)
                        continue

        return boarding_edges

    @staticmethod
    def build_alighting_edges(extended_graph_nodes, sPTP):
        """
        to build extended alighting edges
        :param extended_graph_nodes: dic[CityNode][StopNode] = List[RouteNode]
        :param sPTP: penalty of the transfer of the passenger in EIV
        :return: List[ExtendedEdge]
        """
        spt = sPTP / 60
        alighting_edges = []
        for city_node in extended_graph_nodes:
            for stop_node in extended_graph_nodes[city_node]:
                for route_node in extended_graph_nodes[city_node][stop_node]:
                    route = route_node.route
                    direction = route_node.direction
                    if direction == "I":
                        node_sequence = route.nodes_sequence_i
                    else:
                        node_sequence = route.nodes_sequence_r
                    # if not be first stop of the route add alighting edges
                    if route._type != RouteType.CIRCULAR and str(route_node.stop_node.city_node.graph_node.id) != str(
                            node_sequence[0]):
                        edge = ExtendedEdge(len(alighting_edges), route_node, stop_node,
                                            spt, float('inf'), ExtendedEdgesType.ALIGHTING)
                        alighting_edges.append(edge)
                        continue
                    # but if route type is circular add always alighting edges
                    if route._type == RouteType.CIRCULAR:
                        edge = ExtendedEdge(len(alighting_edges), route_node, stop_node,
                                            spt, float('inf'), ExtendedEdgesType.ALIGHTING)
                        alighting_edges.append(edge)
                        continue

        return alighting_edges

    @staticmethod
    def build_route_edges(extended_graph_nodes):
        """
        to build extended routes edges
        :param extended_graph_nodes: dic[CityNode][StopNode] = List[RouteNode]
        :return: List[ExtendedEdge]
        """

        route_nodes = []
        nodes = []

        for city_node in extended_graph_nodes:
            nodes.append(city_node.graph_node)
            for stop_node in extended_graph_nodes[city_node]:
                for route_node in extended_graph_nodes[city_node][stop_node]:
                    route_nodes.append(route_node)

        route_edges = []
        for route_node in route_nodes:
            # only if route node has previous route node
            if route_node.prev_route_node is not None:

                # previous route node
                previous_route_node = route_node.prev_route_node

                # to identify route
                route = route_node.route
                direction = route_node.direction

                # velocity of the route
                v = route_node.stop_node.mode.v

                # id graph node to actual route node and previous route node
                id_city1 = route_node.stop_node.city_node.graph_node.id
                id_city2 = previous_route_node.stop_node.city_node.graph_node.id

                # to identify node sequence of the route
                if direction == "I":
                    node_sequence = route.nodes_sequence_i
                else:
                    node_sequence = route.nodes_sequence_r

                # to get distance between actual route node and previous route node
                distance = 0
                x_prev = previous_route_node.stop_node.city_node.graph_node.x
                y_prev = previous_route_node.stop_node.city_node.graph_node.y
                x_final = route_node.stop_node.city_node.graph_node.x
                y_final = route_node.stop_node.city_node.graph_node.y
                count = False
                for node in node_sequence:
                    if str(node) == str(id_city2):
                        count = True
                        continue
                    if str(node) == str(id_city1):
                        distance = distance + ((x_prev - x_final) ** 2 + (y_prev - y_final) ** 2) ** 0.5
                        break
                    if count:
                        for n in nodes:
                            if str(node) == str(n.id):
                                x = n.x
                                y = n.y
                                distance = distance + ((x_prev - x) ** 2 + (y_prev - y) ** 2) ** 0.5
                                x_prev = x
                                y_prev = y
                                break

                t = distance / 1000 / v

                edge = ExtendedEdge(len(route_edges), previous_route_node, route_node,
                                    t, float('inf'), ExtendedEdgesType.ROUTE)
                route_edges.append(edge)
        return route_edges
