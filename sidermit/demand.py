from collections import defaultdict

import pandas as pd

from sidermit.exceptions import *
from sidermit.graph import CBD, Periphery, Subcenter


class Demand:

    def __init__(self, graph_obj):
        # initialization of city graph
        self.__graph_obj = graph_obj
        # number of zones
        self.__n = self.__graph_obj.get_n()
        # matrix with demand information
        # dictionary structure [node_idO][node_idD] = vij
        self.__matrix = defaultdict(lambda: defaultdict(float))
        # initialization of matriz with zero trips in all OD pairs
        self.__initial_matrix()

    def matrix_to_file(self, file_path):
        col_origin = []
        col_destination = []
        col_vij = []

        for origin in self.__matrix:
            for destination in self.__matrix[origin]:
                col_origin.append(origin)
                col_destination.append(destination)
                col_vij.append(self.__matrix[origin][destination])

        df_matrix = pd.DataFrame()
        df_matrix["origin"] = col_origin
        df_matrix["destination"] = col_destination
        df_matrix["vij"] = col_vij

        df_matrix.to_csv(file_path, sep=",", index=False)

    def __initial_matrix(self):
        for origin_node in self.__graph_obj.get_nodes():
            for destination_node in self.__graph_obj.get_nodes():
                self.__matrix[str(origin_node.id)][str(destination_node.id)] = 0

    def __change_vij(self, origin_node_id, destination_node_id, vij):

        if vij < 0:
            raise tripsValueIsNotValidExceptions("trips value must be >= 0")

        if self.__matrix.get(str(origin_node_id)):
            if str(destination_node_id) in self.__matrix[str(origin_node_id)]:
                self.__matrix[str(origin_node_id)][str(destination_node_id)] = vij
            else:
                raise IdDestinationnDoesNotFoundExceptions("id destination does not found")
        else:
            raise IdOriginDoesNotFoundExceptions("id origin does not found")

    def get_matrix(self):
        """
        return last od matrix saved
        :return:
        """
        return self.__matrix

    @staticmethod
    def parameters_validator(y, a, alpha, beta):
        """
        to validate parameters
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
            raise AOutRangeExceptions("a must be in range [0-1]")
        if alpha > 1 or alpha < 0:
            raise AlphaOutRangeExceptions("alpha must be in range [0-1]")
        if beta >= 1 or beta < 0:
            raise BetaOutRangeExceptions("beta must be in range [0-1)")
        if alpha + beta > 1:
            raise AlphaBetaOutRangeExceptions("alpha + beta must be in range [0-1]")

        return True

    @staticmethod
    def build_from_parameters(graph_obj, y, a, alpha, beta):
        """
        to build OD matrix with symmetric parameters
        :param graph_obj:
        :param y:
        :param a:
        :param alpha:
        :param beta:
        :return:
        """
        demand_obj = Demand(graph_obj)

        if demand_obj.parameters_validator(y, a, alpha, beta):

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
            for origin_node_id in demand_obj.__matrix:
                # for each destination in matrix[origin_id]
                for destination_node_id in demand_obj.__matrix[origin_node_id]:
                    origin_node_obj = None
                    destination_node_obj = None
                    for node in demand_obj.__graph_obj.get_nodes():
                        if str(node.id) == str(origin_node_id):
                            origin_node_obj = node
                        if str(node.id) == str(destination_node_id):
                            destination_node_obj = node

                    # CBD does not generate trips
                    if isinstance(origin_node_obj, CBD):
                        continue
                    # periphery does not attract
                    if isinstance(destination_node_obj, Periphery):
                        continue
                    # trips beetween P - CBD
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, CBD):
                        demand_obj.__change_vij(origin_node_id, destination_node_id, v_p_cbd)
                    # trips beetween P - SC
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id == destination_node_obj.zone_id:
                        demand_obj.__change_vij(origin_node_id, destination_node_id, v_p_sc)
                    # trips beetween P - OSC
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id != destination_node_obj.zone_id:
                        demand_obj.__change_vij(origin_node_id, destination_node_id, v_p_osc)
                    # trips beetween SC - CBD
                    if isinstance(origin_node_obj, Subcenter) and isinstance(destination_node_obj, CBD):
                        demand_obj.__change_vij(origin_node_id, destination_node_id, v_sc_cbd)
                    # trips beetween SC - OSC
                    if isinstance(origin_node_obj, Subcenter) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id != destination_node_obj.zone_id:
                        demand_obj.__change_vij(origin_node_id, destination_node_id, v_sc_osc)

        return demand_obj

    @staticmethod
    def build_from_file(graph_obj, file_path):
        """
        to build from file
        :param graph_obj:
        :param file_path:
        :return:
        """

        demand_obj = Demand(graph_obj)

        with open(file_path, mode='r', encoding='utf-8') as f_obj:

            n_lines = 0
            for line in f_obj.readlines():
                if n_lines == 0:
                    n_lines = 1
                    continue
                else:
                    if len(line.split(",")) == 3:
                        origin_id, destination_id, vij = line.split(",")
                        demand_obj.__change_vij(str(origin_id), str(destination_id), float(vij))
                    else:
                        raise FileFormatIsNotValidExceptions("each line must provide information about [origin_id] ["
                                                             "destination_id] [vij]")
        return demand_obj
