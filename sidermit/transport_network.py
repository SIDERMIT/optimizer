from sidermit.exceptions import *


class route:

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
    def sequences_to_list(sequence):

        nodes = sequence.split(",")

        if len(nodes) <= 1:
            raise SequencesLenExceptions("len(sequences) must be >=0")

        return nodes

    @staticmethod
    def stops_validator(nodes_list, stops_list):
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
        if nodes_list_i[0] != nodes_list_r[len(nodes_list_r) - 1] or \
                nodes_list_r[0] != nodes_list_i[len(nodes_list_r) - 1]:
            raise NotCycleExceptions("sequence of nodes of both directions do not form a cycle")
        return True

    @staticmethod
    def edges_validator(graph_obj, node_list):

        for i in range(len(node_list) - 1):
            j = i + 1
            if not graph_obj.edge_exist(i, j):
                raise NodeSequencesNotValid("Node sequences is not valid because a edge does not exist")
        return True

class TransportNetwork:

    def __init__(self, graph_obj, modes_obj):
        self.__routes = []
        self.__routes_id = []

    def is_valid(self):

        if len(self.__routes) == 0:
            return False
        else:
            return True
