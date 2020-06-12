from collections import defaultdict

from sidermit.exceptions import *


class demand:

    def __init__(self, graph_obj):

        # matrix with demand information
        # dictionary structure [node_idO][node_idD] = vij
        self.__matrix = defaultdict(lambda: defaultdict(float))
        # city graph (graph.py)
        self.__graph_obj = None
        # initialization of city graph
        if graph_obj.is_valid():
            self.__graph_obj = graph_obj
        else:
            raise GraphIsNotValidExceptions("Graph is not valid")
        # number of zones
        self.__n = self.__graph_obj.obtain_n()
        # initialization of matriz with zero trips in all OD pairs
        self.__initial_matrix()

    def __initial_matrix(self):
        for nodeO in self.__graph_obj.obtain_nodes():
            for nodeD in self.__graph_obj.obtain_nodes():
                self.__matrix[nodeO.id][nodeD.id] = 0

    def __change_vij(self, nodeid_origin, nodeid_destination, vij):

        if self.__matrix.get(nodeid_origin):
            if self.__matrix[nodeid_origin].get(nodeid_destination):
                self.__matrix[nodeid_origin][nodeid_destination] = vij
            else:
                raise IdDestinationnDoesNotFoundExceptions("id destination does not found")
        else:
            raise IdOriginDoesNotFoundExceptions("id origin does not found")

    def obtain_matrix(self):
        """
        # return last od matrix saved
        :return:
        """
        return self.__matrix

    @staticmethod
    def parameters_validator(y, a, alpha, beta):
        """
        # to validate parameters
        :param y:
        :param a:
        :param alpha:
        :param beta:
        :return:
        """
        if not isinstance(y, int) and not isinstance(y, float):
            raise YIsNotValidExceptions("must specify value int or float for y")
        if not isinstance(a, int) and not isinstance(a, float):
            raise AIsNotValidExceptions("must specify value int or float for a")
        if not isinstance(alpha, int) and not isinstance(alpha, float):
            raise AlphaIsNotValidExceptions("must specify value int or float for alpha")
        if not isinstance(beta, int) and not isinstance(beta, float):
            raise BetaIsNotValidExceptions("must specify value int or float for beta")
        if y < 0:
            raise YOutRangeExceptions("y must be positive")
        if a > 1 or a < 0:
            raise AOutRangeExceptions("A must be in range [0-1]")
        if alpha > 1 or alpha < 0:
            raise AlphaOutRangeExceptions("alpha must be in range [0-1]")
        if beta >= 1 or beta < 0:
            raise BetaOutRangeExceptions("beta must be in range [0-1)")
        if alpha + beta > 1:
            raise AlphaBetaOutRangeExceptions("alpha + beta must be in range [0-1]")

        return True

    @staticmethod
    def build_matrix_from_parameters(graph_obj, y, a, alpha, beta):
        """
        to build OD matrix with symmetric parameters
        :param graph_obj:
        :param y:
        :param a:
        :param alpha:
        :param beta:
        :return:
        """
        demand_obj = demand(graph_obj)

        if demand_obj.parameters_validator(y, a, alpha, beta):

            zones = demand_obj.__graph_obj.obtain_zones()

            b = 1 - a
            gamma = 0
            gamma_g = 0
            n = demand_obj.__n

            if n > 1:
                gamma = 1 - alpha - beta
                alpha_g = alpha / (1 - beta)
                gamma_g = gamma / (1 - beta)
            else:
                beta = 1 - alpha
                alpha_g = 1

            y_z = y
            # demand for each zone
            if n != 0:
                y_z = y / n
            # periphery demand
            y_p = a * y_z
            # subcenter demand
            y_sc = b * y_z
            # trips periphery - CBD
            v_p_cbd = alpha * y_p
            # trips periphery - subcenter
            v_p_sc = beta * y_p
            # trips periphery - other subcenter
            v_p_osc = 0
            if n > 1:
                v_p_osc = gamma * y_p / (n - 1)
            # trips subcenter - cbd
            v_sc_cbd = y_sc * alpha_g
            # trips subcenter -  other subcenter
            v_sc_osc = 0
            if n > 1:
                v_sc_osc = y_sc * gamma_g / (n - 1)

            # for each origin in matrix
            for origin_id in demand_obj.__matrix:
                for destination_id in demand_obj.__matrix:
                    nodeO = None
                    nodeD = None
                    for node in demand_obj.__graph_obj.obtain_nodes():
                        if node.id == origin_id:
                            nodeO = node
                        if node.id == destination_id:
                            nodeD = node

                    if isinstance(nodeO, CBD):
                        continue
                    if isinstance(nodeD, Periphery):
                        continue

                    if isinstance(nodeO, Periphery) and isinstance(nodeD, Subcenter) and nodeO.zone_id == nodeD.zone_id:

                    demand_obj.__change_vij(nodeO.id, nodeD.id, )

    @staticmethod
    def build_matrix_from_file(file_path):
        pass
