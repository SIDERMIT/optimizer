from collections import defaultdict


class OperatorsCost:

    @staticmethod
    def lines_travel_time(routes, edge_distance):
        """
        to get a dictionary with travel times for all lines defined in the network
        :param edge_distance:
        :param routes:
        :return:
        """
        line_travel_time = defaultdict(float)

        for route in routes:
            node_sequence_i = route.nodes_sequence_i
            node_sequence_r = route.nodes_sequence_r

            tv = 0

            # recorremos secuencia de ida
            for i in range(len(node_sequence_i) - 1):
                j = i + 1

                nodei_id = str(node_sequence_i[i])
                nodej_id = str(node_sequence_i[j])

                tv += edge_distance[nodei_id][nodej_id] / route.mode.v

            # recorremos secuencia de vuelta
            for i in range(len(node_sequence_r) - 1):
                j = i + 1

                nodei_id = str(node_sequence_r[i])
                nodej_id = str(node_sequence_r[j])

                tv += edge_distance[nodei_id][nodej_id] / route.mode.v

            line_travel_time[route.id] = tv

        return line_travel_time

    @staticmethod
    def get_cycle_time(z, v, routes, line_travel_time):
        """
        to get cycle time of all routes in the network
        :param z:
        :param v:
        :param routes:
        :param line_travel_time:
        :return:
        """

        cycle_time = defaultdict(float)

        for route in routes:
            route_id = route.id
            t = route.mode.t / 3600

            tc = line_travel_time[route_id]

            # secuancial
            if route.mode.bya == 0:

                for stop in z[route_id]["I"]:
                    tc += t * z[route_id]["I"][stop]
                for stop in v[route_id]["I"]:
                    tc += t * v[route_id]["I"][stop]
                for stop in z[route_id]["R"]:
                    tc += t * z[route_id]["R"][stop]
                for stop in v[route_id]["R"]:
                    tc += t * v[route_id]["R"][stop]

            # simultaneo
            if route.mode.bya == 1:
                processed_stop_i = []
                processed_stop_r = []

                for stop in z[route_id]["I"]:
                    processed_stop_i.append(stop)
                    tc += t * max(z[route_id]["I"][stop], v[route_id]["I"][stop])
                for stop in v[route_id]["I"]:
                    if stop not in processed_stop_i:
                        tc += t * max(z[route_id]["I"][stop], v[route_id]["I"][stop])
                for stop in z[route_id]["R"]:
                    processed_stop_r.append(stop)
                    tc += t * max(z[route_id]["R"][stop], v[route_id]["R"][stop])
                for stop in v[route_id]["R"]:
                    if stop not in processed_stop_r:
                        tc += t * max(z[route_id]["R"][stop], v[route_id]["R"][stop])

            cycle_time[route_id] = tc

        return cycle_time

    @staticmethod
    def get_operators_cost(routes, cycle_time, f, k):
        """
        to get operators cost give a frequencies and boarding size for all lines
        :param routes:
        :param cycle_time:
        :param f:
        :param k:
        :return:
        """

        CO = 0

        for route in routes:
            route_id = route.id

            f_r = f[route_id]

            if f_r == 0:
                continue

            k_r = k[route_id]
            tc_r = cycle_time[route_id]

            mode = route.mode
            c0 = mode.co
            c1 = mode.c1

            CO += (c0 + c1 * k_r) * f_r * tc_r

        return CO
