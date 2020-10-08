import math
from collections import defaultdict
from enum import Enum
from typing import List

import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt

from sidermit.city import Graph, CBD, Periphery, Subcenter
from sidermit.exceptions import *
from sidermit.publictransportsystem import TransportMode, TransportModeManager


class RouteType(Enum):
    """
    route types, CUSTOM for user-created custom routes, PREDEFINED for predefined routes created by a method of the
    TransportNetwork class, CIRCULAR to a special type of predefined route with different construction rules
    """
    CUSTOM = 1
    PREDEFINED = 2
    CIRCULAR = 3


class Route:

    def __init__(self, route_id, mode_obj: TransportMode, nodes_sequence_i: str, nodes_sequence_r: str,
                 stops_sequence_i: str, stops_sequence_r: str, _type: RouteType = RouteType.CUSTOM):
        """
        to defined a route
        :param route_id: route id
        :param mode_obj: TransportMode object. Means of transport of the route
        :param nodes_sequence_i: sequence of id nodes of the city graph where the route travels in the forward direction
        :param nodes_sequence_r: sequence of id nodes of the city graph where the route travels in the return direction
        :param stops_sequence_i: sequence of id nodes of the city graph where the route stops in the forward direction
        :param stops_sequence_r: sequence of id nodes of the city graph where the route stops in the return direction
        :param _type: RouteType, default value CUSTOM.
        """
        self.id = None
        self.mode = None
        self.nodes_sequence_i = None
        self.nodes_sequence_r = None
        self.stops_sequence_i = None
        self.stops_sequence_r = None
        self._type = _type
        if _type == RouteType.CUSTOM and (
                nodes_sequence_i is None or nodes_sequence_r is None or nodes_sequence_i == "" or nodes_sequence_r == ""):
            raise NodeSequencesIsNotValidException("You should give a value for nodes_sequence_i and nodes_sequence_r")
        if _type == RouteType.CUSTOM and (
                stops_sequence_i is None or stops_sequence_r is None or stops_sequence_i == "" or stops_sequence_r == ""):
            raise StopSequenceIsNotValidException("You should give a value for stops_sequence_i and stops_sequence_r")

        if route_id is None:
            raise RouteIdIsNotValidException("route_id is not valid. Try to give a value for route_id")

        # special case for circular routes
        if _type == RouteType.PREDEFINED or _type == RouteType.CIRCULAR:
            self.id = route_id
            self.mode = mode_obj
            self.nodes_sequence_i = self.sequences_to_list(nodes_sequence_i)
            self.nodes_sequence_r = self.sequences_to_list(nodes_sequence_r)
            self.stops_sequence_i = self.sequences_to_list(stops_sequence_i)
            self.stops_sequence_r = self.sequences_to_list(stops_sequence_r)

        else:
            # to valid parameters
            if self.parameters_validator(mode_obj,
                                         nodes_sequence_i, nodes_sequence_r,
                                         stops_sequence_i, stops_sequence_r):
                self.id = route_id
                self.mode = mode_obj
                self.nodes_sequence_i = self.sequences_to_list(nodes_sequence_i)
                self.nodes_sequence_r = self.sequences_to_list(nodes_sequence_r)
                self.stops_sequence_i = self.sequences_to_list(stops_sequence_i)
                self.stops_sequence_r = self.sequences_to_list(stops_sequence_r)

    def parameters_validator(self, mode_obj: TransportMode, nodes_sequence_i: str, nodes_sequence_r: str,
                             stops_sequence_i: str, stops_sequence_r: str) -> bool:
        """
        to check all parameters
        :param mode_obj: TransportMode object. Means of transport of the route
        :param nodes_sequence_i: sequence of id nodes of the city graph where the route travels in the forward direction
        :param nodes_sequence_r: sequence of id nodes of the city graph where the route travels in the return direction
        :param stops_sequence_i: sequence of id nodes of the city graph where the route stops in the forward direction
        :param stops_sequence_r: sequence of id nodes of the city graph where the route stops in the return direction
        :return: True if parameters are valid. Exception if not.
        """
        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        nodes_i = self.sequences_to_list(nodes_sequence_i)
        nodes_r = self.sequences_to_list(nodes_sequence_r)
        stops_i = self.sequences_to_list(stops_sequence_i)
        stops_r = self.sequences_to_list(stops_sequence_r)

        if self.direction_validator(nodes_i, nodes_r):
            if self.stops_validator(nodes_i, stops_i) and self.stops_validator(nodes_r, stops_r):
                if self.sequences_validator(nodes_i) and self.sequences_validator(nodes_r):
                    return True

    @staticmethod
    def sequences_to_string(sequence_list: List[str]) -> str:
        """
        convert a node id sequence list to a string
        :param sequence_list: node id sequence list
        :return: String
        """
        line = ""
        for node in sequence_list:
            if line == "":
                line = line + str(node)
            else:
                line = line + "," + str(node)
        return line

    @staticmethod
    def sequences_to_list(sequence: str) -> List[int]:
        """
        convert a string of node id sequence to a list
        :param sequence: String
        :return: List[node id]
        """
        if sequence == "":
            return []

        nodes_split = sequence.split(",")
        nodes = []

        for node in nodes_split:
            nodes.append(int(node.rstrip("\n")))

        return nodes

    @staticmethod
    def stops_validator(nodes_list: List[int], stops_list: List[int]) -> bool:
        """
        to check if all stops of a direction of a route are a sub group of node_sequences. Also check if first and last
        nodes are stops
        :param nodes_list: list of node sequence
        :param stops_list: list of stops sequence
        :return: True if parameters are valid. Raise a exceptions if not
        """
        # to check if each stops be in node_sequences
        for stop in stops_list:
            if stop not in nodes_list:
                raise StopsSequencesException("stop is not reachable")
        # to check if first stop is equal to first node in node sequences
        if nodes_list[0] != stops_list[0]:
            raise FirstStopIsNotValidException("first stop is not valid, must be equal to first node")
        # to check if last stop is equal to last node in node sequences
        if nodes_list[len(nodes_list) - 1] != stops_list[len(stops_list) - 1]:
            raise LastStopIsNotValidException("last stop is not valid, must be equal to last node")
        return True

    @staticmethod
    def direction_validator(nodes_list_i: List[int], nodes_list_r: List[int]) -> bool:
        """
        to check if both direction of a route form a cycle
        :param nodes_list_i: list of node sequence (forward direction)
        :param nodes_list_r: list of node sequence (return direction)
        :return: True if parameters are valid. Raise a exceptions if not.
        """
        if nodes_list_i[0] != nodes_list_r[len(nodes_list_r) - 1] or \
                nodes_list_r[0] != nodes_list_i[len(nodes_list_i) - 1]:
            raise NotCycleException("sequence of nodes of both directions do not form a cycle")
        return True

    @staticmethod
    def sequences_validator(sequence: List[int]) -> bool:
        """
        to check if sequence have a loop
        :param sequence: list of node sequence
        :return: True if parameters are valid. Raise a exceptions if not.
        """

        for node1 in sequence:
            n = 0
            for node2 in sequence:
                if node1 == node2:
                    n = n + 1
            if n > 1:
                raise NodeSequencesIsNotValidException("node sequence loops")

        return True


class TransportNetwork:

    def __init__(self, graph_obj: Graph):
        """
        transport route manager on a city graph
        :param graph_obj: Graph where transport network develops
        """
        self.__graph_obj = graph_obj
        self.__routes = []
        self.__routes_id = []
        self.__modes = []

    def __edges_validator(self, node_list: List[int]) -> bool:
        """
        to check if each edges in a node_sequences list exist in the graph object
        :param node_list: list of nodes
        :return: True if parameters are valid. Raise a exceptions if not.
        """
        for i in range(len(node_list) - 1):
            j = i + 1
            if not self.__graph_obj.edge_exist(node_list[i], node_list[j]):
                raise NodeSequencesIsNotValidException("Node sequences is not valid because a edge does not exist")
        return True

    def get_modes(self) -> List[TransportMode]:
        return self.__modes

    def get_routes(self) -> List[Route]:
        """
        to get all routes
        :return: List[Route]
        """
        return self.__routes

    def get_route(self, route_id) -> Route:
        """
        to get a specific route by a route_id
        :param route_id: route id
        :return: Route object if route id is defined in the network. Raise a exceptions if not.
        """
        if route_id in self.__routes_id:
            i = self.__routes_id.index(route_id)
            return self.__routes[i]
        else:
            raise RouteIdNotFoundException("route_id not found")

    def add_transport_mode(self, mode: TransportMode):
        """
        to add a transport mode in the network
        :param mode: TransportMode
        :return:
        """

        if mode not in self.__modes:

            mode_manager = TransportModeManager(add_default_mode=False)

            list_mode = [mode]

            for modes in self.__modes:
                if modes not in list_mode:
                    list_mode.append(modes)

            for modes in list_mode:
                mode_manager.add_mode(modes)

            if mode_manager.is_valid_to_assignment_step():
                self.__modes.append(mode)
            else:
                raise TransportModeException(
                    "only 2 transport mode can be defined and at least one should have d parameter = 1")

    def remove_transport_mode(self, mode: TransportMode):
        """
        to remove a transport mode in the network and all lines defined with that transport mode
        :param mode: TransportMode
        :return:
        """

        list_mode = []

        for modes in self.__modes:
            if modes != mode:
                list_mode.append(modes)

        self.__modes = list_mode

        for route in self.__routes:
            if route.mode == mode:
                self.remove_route(route.id)

    def add_route(self, route_obj: Route):
        """
        to add a specific route in routes list
        :param route_obj: Route object
        :return:
        """
        if not isinstance(route_obj, Route):
            raise RouteIsNotvalidException("route_obj is not valid")

        route_id = route_obj.id
        nodes_sequence_i = route_obj.nodes_sequence_i
        nodes_sequence_r = route_obj.nodes_sequence_r

        if self.__edges_validator(nodes_sequence_i) or self.__edges_validator(nodes_sequence_r):
            if route_id not in self.__routes_id:
                self.add_transport_mode(route_obj.mode)
                self.__routes.append(route_obj)
                self.__routes_id.append(route_id)
            else:
                raise RouteIdDuplicatedException("route_id is duplicated")

    def remove_route(self, route_id):
        """
        to delete a specific route_id in the network
        :param route_id: route id
        :return:
        """
        if route_id in self.__routes_id:
            i = self.__routes_id.index(route_id)
            self.__routes_id.pop(i)
            self.__routes.pop(i)
        else:
            raise RouteIdNotFoundException("route_id not found")

    def routes_to_file(self, file_path):
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
            col_mode.append(route.mode.name)
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

        df_transit_network.to_csv(file_path, sep=";", index=False, encoding="utf-8")

    def get_circular_routes(self, mode_obj: TransportMode) -> List[Route]:
        """
        to get predefined circular routes, 2 routes with only a direction and whose stops and nodes sequence are all
        subcenter nodes.
        :param mode_obj: transport Mode
        :return: List[Route]
        """

        zones = self.__graph_obj.get_zones()
        if len(zones) <= 1:
            raise CircularRouteIsNotValidException("to add a predefined circular route you have a city "
                                                   "with more of one zone created")

        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        mode_name = mode_obj.name

        route_id_i = "CIR_I_{}".format(mode_name)
        route_id_r = "CIR_R_{}".format(mode_name)

        nodes_sequence_i = ""
        nodes_sequence_r = ""

        for i in range(len(zones)):

            if nodes_sequence_i == "":
                nodes_sequence_i = nodes_sequence_i + str(zones[i].subcenter.id)
                nodes_sequence_r = nodes_sequence_r + str(zones[len(zones) - 1 - i].subcenter.id)
            else:
                nodes_sequence_i = nodes_sequence_i + "," + str(zones[i].subcenter.id)
                nodes_sequence_r = nodes_sequence_r + "," + str(zones[len(zones) - 1 - i].subcenter.id)

        nodes_sequence_i = nodes_sequence_i + "," + str(zones[0].subcenter.id)
        nodes_sequence_r = nodes_sequence_r + "," + str(zones[len(zones) - 1].subcenter.id)

        stops_sequence_i = nodes_sequence_i
        stops_sequence_r = nodes_sequence_r

        route1 = Route(route_id_i, mode_obj, nodes_sequence_i, "", stops_sequence_i, "", _type=RouteType.CIRCULAR)
        route2 = Route(route_id_r, mode_obj, "", nodes_sequence_r, "", stops_sequence_r, _type=RouteType.CIRCULAR)

        return [route1, route2]

    def get_feeder_routes(self, mode_obj: TransportMode) -> List[Route]:
        """
        to get predefined feeder routes, where for each zone exist a route with nodes and stops sequences beetween
        p-sc for I direction and sc-p for R direction.
        :param mode_obj: TransportMode
        :return: List[Route]
        """

        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        mode_name = mode_obj.name

        routes = []
        for zone in self.__graph_obj.get_zones():
            id_p = zone.periphery.id
            id_sc = zone.subcenter.id

            route_id = "F_{}_{}".format(mode_name, zone.id)
            nodes_sequence_i = "{},{}".format(id_p, id_sc)
            stops_sequence_i = nodes_sequence_i
            nodes_sequence_r = "{},{}".format(id_sc, id_p)
            stops_sequence_r = nodes_sequence_r

            route = Route(route_id, mode_obj, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                          stops_sequence_r, _type=RouteType.PREDEFINED)

            routes.append(route)

        return routes

    def get_radial_routes(self, mode_obj: TransportMode, short: bool = False, express: bool = False) -> List[Route]:
        """
        to get predefined radial routes, where for each zone exist a route with nodes and stops sequences beetween
        p-sc-cbd for I direction and cbd-sc-p for R direction.
        :param mode_obj: TransportMode
        :param short: if radial routes omit the passage through the periphery (default: False)
        :param express: if radial routes omit to stop in the subcenter (default: False)
        :return: List[Route]
        """

        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        mode_name = mode_obj.name

        cbd = self.__graph_obj.get_cbd()
        id_cbd = cbd.id

        routes = []

        for zone in self.__graph_obj.get_zones():

            id_p = zone.periphery.id
            id_sc = zone.subcenter.id

            if short is True:
                route_id = "RS_{}_{}".format(mode_name, zone.id)
                nodes_sequence_i = "{},{}".format(id_sc, id_cbd)
                stops_sequence_i = nodes_sequence_i
                nodes_sequence_r = "{},{}".format(id_cbd, id_sc)
                stops_sequence_r = nodes_sequence_r
            else:
                if express is True:
                    route_id = "RE_{}_{}".format(mode_name, zone.id)
                    nodes_sequence_i = "{},{},{}".format(id_p, id_sc, id_cbd)
                    stops_sequence_i = "{},{}".format(id_p, id_cbd)
                    nodes_sequence_r = "{},{},{}".format(id_cbd, id_sc, id_p)
                    stops_sequence_r = "{},{}".format(id_cbd, id_p)
                else:
                    route_id = "R_{}_{}".format(mode_name, zone.id)
                    nodes_sequence_i = "{},{},{}".format(id_p, id_sc, id_cbd)
                    stops_sequence_i = nodes_sequence_i
                    nodes_sequence_r = "{},{},{}".format(id_cbd, id_sc, id_p)
                    stops_sequence_r = nodes_sequence_r

            route = Route(route_id, mode_obj, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                          stops_sequence_r, _type=RouteType.PREDEFINED)
            routes.append(route)

        return routes

    def get_diametral_routes(self, mode_obj: TransportMode, jump: int = 1, short: bool = False,
                             express: bool = False) -> List[Route]:
        """
        to get predefined diametral routes, where for each zone exist a route with nodes and stops sequences beetween
        p-sc-cbd-sc'-p' for I direction and p'-sc'-cbd-sc-p for R direction. p' and sc' are periphery and subcenter
        nodes with zone id equivalent to the id of the treated zone plus the jump
        :param mode_obj: TransportMode
        :param jump: to identified other zone where diametral routes transit
        :param short: if diametral routes omit the passage through the periphery (default: False)
        :param express: if diametral routes omit to stop in the subcenter and cbd nodes  (default: False)
        :return: List[Route]
        """
        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        mode_name = mode_obj.name

        cbd = self.__graph_obj.get_cbd()
        id_cbd = cbd.id

        zones = self.__graph_obj.get_zones()

        if jump > len(zones) / 2 or jump <= 0 or not isinstance(jump, int):
            raise JumpIsNotValidException("jump must be a int in range (0-n° zones)")

        end = len(zones)
        if len(zones) % 2.0 == 0 and jump == math.floor(len(zones) / 2):
            end = math.floor(len(zones) / 2)

        routes = []

        for zone in zones[:end]:
            id_p = zone.periphery.id
            id_sc = zone.subcenter.id

            zone_id = zone.id

            if zone_id + jump <= len(zones):
                zone2_id = zone_id + jump
            else:
                zone2_id = zone_id + jump - len(zones)

            # zones are sort per id in list
            zone2 = zones[zone2_id - 1]

            id_p2 = zone2.periphery.id
            id_sc2 = zone2.subcenter.id

            if short is True:
                if express is True:
                    route_id = "DSE{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{},{}".format(id_sc, id_cbd, id_sc2)
                    stops_sequence_i = "{},{}".format(id_sc, id_sc2)
                    nodes_sequence_r = "{},{},{}".format(id_sc2, id_cbd, id_sc)
                    stops_sequence_r = "{},{}".format(id_sc2, id_sc)
                else:
                    route_id = "DS{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{},{}".format(id_sc, id_cbd, id_sc2)
                    stops_sequence_i = nodes_sequence_i
                    nodes_sequence_r = "{},{},{}".format(id_sc2, id_cbd, id_sc)
                    stops_sequence_r = nodes_sequence_r
            else:
                if express is True:
                    route_id = "DE{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{},{},{},{}".format(id_p, id_sc, id_cbd, id_sc2, id_p2)
                    stops_sequence_i = "{},{}".format(id_p, id_p2)
                    nodes_sequence_r = "{},{},{},{},{}".format(id_p2, id_sc2, id_cbd, id_sc, id_p)
                    stops_sequence_r = "{},{}".format(id_p2, id_p)
                else:
                    route_id = "D{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{},{},{},{}".format(id_p, id_sc, id_cbd, id_sc2, id_p2)
                    stops_sequence_i = nodes_sequence_i
                    nodes_sequence_r = "{},{},{},{},{}".format(id_p2, id_sc2, id_cbd, id_sc, id_p)
                    stops_sequence_r = nodes_sequence_r
            route = Route(route_id, mode_obj, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                          stops_sequence_r, _type=RouteType.PREDEFINED)
            routes.append(route)

        return routes

    def get_tangencial_routes(self, mode_obj: TransportMode, jump: int = 1, short: bool = False,
                              express: bool = False) -> List[Route]:
        """
        to get predefined tangencial routes, where for each zone exist a route with nodes and stops sequences beetween
        p-sc-sc'-...-sc''-p'' for I direction and p''-sc''-...-sc'-sc-p for R direction. sc', ..., sc'' are subcenter
        nodes with zone id less than or equal to id of the treated zone plus the jump. p'' and sc'' are periphery
        and subcenter nodes with id equivalent to the id of the treated zone plus the jump
        :param mode_obj: TransportMode
        :param jump: to identified other zone where tangencial routes transit
        :param short: if radial routes omit the passage through the periphery (default: False)
        :param express: if radial routes omit to stop in the subcenters nodes (default: False)
        :return: List[Route]
        """
        if not isinstance(mode_obj, TransportMode):
            raise ModeIsNotValidException("mode obj is not valid")

        mode_name = mode_obj.name

        zones = self.__graph_obj.get_zones()

        if jump > len(zones) / 2 or jump <= 0 or not isinstance(jump, int):
            raise JumpIsNotValidException("jump must be a int in range (0-n° zones)")

        end = len(zones)
        if len(zones) % 2.0 == 0 and jump == math.floor(len(zones) / 2):
            end = math.floor(len(zones) / 2)

        routes = []

        for zone in zones[:end]:
            id_p = zone.periphery.id
            id_sc = zone.subcenter.id

            zone_id = zone.id

            if zone_id + jump <= len(zones):
                zone2_id = zone_id + jump
            else:
                zone2_id = zone_id + jump - len(zones)

            # zones are sort per id in list
            zone2 = zones[zone2_id - 1]

            id_p2 = zone2.periphery.id
            id_sc2 = zone2.subcenter.id

            list_zones_id = []

            if zone2_id > zone_id and jump != 1:
                for i in range(zone_id + 1, zone2_id):
                    list_zones_id.append(i)

            if zone2_id < zone_id:
                if zone_id != len(zones):
                    for i in range(zone_id + 1, len(zones) + 1):
                        list_zones_id.append(i)

                for i in range(1, zone2_id):
                    list_zones_id.append(i)

            if short is True:
                if express is True:
                    route_id = "TSE{}_{}_{}".format(jump, mode_name, zone.id)

                    nodes_sequence_i = "{}".format(id_sc)
                    nodes_sequence_r = "{}".format(id_sc2)

                    for i in range(len(list_zones_id)):
                        zone3 = zones[list_zones_id[i] - 1]
                        zone4 = zones[list_zones_id[len(list_zones_id) - 1 - i] - 1]

                        nodes_sequence_i = nodes_sequence_i + "," + str(zone3.subcenter.id)
                        nodes_sequence_r = nodes_sequence_r + "," + str(zone4.subcenter.id)

                    nodes_sequence_i = nodes_sequence_i + "," + str("{}".format(id_sc2))
                    nodes_sequence_r = nodes_sequence_r + "," + str("{}".format(id_sc))

                    stops_sequence_i = "{},{}".format(id_sc, id_sc2)
                    stops_sequence_r = "{},{}".format(id_sc2, id_sc)

                else:
                    route_id = "TS{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{}".format(id_sc)
                    nodes_sequence_r = "{}".format(id_sc2)
                    for i in range(len(list_zones_id)):
                        zone3 = zones[list_zones_id[i] - 1]
                        zone4 = zones[list_zones_id[len(list_zones_id) - 1 - i] - 1]

                        nodes_sequence_i = nodes_sequence_i + "," + str(zone3.subcenter.id)
                        nodes_sequence_r = nodes_sequence_r + "," + str(zone4.subcenter.id)
                    nodes_sequence_i = nodes_sequence_i + "," + "{}".format(id_sc2)
                    nodes_sequence_r = nodes_sequence_r + "," + "{}".format(id_sc)
                    stops_sequence_i = nodes_sequence_i
                    stops_sequence_r = nodes_sequence_r

            else:
                if express is True:
                    route_id = "TE{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{}".format(id_p, id_sc)
                    nodes_sequence_r = "{},{}".format(id_p2, id_sc2)
                    for i in range(len(list_zones_id)):
                        zone3 = zones[list_zones_id[i] - 1]
                        zone4 = zones[list_zones_id[len(list_zones_id) - 1 - i] - 1]

                        nodes_sequence_i = nodes_sequence_i + "," + str(zone3.subcenter.id)
                        nodes_sequence_r = nodes_sequence_r + "," + str(zone4.subcenter.id)
                    nodes_sequence_i = nodes_sequence_i + "," + "{},{}".format(id_sc2, id_p2)
                    nodes_sequence_r = nodes_sequence_r + "," + "{},{}".format(id_sc, id_p)
                    stops_sequence_i = "{},{}".format(id_p, id_p2)
                    stops_sequence_r = "{},{}".format(id_p2, id_p)
                else:
                    route_id = "T{}_{}_{}".format(jump, mode_name, zone.id)
                    nodes_sequence_i = "{},{}".format(id_p, id_sc)
                    nodes_sequence_r = "{},{}".format(id_p2, id_sc2)
                    for i in range(len(list_zones_id)):
                        zone3 = zones[list_zones_id[i] - 1]
                        zone4 = zones[list_zones_id[len(list_zones_id) - 1 - i] - 1]

                        nodes_sequence_i = nodes_sequence_i + "," + str(zone3.subcenter.id)
                        nodes_sequence_r = nodes_sequence_r + "," + str(zone4.subcenter.id)
                    nodes_sequence_i = nodes_sequence_i + "," + "{},{}".format(id_sc2, id_p2)
                    nodes_sequence_r = nodes_sequence_r + "," + "{},{}".format(id_sc, id_p)
                    stops_sequence_i = nodes_sequence_i
                    stops_sequence_r = nodes_sequence_r

            route = Route(route_id, mode_obj, nodes_sequence_i, nodes_sequence_r, stops_sequence_i,
                          stops_sequence_r, _type=RouteType.PREDEFINED)
            routes.append(route)

        return routes

    def plot(self, file_path, list_routes=None, direction=None):
        """
        to plot network and graph
        :param file_path:
        :param list_routes: list of routes to plot, default value is None and plot all routes
        :param direction: "I" or "R" direction to plot. default value is None and plot both direction.
        :return:
        """
        # if list routes is empty then plot all routes
        if list_routes is None:
            list_routes = self.__routes_id

        # edges information and positions
        # edge city
        edges_graph = []
        position = defaultdict(list)
        for edge in self.__graph_obj.get_edges():
            edges_graph.append((edge.node1.id, edge.node2.id))
            if not position.get(edge.node1.id):
                position[edge.node1.id].append(edge.node1.x)
                position[edge.node1.id].append(edge.node1.y)
            if not position.get(edge.node2.id):
                position[edge.node2.id].append(edge.node2.x)
                position[edge.node2.id].append(edge.node2.y)

        # nodes information and positions
        info_cbd = []
        info_sc = []
        info_p = []
        id_cbd = []
        id_sc = []
        id_p = []
        x_cbd = []
        y_cbd = []
        x_sc = []
        y_sc = []
        x_p = []
        y_p = []

        for node in self.__graph_obj.get_nodes():
            if isinstance(node, CBD):
                info_cbd.append(node)
            if isinstance(node, Periphery):
                info_p.append(node)
            if isinstance(node, Subcenter):
                info_sc.append(node)

        for cbd in info_cbd:
            x_cbd.append(cbd.x)
            y_cbd.append(cbd.y)
            id_cbd.append(cbd.id)

        for sc in info_sc:
            x_sc.append(sc.x)
            y_sc.append(sc.y)
            id_sc.append(sc.id)
        for p in info_p:
            x_p.append(p.x)
            y_p.append(p.y)
            id_p.append(p.id)

        # edges routes and stops
        edges_i = []
        edges_r = []
        stops_i = []
        stops_r = []
        for route_id in list_routes:
            if route_id not in self.__routes_id:
                raise RouteIdNotFoundException("route_id does not found")
            else:
                ind = self.__routes_id.index(route_id)
                route = self.__routes[ind]
                nodes_i = route.nodes_sequence_i
                nodes_r = route.nodes_sequence_r
                stop_i = route.stops_sequence_i
                stop_r = route.stops_sequence_r

                for i in range(len(nodes_i) - 1):
                    id1 = nodes_i[i]
                    id2 = nodes_i[i + 1]
                    edges_i.append((id1, id2))
                for i in range(len(nodes_r) - 1):
                    id1 = nodes_r[i]
                    id2 = nodes_r[i + 1]
                    edges_r.append((id1, id2))
                for i in range(len(stop_i)):
                    if stop_i[i] not in stops_i:
                        stops_i.append(stop_i[i])
                for i in range(len(stop_r)):
                    if stop_r[i] not in stops_r:
                        stops_r.append(stop_r[i])

        G = nx.DiGraph()
        G.add_edges_from(edges_graph)
        G.add_edges_from(edges_i)
        G.add_edges_from(edges_r)

        # separate calls to draw labels, nodes and edges
        # plot p, Sc and CBD
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_p, node_color='red', node_size=300)
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_sc, node_color='blue', node_size=300)
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_cbd, node_color='purple',
                               node_size=300)
        # plot stops
        if direction is None or direction == "I":
            nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=stops_i, node_color='yellow',
                                   node_size=300)
        if direction is None or direction == "R":
            nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=stops_r, node_color='yellow',
                                   node_size=300)
        # plot labels
        nx.draw_networkx_labels(G, position)
        # plot edges city
        nx.draw_networkx_edges(G, position, edgelist=edges_graph, edge_color='orange', arrows=True)
        # plot edges_i
        if direction is None or direction == "I":
            nx.draw_networkx_edges(G, position, edgelist=edges_i, edge_color='lime', arrows=True)
        # plot edges_r
        if direction is None or direction == "R":
            nx.draw_networkx_edges(G, position, edgelist=edges_r, edge_color='aqua', arrows=True)

        plt.title("City graph")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().set_aspect('equal')
        plt.savefig(file_path)
