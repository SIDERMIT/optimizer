from sidermit.graph import Node


class ExtendedNode:
    def __init__(self, extendend_node_id):
        self.id = extendend_node_id
        self.adjacencies = []

    def add_adjancencies(self, adjacencies):
        self.adjacencies = adjacencies


class CityNode(ExtendedNode, Node):

    def __init__(self, city_node):
        Node.__init__(self, city_node.id, city_node.x, city_node.y, city_node.radius, city_node.angle, city_node.width,
                      city_node.zone_id, city_node.name)


class StopNode:
    def __init__(self, stop_node_id, mode_name, city_node):
        ExtendedNode.__init__(self, stop_node_id)
        self.mode_name = mode_name
        self.city_node = city_node


class RouteNode:
    def __init__(self, route_node_id, route_id, stop_node):
        ExtendedNode.__init__(self, route_node_id)
        self.route_id = route_id
        self.stop_node = stop_node
