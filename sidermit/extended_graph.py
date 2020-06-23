

class ExtendedNode:
    def __init__(self, extendend_node_id):
        self.id = extendend_node_id
        self.adjacencies = []

    def add_adjancencies(self, adjacencies):
        self.adjacencies = adjacencies


class CityNode(ExtendedNode):

    def __init__(self, city_node_id, city_node):
        ExtendedNode.__init__(self, city_node_id)


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
