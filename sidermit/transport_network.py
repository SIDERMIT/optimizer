import pandas as pd

from sidermit.exceptions import *


class Route:

    def __init__(self, graph_obj, modes_obj, route_id, mode_name, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                 stops_sequence_r):
        self.id = None
        self.mode = None
        self.nodes_sequence_i = None
        self.nodes_sequence_r = None
        self.stops_sequence_i = None
        self.stops_sequence_r = None

        if self.parameters_validator(graph_obj, modes_obj, route_id, mode_name, nodes_sequence_i, nodes_sequence_r,
                                     stops_sequence_i,
                                     stops_sequence_r):
            self.id = route_id
            self.mode = mode_name
            self.nodes_sequence_i = self.sequences_to_list(nodes_sequence_i)
            self.nodes_sequence_r = self.sequences_to_list(nodes_sequence_r)
            self.stops_sequence_i = self.sequences_to_list(stops_sequence_i)
            self.stops_sequence_r = self.sequences_to_list(stops_sequence_r)

    def parameters_validator(self, graph_obj, modes_obj, route_id, mode_name, nodes_sequence_i, nodes_sequence_r,
                             stops_sequence_i, stops_sequence_r):
        """
        to check all parameters
        :param graph_obj:
        :param modes_obj:
        :param route_id:
        :param mode_name:
        :param nodes_sequence_i:
        :param nodes_sequence_r:
        :param stops_sequence_i:
        :param stops_sequence_r:
        :return:
        """

        modes_names = modes_obj.get_modes_names()
        nodes_i = self.sequences_to_list(nodes_sequence_i)
        nodes_r = self.sequences_to_list(nodes_sequence_r)
        stops_i = self.sequences_to_list(stops_sequence_i)
        stops_r = self.sequences_to_list(stops_sequence_r)

        if route_id is None:
            raise RouteIdIsNotValidExceptions("route_id is not valid. Try to give a value for route_id")

        if mode_name not in modes_names:
            raise ModeNameIsNotValidExceptions("mode_name was not define in modes_obj")

        if self.edges_validator(graph_obj, nodes_i) and self.edges_validator(graph_obj, nodes_r):
            if self.direction_validator(nodes_i, nodes_r):
                if self.stops_validator(nodes_i, stops_i) and self.stops_validator(nodes_r, stops_r):
                    return True

    @staticmethod
    def sequences_to_string(sequence_list):
        """
        to get a string with a sequences list
        :param sequence_list:
        :return:
        """

        line = ""

        for node in sequence_list:
            if line == "":
                line = line + node
            else:
                line = line + "-" + node

        return line

    @staticmethod
    def sequences_to_list(sequence):
        """
        to get a list with a sequence string
        :param sequence:
        :return:
        """
        nodes = sequence.split(",")

        if len(nodes) <= 1:
            raise SequencesLenExceptions("len(sequences) must be >=0")

        return nodes

    @staticmethod
    def stops_validator(nodes_list, stops_list):
        """
        to check if all stops of a direction of a route are a sub group of node_sequences. Also check if first and last
        nodes are stops
        :param nodes_list:
        :param stops_list:
        :return:
        """
        # to check if each stops be in node_sequences
        for stop in stops_list:
            if stop not in nodes_list:
                raise StopsSequencesExceptions("stop is not reachable")
        # to check if first stop is equal to first node in node sequences
        if nodes_list[0] != stops_list[0]:
            raise FirstStopIsNotValidExceptions("first stop is not valid, must be equal to first node")
        # to check if last stop is equal to last node in node sequences
        if nodes_list[len(nodes_list) - 1] != stops_list[len(stops_list) - 1]:
            raise LastStopIsNotValidExceptions("last stop is not valid, must be equal to last node")
        return True

    @staticmethod
    def direction_validator(nodes_list_i, nodes_list_r):
        """
        to check if both direction of a route form a cycle
        :param nodes_list_i:
        :param nodes_list_r:
        :return:
        """
        if nodes_list_i[0] != nodes_list_r[len(nodes_list_r) - 1] or \
                nodes_list_r[0] != nodes_list_i[len(nodes_list_r) - 1]:
            raise NotCycleExceptions("sequence of nodes of both directions do not form a cycle")
        return True

    @staticmethod
    def edges_validator(graph_obj, node_list):
        """
        to check if each edges in a node_sequences exist in the graph object
        :param graph_obj:
        :param node_list:
        :return:
        """

        for i in range(len(node_list) - 1):
            j = i + 1
            if not graph_obj.edge_exist(i, j):
                raise NodeSequencesNotValid("Node sequences is not valid because a edge does not exist")
        return True


class TransportNetwork:

    def __init__(self, graph_obj, modes_obj):
        self.__graph_obj = graph_obj
        self.__modes_obj = modes_obj
        self.__routes = []
        self.__routes_id = []

    def is_valid(self):
        """
        to check if Transport Network is valid
        :return:
        """
        # could be added a validation of whether the defined routes are specific to transport the defined demand,
        # very difficult to do
        if len(self.__routes) == 0:
            return False
        else:
            return True

    def get_routes(self):
        """
        to get all routes
        :return:
        """
        return self.__routes

    def get_route(self, route_id):
        """
        to get a specific route with a route_id
        :param route_id:
        :return:
        """
        if route_id in self.__routes_id:
            i = self.__routes_id.index(route_id)
            return self.__routes[i]
        else:
            raise RouteIdNotFoundExceptions("route_id not found")

    def add_route(self, route_id, mode_name, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                  stops_sequence_r):
        """
        to add a specific route in routes list
        :param route_id:
        :param mode_name:
        :param nodes_sequence_i:
        :param nodes_sequence_r:
        :param stops_sequence_i:
        :param stops_sequence_r:
        :return:
        """
        if route_id not in self.__routes_id:
            route = Route(self.__graph_obj, self.__modes_obj, route_id, mode_name, nodes_sequence_i,
                          nodes_sequence_r, stops_sequence_i, stops_sequence_r)
            self.__routes.append(route)
            self.__routes_id.append(route_id)
        else:
            raise RouteIdDuplicatedExceptions("route_id is duplicated")

    def delete_route(self, route_id):
        """
        to delete a specific route_id in list of routes
        :param route_id:
        :return:
        """
        if route_id in self.__routes_id:
            i = self.__routes_id.index(route_id)
            self.__routes_id.pop(i)
            self.__routes.pop(i)
        else:
            raise RouteIdNotFoundExceptions("route_id not found")

    def route_to_file(self, file_path):
        """
        to save file with all routes information
        :param file_path:
        :return:
        """
        # route_id, mode_name, nodes_sequence_i, nodes_sequence_r, stops_sequence_i, stops_sequence_r
        col_route_id = []
        col_mode = []
        col_nodes_sequence_i = []
        col_nodes_sequence_r = []
        col_stops_sequence_i = []
        col_stops_sequence_r = []

        for route in self.__routes:

            col_route_id.append(route.id)
            col_mode.append(route.mode)
            col_nodes_sequence_i.append(route.sequences_to_string(route.nodes_sequence_i))
            col_nodes_sequence_r.append(route.sequences_to_string(route.nodes_sequence_r))
            col_stops_sequence_i.append(route.sequences_to_string(route.stops_sequence_i))
            col_stops_sequence_r.append(route.sequences_to_string(route.stops_sequence_r))

        df_transit_network = pd.DataFrame()
        df_transit_network["route_id"] = col_route_id
        df_transit_network["mode"] = col_mode
        df_transit_network["nodes_sequence_i"] = col_nodes_sequence_i
        df_transit_network["nodes_sequence_r"] = col_nodes_sequence_r
        df_transit_network["stops_sequence_i"] = col_stops_sequence_i
        df_transit_network["stops_sequence_r"] = col_stops_sequence_r

        df_transit_network.to_csv(file_path, sep=",", index=False)

    @staticmethod
    def build_from_file(file_path):
        """
        to build route list from a file
        :param file_path:
        :return:
        """
        pass


    def update_route(self, route_id, mode_name=None, nodes_sequence_i=None,
                          nodes_sequence_r=None, stops_sequence_i=None, stops_sequence_r=None):
        """
        to update route information
        :param route_id:
        :return:
        """
        pass
