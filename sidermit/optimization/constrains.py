from sidermit.city import Graph


class Constrains:

    @staticmethod
    def most_loaded_section_constrains(routes, most_loaded_section):
        """
        to get constrains to optimization problem with respect to most loaded section for each routes
        :param most_loaded_section:
        :param routes:
        :return:
        """

        ineq_constrains = []

        for route in routes:
            kmax = route.mode.kmax
            max_loaded_section = most_loaded_section[route.id]

            ineq_constrains.append(max_loaded_section - kmax)

        return ineq_constrains

    @staticmethod
    def fmax_constrains(graph_obj: Graph, routes, list_mode, f):
        """
        to get constrains about fmax in each edge in the network with respect to capacity in stop of the each mode
        :param graph_obj:
        :param routes:
        :param list_mode:
        :param f:
        :return:
        """

        ineq_constrain = []

        edges = graph_obj.get_edges()

        for edge in edges:
            nodei = edge.node1.id
            nodej = edge.node2.id
            for mode in list_mode:
                fmax = mode.fmax
                sum_f = 0
                for route in routes:
                    if route.mode == mode:
                        if f[route.id] != 0:
                            node_sequence_i = route.nodes_sequence_i
                            node_sequence_r = route.nodes_sequence_r

                            for i in range(len(node_sequence_i) - 1):
                                j = i + 1
                                if str(nodei) == str(node_sequence_i[i]) and str(nodej) == str(node_sequence_i[j]):
                                    sum_f += f[route.id] / mode.d

                            for i in range(len(node_sequence_r) - 1):
                                j = i + 1
                                if str(nodei) == str(node_sequence_r[i]) and str(nodej) == str(node_sequence_r[j]):
                                    sum_f += f[route.id] / mode.d
                ineq_constrain.append(sum_f - fmax)

        return ineq_constrain
