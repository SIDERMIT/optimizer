from sidermit.publictransportsystem import RouteType
from sidermit.city import Graph

class Constrains:

    @staticmethod
    def most_loaded_section_constrains(routes, z, v, k):
        """
        to get constrains to optimization problem with respect to most loaded section for each routes
        :param k:
        :param routes:
        :param z:
        :param v:
        :return:
        """

        eq_constrains = []
        ineq_constrains = []

        for route in routes:
            if route._type != RouteType.CIRCULAR:
                pass
            else:
                kmax = route.mode.kmax
                route_id = route.id
                node_sequence_i = route.nodes_sequence_i
                node_sequence_r = route.nodes_sequence_r

                max_loaded_section = 0

                prev_loaded = 0

                for i in node_sequence_i:

                    zi = 0
                    vi = 0

                    for stop_node in z[route_id]["I"]:
                        if str(stop_node.city_node.graph_node.id) == str(i):
                            zi = z[route_id]["I"][stop_node]
                            break
                    for stop_node in v[route_id]["I"]:
                        if str(stop_node.city_node.graph_node.id) == str(i):
                            vi = v[route_id]["I"][stop_node]
                            break

                    prev_loaded += zi - vi

                    if prev_loaded > max_loaded_section:
                        max_loaded_section = prev_loaded

                prev_loaded = 0

                for i in node_sequence_r:

                    zi = 0
                    vi = 0

                    for stop_node in z[route_id]["R"]:
                        if str(stop_node.city_node.graph_node.id) == str(i):
                            zi = z[route_id]["R"][stop_node]
                            break
                    for stop_node in v[route_id]["R"]:
                        if str(stop_node.city_node.graph_node.id) == str(i):
                            vi = v[route_id]["R"][stop_node]
                            break

                    prev_loaded += zi - vi

                    if prev_loaded > max_loaded_section:
                        max_loaded_section = prev_loaded

                eq_constrains.append(max_loaded_section - k[route_id])
                ineq_constrains.append(k[route_id] - kmax)

        return eq_constrains, ineq_constrains

    @staticmethod
    def fmax_constrains(graph_obj: Graph, routes, list_mode):

        edges = graph_obj.get_edges()

        for edge in edges:
            nodei = edge.node1
            nodej = edge.node2
            for mode in list_mode:
                fmax = mode.fmax
                for route in routes:
                    if route.mode == mode:
                        pass

