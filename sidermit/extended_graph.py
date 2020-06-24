class ExtendedNode:
    def __init__(self, extendend_node_id):
        self.id = extendend_node_id
        self.adjacencies = []

    def add_adjancencies(self, adjacencies):
        self.adjacencies = adjacencies


class CityNode(ExtendedNode):

    def __init__(self, city_node_id, city_node):
        ExtendedNode.__init__(self, city_node_id)
        self.city_node = city_node


class StopNode(ExtendedNode):
    def __init__(self, stop_node_id, mode_name, city_node):
        ExtendedNode.__init__(self, stop_node_id)
        self.mode_name = mode_name
        self.city_node = city_node


class RouteNode(ExtendedNode):
    def __init__(self, route_node_id, route_id, stop_node):
        ExtendedNode.__init__(self, route_node_id)
        self.route_id = route_id
        self.stop_node = stop_node


class ExtendedEdge:
    def __init__(self, extended_edge_id, nodei, nodej, t, f):
        self.id = extended_edge_id
        self.nodei = nodei
        self.nodej = nodej
        self.t = t
        self.f = f


class AccessEdge(ExtendedEdge):
    def __init__(self, access_edge_id, nodei, nodej, t, f):
        ExtendedEdge.__init__(self, access_edge_id, nodei, nodej, t, f)


class BoardingEdge(ExtendedEdge):
    def __init__(self, access_edge_id, nodei, nodej, t, f):
        ExtendedEdge.__init__(self, access_edge_id, nodei, nodej, t, f)


class AlightingEdge(ExtendedEdge):
    def __init__(self, access_edge_id, nodei, nodej, t, f):
        ExtendedEdge.__init__(self, access_edge_id, nodei, nodej, t, f)


class RouteEdge(ExtendedEdge):
    def __init__(self, access_edge_id, nodei, nodej, t, f):
        ExtendedEdge.__init__(self, access_edge_id, nodei, nodej, t, f)


class ExtendedGraph:

    def __init__(self, graph_obj, mode_obj, network_obj):
        self.__graph_obj = graph_obj
        self.__mode_obj = mode_obj
        self.__network_obj = network_obj

        self.__city_nodes = []
        self.__stop_nodes = []
        self.__route_nodes = []

        self.__access_edges = []
        self.__boarding_edges = []
        self.__alighting_edges = []
        self.__routes_edges = []

        self.__add_city_nodes()


    def __add_city_nodes(self):
        for node in self.__graph_obj.get_nodes():
            city_node = CityNode(len(self.__city_nodes), node)
            self.__city_nodes.append(city_node)

    def __add_stop_nodes(self):

        for city_node in self.__city_nodes:
            


