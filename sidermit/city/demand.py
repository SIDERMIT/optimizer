from __future__ import annotations

from collections import defaultdict

import pandas as pd

from sidermit.city.graph import Graph, CBD, Periphery, Subcenter
from sidermit.exceptions import *

defaultdict2_float = defaultdict(lambda: defaultdict(float))


class Demand:

    def __init__(self, graph_obj: Graph):
        """
        class that allows to build the OD matrix
        :param graph_obj: city graph object, necessary to recognize the id of the created nodes and compatibility
        with that of the OD matrix
        """
        # initialization of city graph
        self.__graph_obj = graph_obj
        # number of zones
        self.__n = self.__graph_obj.get_n()
        # matrix with demand information
        # dictionary structure [node_idO][node_idD] = vij
        self.__matrix = defaultdict(lambda: defaultdict(float))
        # total trips
        self.total_trips = 0
        # initialization of matriz with zero trips in all OD pairs
        self.__build_default_matrix()

    def get_total_trips(self) -> float:
        """
        to get total trips in all OD pair
        :return:
        """
        return self.total_trips

    def matrix_to_file(self, file_path):
        """
        write OD matrix defined in a csv file
        :param file_path:
        :return:
        """
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

    def __build_default_matrix(self):
        """
        Build initial OD matrix with 0 trips in all OD pairs
        :return: None
        """
        for origin_node in self.__graph_obj.get_nodes():
            for destination_node in self.__graph_obj.get_nodes():
                self.__matrix[int(origin_node.id)][int(destination_node.id)] = 0

    def change_vij(self, origin_node_id: int, destination_node_id: int, vij: float):
        """
        Change trip value to a OD pair
        :param origin_node_id:
        :param destination_node_id:
        :param vij: trips in OD pair
        :return:
        """

        if vij < 0:
            raise TripsValueIsNotValidException("trips value must be >= 0")

        if self.__matrix.get(origin_node_id):
            if destination_node_id in self.__matrix[origin_node_id]:
                self.total_trips = self.total_trips - self.__matrix[origin_node_id][destination_node_id] + vij
                self.__matrix[origin_node_id][destination_node_id] = vij
            else:
                raise DestinationIdDoesNotFoundException("id destination does not found")
        else:
            raise OriginIdDoesNotFoundException("id origin does not found")

    def get_matrix(self) -> defaultdict2_float:
        """
        Get last OD matrix saved
        :return:
        """
        return self.__matrix

    @staticmethod
    def parameters_validator(y: float, a: float, alpha: float, beta: float) -> bool:
        """
        to validate construction parameters of symmetric OD matrix
        :param y: total demand
        :param a: proportion of trips generated in the peripheries
        :param alpha: proportion of trips from the periphery to the CBD
        :param beta: proportion of trips from the periphery that go to the sub-center of the same zone
        :return: True if parameters are valid. False if not.
        """
        if not isinstance(y, int) and not isinstance(y, float):
            raise YIsNotValidException("must specify value int or float for y")
        if not isinstance(a, int) and not isinstance(a, float):
            raise AIsNotValidException("must specify value int or float for a")
        if not isinstance(alpha, int) and not isinstance(alpha, float):
            raise AlphaIsNotValidException("must specify value int or float for alpha")
        if not isinstance(beta, int) and not isinstance(beta, float):
            raise BetaIsNotValidException("must specify value int or float for beta")
        if y < 0:
            raise YOutOfRangeException("y must be positive")
        if a > 1 or a < 0:
            raise AOutOfRangeException("a must be in range [0-1]")
        if alpha > 1 or alpha < 0:
            raise AlphaOutOfRangeException("alpha must be in range [0-1]")
        if beta >= 1 or beta < 0:
            raise BetaOutOfRangeException("beta must be in range [0-1)")
        if alpha + beta > 1:
            raise AlphaBetaOutOfRangeException("alpha + beta must be in range [0-1]")

        return True

    @staticmethod
    def build_from_parameters(graph_obj: Graph, y: float, a: float, alpha: float, beta: float) -> Demand:
        """
        to build OD matrix with symmetric parameters
        :param graph_obj: city graph object, necessary to recognize the id of the created nodes and compatibility
        with that of the OD matrix.
        :param y: total demand
        :param a: proportion of trips generated in the peripheries
        :param alpha: proportion of trips from the periphery to the CBD
        :param beta: proportion of trips from the periphery that go to the sub-center of the same zone
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
                        if node.id == origin_node_id:
                            origin_node_obj = node
                        if node.id == destination_node_id:
                            destination_node_obj = node

                    # CBD does not generate trips
                    if isinstance(origin_node_obj, CBD):
                        continue
                    # periphery does not attract
                    if isinstance(destination_node_obj, Periphery):
                        continue
                    # trips between P - CBD
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, CBD):
                        demand_obj.change_vij(origin_node_id, destination_node_id, v_p_cbd)
                    # trips between P - SC
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id == destination_node_obj.zone_id:
                        demand_obj.change_vij(origin_node_id, destination_node_id, v_p_sc)
                    # trips between P - OSC
                    if isinstance(origin_node_obj, Periphery) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id != destination_node_obj.zone_id:
                        demand_obj.change_vij(origin_node_id, destination_node_id, v_p_osc)
                    # trips between SC - CBD
                    if isinstance(origin_node_obj, Subcenter) and isinstance(destination_node_obj, CBD):
                        demand_obj.change_vij(origin_node_id, destination_node_id, v_sc_cbd)
                    # trips between SC - OSC
                    if isinstance(origin_node_obj, Subcenter) and isinstance(destination_node_obj, Subcenter) and \
                            origin_node_obj.zone_id != destination_node_obj.zone_id:
                        demand_obj.change_vij(origin_node_id, destination_node_id, v_sc_osc)

        return demand_obj

    @staticmethod
    def build_from_file(graph_obj: Graph, file_path) -> Demand:
        """
        to build OD matrix from file
        :param graph_obj: city graph object, necessary to recognize the id of the created nodes and compatibility
        with that of the OD matrix.
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
                        try:
                            demand_obj.change_vij(int(origin_id), int(destination_id), float(vij))
                        except ValueError:
                            raise NodeIdDemandIsNotAnInteger("Node id must be a integer")
                    else:
                        raise FileFormatIsNotValidException("each line must provide information about [origin_id] ["
                                                            "destination_id] [vij]")
        return demand_obj

    @staticmethod
    def build_from_content(graph_obj: Graph, matrix) -> Demand:
        """

        :param graph_obj: city graph object, necessary to recognize the id of the created nodes and compatibility
        with that of the OD matrix.
        :param matrix: List[List[float]]
        :return: Demand object
        """

        demand_obj = Demand(graph_obj)
        nodes = graph_obj.get_nodes()

        if len(nodes) != len(matrix):
            raise DemandMatrixIsNotValidException("Matrix should have rows equal to number of nodes")
        for i in range(len(matrix)):
            if len(nodes) != len(matrix[i]):
                raise DemandMatrixIsNotValidException("Matrix should have columns equal to number of nodes")
            for j in range(len(matrix[i])):
                origin_node_id = nodes[i].id
                destination_node_id = nodes[j].id
                vij = matrix[i][j]
                if vij < 0:
                    raise VijIsNotValidException("Vij should be >=0")

                demand_obj.change_vij(origin_node_id, destination_node_id, vij)

        return demand_obj
