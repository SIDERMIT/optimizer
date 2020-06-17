class route:

    def __init__(self, graph_obj, modes_obj, route_id, mode, node_sequences_i, node_Sequence_r, stop_sequence_i,
                 stop_Sequence_r):
        pass

    @staticmethod
    def parameters_validator(graph_obj, modes_obj, route_id, mode_name, node_sequences_i, node_sequence_r,
                             stop_sequence_i, stop_sequence_r):

        modes_names = modes_obj.get_modes_names()

        if route_id is None:
            raise RouteIdIsNotValidExceptions("route_id is not valid. Try to give a value for route_id")

        if mode_name not in modes_names:
            raise ModeNameIsNotValidExceptions("mode_name was not define in modes_obj")

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
        if nodes_list_i[0] != nodes_list_r[len(nodes_list_r) - 1] or nodes_list_r[0] != nodes_list_i[
            len(nodes_list_r) - 1]:
            raise NotCycleExceptions("sequence of nodes of both directions do not form a cycle")
        return True

    @staticmethod
    def edges_validator(stops_list):
        return True
