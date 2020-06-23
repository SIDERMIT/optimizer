import math
from collections import defaultdict
from enum import Enum

import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt

from sidermit.exceptions import *


class GraphFileFormat(Enum):
    # Pajek reference: https://gephi.org/users/supported-graph-formats/pajek-net-format/
    # [node_id] [node name] [x] [y] [type] [zone] [width]
    PAJEK = 1


class Zone:

    def __init__(self, zone_id, node_periphery, node_subcenter):

        if zone_id is None:
            raise ZoneIdIsNotValidException("zone_id is not valid")
        if zone_id <= 0:
            raise ZoneIdIsNotValidException("zone_id number must be >=1")
        if not isinstance(node_periphery, Periphery):
            raise PeripheryNodeTypeIsNotValidException('node must be periphery')

        if not isinstance(node_subcenter, Subcenter):
            raise SubcenterNodeTypeIsNotValidException('node must be subcenter')

        if node_periphery.zone_id != zone_id or node_subcenter.zone_id != zone_id:
            raise ZoneIdIsNotValidException("node_periphery and node_subcenter must be equal to zone_id")

        self.id = zone_id
        self.periphery = node_periphery
        self.subcenter = node_subcenter


class Node:

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        if name is None:
            raise NameIsNotDefinedException("must define a name to node")
        if node_id is None:
            raise NodeIdIsNotValidException("zone_id is not valid")
        if zone_id is None:
            raise ZoneIdIsNotValidException("zone_id is not valid")
        if radius < 0:
            raise NodeRadiusIsNotValidException("radius must be positive")
        if angle < 0 or angle > 360:
            raise NodeAngleIsNotValidException("angle must belong into range [0-360]")
        if width < 0:
            raise NodeWidthIsNotValidException("width must be >= 0")
        self.id = node_id
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle
        self.width = width
        self.name = name
        self.zone_id = zone_id


class CBD(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        if zone_id != 0:
            raise ZoneIdIsNotValidException("CBD node_id must be equal to 0")
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Periphery(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Subcenter(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Edge:

    def __init__(self, edge_id, node1, node2):
        if edge_id is None:
            raise EdgeIdIsNotValidException("edge_id is not valid")
        if isinstance(node1, Periphery) and isinstance(node2, Periphery):
            raise EdgeIsNotAvailableException("edge between periphery nodes is not available")
        if isinstance(node1, Periphery) and isinstance(node2, CBD):
            raise EdgeIsNotAvailableException("edge between periphery and CBD is not available")
        if isinstance(node1, CBD) and isinstance(node2, Periphery):
            raise EdgeIsNotAvailableException("edge between periphery and CBD is not available")
        self.id = edge_id
        self.node1 = node1
        self.node2 = node2


class Graph:

    def __init__(self):

        self.__nodes_id = []
        self.__edges_id = []
        self.__cbd_exist = False

        self.__zones = []
        self.__nodes = []
        self.__edges = []

        self.__n = None
        self.__l = None
        self.__g = None
        self.__p = None
        self.__etha = None
        self.__etha_zone = None
        self.__angles = None
        self.__Gi = None
        self.__Hi = None

    def edge_exist(self, id_i, id_j):
        """
        to check if edge with origin node id = id_i and destination node id = id_j exist
        :param id_i:
        :param id_j:
        :return:
        """
        for edge in self.__edges:
            if str(edge.node1.id) == str(id_i) and str(edge.node2.id) == str(id_j):
                return True
        return False

    def graph_to_pajek(self, file_path):
        """
        Serialize graph data to file using Pajek format
        :param file_path: file path
        :return: None
        """

        file = open(file_path, 'w')
        file.write("*vertices {}{}".format(len(self.__nodes), "\n"))
        for node_obj in self.__nodes:
            node_type = None
            if isinstance(node_obj, CBD):
                node_type = 'CBD'
            elif isinstance(node_obj, Periphery):
                node_type = 'P'
            elif isinstance(node_obj, Subcenter):
                node_type = 'SC'

            file.write("{0} {1} {2} {3} {4} {5} {6}\n".
                       format(node_obj.id, node_obj.name, node_obj.x, node_obj.y, node_type, node_obj.zone_id,
                              node_obj.width))
        file.close()

    @staticmethod
    def parameters_validator(n, l, g, p, etha=None, etha_zone=None, angles=None, Gi=None, Hi=None):
        """
        to validate parameters
        :param n:
        :param l:
        :param g:
        :param p:
        :param etha:
        :param etha_zone:
        :param angles:
        :param Gi:
        :param Hi:
        :return:
        """
        if n < 0 or not isinstance(n, int):
            raise NIsNotValidNumberException('n cannot be a negative number')
        if l < 0:
            raise LIsNotValidNumberException('L cannot be a negative number')
        if g < 0:
            raise GIsNotValidNumberException('G cannot be a negative number')
        if p < 0:
            raise PIsNotValidNumberException('n cannot be a negative number')
        if etha is None and etha_zone is not None:
            raise EthaValueRequiredException("must give value for etha")
        if etha is not None and etha_zone is None:
            raise EthaZoneValueRequiredException("must give value for etha zone")
        if etha is not None and etha_zone is not None:
            if etha < 0 or etha > 1:
                raise EthaValueIsNotValidException("etha value is not valid. Try with value belong in [0-1]")
            elif etha_zone <= 0 or etha_zone > n or not isinstance(etha_zone, int):
                raise EthaZoneValueIsNotValidException("etha zone is not valid. Try with value belong in [1,...,n]")
        if angles is not None:
            if len(angles) != n:
                raise AngleListLengthIsNotValidException("must give angle value for all zones")
            for angle in angles:
                if angle < 0 or angle > 360:
                    raise AngleValueIsNotValidException("angle must belong in range [0°-360°]")
        if Gi is not None:
            if len(Gi) != n:
                raise GiListLengthIsNotValidException("must give Gi value for all zones")
            for gi in Gi:
                if gi < 0:
                    raise GiValueIsNotValidException("Gi must be >= 0")
        if Hi is not None:
            if len(Hi) != n:
                raise HiListLengthIsNotValidException("must give Hi value for all zones")
            for hi in Hi:
                if hi < 0:
                    raise HiValueIsNotValidException("Hi must be >= 0")
        return True

    @staticmethod
    def build_from_parameters(n, l, g, p, etha=None, etha_zone=None, angles=None, Gi=None, Hi=None):
        """
        to build a city graph with parameters information
        :param etha_zone:
        :param etha:
        :param angles:
        :param Hi:
        :param Gi:
        :param n:
        :param l:
        :param g:
        :param p:
        :return:
        """

        graph_obj = Graph()

        # if parameters are valid
        if graph_obj.parameters_validator(n, l, g, p, etha, etha_zone, angles, Gi, Hi):
            # ADD CBD
            # ADD Zones
            # # for each zones add Nodes periphery and subcenter
            # ADD all edges
            # add CBD
            cbd_node_obj = CBD(0, 0, 0, 0, 0, p, 0, "CBD")
            graph_obj.__add_cbd(cbd_node_obj)

            # Add zones
            for zone in range(n):
                periphery_node_id = 2 * zone + 1
                subcenter_node_id = 2 * zone + 2
                periphery_radius = l + g * l
                subcenter_radius = l
                periphery_angle = 360 / n * zone
                subcenter_angle = 360 / n * zone
                x_p, y_p = graph_obj.get_xy(periphery_radius, periphery_angle)
                x_sc, y_sc = graph_obj.get_xy(subcenter_radius, subcenter_angle)

                periphery_node_name = "P_{}".format(zone + 1)
                periphery_node_obj = Periphery(periphery_node_id, x_p, y_p, periphery_radius, periphery_angle, p,
                                               zone + 1, periphery_node_name)
                subcenter_node_name = "SC_{}".format(zone + 1)
                subcenter_node_obj = Subcenter(subcenter_node_id, x_sc, y_sc, subcenter_radius, subcenter_angle, p,
                                               zone + 1, subcenter_node_name)

                # add periphery and subcenter nodes to graph obj
                graph_obj.__add_zone(periphery_node_obj, subcenter_node_obj, zone + 1)

            # add asymmetry by angles
            if angles is not None:
                graph_obj.__angles_asymmetry(angles)
            # add asymmetry by Gi
            if Gi is not None:
                graph_obj.__Gi_asymmetry(Gi)
            # add asymmetry by Hi
            if Hi is not None:
                graph_obj.__Hi_asymmetry(Hi)
            # add asymmetry by etha
            if etha is not None and etha_zone is not None:
                graph_obj.__etha_asymmetry(etha, etha_zone)

        graph_obj.__n = n
        graph_obj.__l = l
        graph_obj.__g = g
        graph_obj.__p = p
        graph_obj.__etha = etha
        graph_obj.__etha_zone = etha_zone
        graph_obj.__angles = angles
        graph_obj.__Gi = Gi
        graph_obj.__Hi = Hi

        return graph_obj

    @staticmethod
    def __pajekfile_to_dataframe(file_path):

        # read pajek file as a Dataframe
        df_file = pd.DataFrame()
        col_id = []
        col_name = []
        col_x = []
        col_y = []
        col_type = []
        col_zone = []
        col_width = []

        with open(file_path, mode='r', encoding='utf-8') as f_obj:
            n_nodes = 0
            for line in f_obj.readlines():
                if line.lower().startswith("*vertices"):
                    _, n_nodes = line.split()
                    n_nodes = int(n_nodes)
                    continue
                if n_nodes > 0:
                    if len(line.split()) == 7:
                        node_id, name, x, y, node_type, zone, width = line.split()
                        if node_type != "CBD" and node_type != "SC" and node_type != "P":
                            raise NodeTypeIsNotValidException("Node type is not valid. Try with CBD, SC or P")
                        col_id.append(node_id)
                        col_name.append(name)
                        col_x.append(x)
                        col_y.append(y)
                        col_type.append(node_type)
                        col_zone.append(zone)
                        col_width.append(width)

                        n_nodes = n_nodes - 1
                    else:
                        raise PajekFormatIsNotValidException("each node line must provide information about [id] ["
                                                             "name] [x] [y] [type] [zone] [width]")

            df_file["node_id"] = col_id
            df_file["name"] = col_name
            df_file["x"] = col_x
            df_file["y"] = col_y
            df_file["type"] = col_type
            df_file["zone"] = col_zone
            df_file["width"] = col_width

            return df_file

    @staticmethod
    def get_angle(x, y):
        """
        to get angle of a vector with coor (0,0,x,y)  with respect to x+
        :param x:
        :param y:
        :return:
        """
        a = 1
        b = 0
        c = x
        d = y

        if x == 0 and y == 0:
            return 0

        dot_product = a * c + b * d
        # for three dimensional simply add dotProduct = a*c + b*d  + e*f
        mod_of_vector1 = math.sqrt(a * a + b * b) * math.sqrt(c * c + d * d)
        # for three dimensional simply add modOfVector = math.sqrt( a*a + b*b + e*e)*math.sqrt(c*c + d*d +f*f)
        angle = dot_product / mod_of_vector1
        # print("Cosθ =",angle)
        angle_in_degree = math.degrees(math.acos(angle))
        if y < 0:
            if x >= 0:
                angle_in_degree = 360 - angle_in_degree
            if x < 0:
                angle_in_degree = (180 - angle_in_degree) + 180
        return angle_in_degree

    @staticmethod
    def get_xy(radius, angle):
        """
        to get x, y with radius and angle parameters
        :param radius:
        :param angle:
        :return:
        """
        x, y = radius * math.cos(math.radians(angle)), radius * math.sin(math.radians(angle))
        return x, y

    @staticmethod
    def build_from_file(file_path, file_format=GraphFileFormat.PAJEK):
        """
        to build a city graph with pajek file information
        :param file_path:
        :param file_format:
        :return: Graph instance
        """
        graph_obj = Graph()

        if file_format == GraphFileFormat.PAJEK:

            df_file = graph_obj.__pajekfile_to_dataframe(file_path)

            df_file = df_file.sort_values(["zone", "type"], ascending=[True, True])

            lines_accepted = list(range(1, 10001, 2))

            if not len(df_file["node_id"]) in lines_accepted:
                raise LineNumberInFileIsNotValidException("The number of lines in the file must be 2n+1 or "
                                                          "file is very big (until 5000 zones accepted)")

            n = int((len(df_file["node_id"]) - 1) / 2)

            cbd = []
            periphery = []
            subcenter = []

            width = 0

            # build nodes list
            for i in range(len(df_file["node_id"])):
                node_id = df_file.iloc[i]["node_id"]
                name = df_file.iloc[i]["name"]
                x = float(df_file.iloc[i]["x"])
                y = float(df_file.iloc[i]["y"])
                node_type = df_file.iloc[i]["type"]
                zone = int(df_file.iloc[i]["zone"])
                width = float(df_file.iloc[i]["width"])

                radius = math.sqrt(x ** 2 + y ** 2)
                angle = graph_obj.get_angle(x, y)

                if node_type == "CBD":
                    cbd.append(CBD(node_id, x, y, radius, angle, width, zone, name))
                if node_type == "P":
                    periphery.append(Periphery(node_id, x, y, radius, angle, width, zone, name))
                if node_type == "SC":
                    subcenter.append(Subcenter(node_id, x, y, radius, angle, width, zone, name))

            r_sc = []
            r_p = []
            ang_sc = []
            r_cbd = 0
            ang_cbd = 0

            if len(cbd) == 1:
                r_cbd = cbd[0].radius
                ang_cbd = cbd[0].angle

            etha = None
            etha_zone = None

            # verification of existence and uniqueness of SC and P by zone
            # save information to build parameters
            for zone in range(n):
                zone_id = zone + 1
                n_p = 0
                n_sc = 0
                node_periphery = None
                node_subcenter = None

                for p in periphery:
                    if p.zone_id == zone_id:
                        n_p = n_p + 1
                        node_periphery = p
                for sc in subcenter:
                    if sc.zone_id == zone_id:
                        n_sc = n_sc + 1
                        node_subcenter = sc
                if n_p != 1 or n_sc != 1:
                    raise PeripherySubcenterNumberForZoneException("try to verify that each zone [1, ..., n] has "
                                                                   "one sc and p")

                radius_p = node_periphery.radius
                radius_sc = node_subcenter.radius
                angle_sc = node_subcenter.angle

                r_sc.append(radius_sc)
                r_p.append(radius_p)
                ang_sc.append(angle_sc)

                # Update etha and etha_zone
                if ang_cbd - 0.001 <= angle_sc <= ang_cbd + 0.001:
                    etha_zone = zone_id
                    etha = r_cbd / radius_sc

            L = 0
            g = 0
            if len(r_sc) != 0 and len(r_p) != 0:
                L = sum(r_sc) / len(r_sc)
                g = (sum(r_p) / len(r_p) - L) / L

            Gi = []
            Hi = []
            for i in range(n):
                Gi.append(r_sc[i] / L)
                Hi.append(r_p[i] / (L + g * L))

            angles = ang_sc

            # if parameters are valid
            if graph_obj.parameters_validator(n, L, g, width, etha, etha_zone, angles, Gi, Hi):

                for node in cbd:
                    graph_obj.__add_cbd(node)

                for i in range(n):
                    node_periphery = None
                    node_subcenter = None
                    for p in periphery:
                        if p.zone_id == i + 1:
                            node_periphery = p
                            break
                    for sc in subcenter:
                        if sc.zone_id == i + 1:
                            node_subcenter = sc
                            break
                    graph_obj.__add_zone(node_periphery, node_subcenter)

        else:
            raise FileFormatIsNotValidException("File don't have a valid format. Try with Pajek format")

        graph_obj.__n = n
        graph_obj.__l = L
        graph_obj.__g = g
        graph_obj.__p = width
        graph_obj.__etha = etha
        graph_obj.__etha_zone = etha_zone
        graph_obj.__angles = angles
        graph_obj.__Gi = Gi
        graph_obj.__Hi = Hi

        return graph_obj

    def __add_cbd(self, cbd_node):
        # not need to check because CBD is the first node append in __nodes
        # if CBD_node.id in self.__nodes_id:
        #   raise IdEdgeIsDuplicatedException("node id is duplicated")
        # not need to check because n° of lines in pajek file and n° of SC = n° of P = 1 for each zone have exceptions
        # if self.__CBD_exist:
        #    raise CBDDuplicatedException('a CBD already exists')
        self.__cbd_exist = True
        self.__nodes_id.append(cbd_node.id)
        self.__nodes.append(cbd_node)

    def __add_zone(self, node_periphery, node_subcenter, zone_id=None):
        # zones can only be added if CBD is included
        if len(self.__nodes) == 0:
            raise CBDDoesNotExistException("Need add CBD node previously")
        # always add last zone
        if zone_id is None:
            zone_id = len(self.__zones) + 1
        # not need to check because number of periphery and subcenter control exceptions
        # if zone_id != len(self.__zones) + 1:
        #    raise AddPreviousZonesExceptions("need to specify zone {} previously".format(len(self.__zones) + 1))
        self.__zones.append(Zone(zone_id, node_periphery, node_subcenter))
        self.__add_nodes(node_periphery, node_subcenter)

        # must build all the edges
        self.__build_edges()

    def __add_nodes(self, node_periphery, node_subcenter):
        # not need to check because number of periphery and subcenter control exceptions
        # if not isinstance(node_periphery, Periphery):
        #    raise PeripheryTypeIsNotValidException('node_periphery is not a valid periphery node')
        # if not isinstance(node_subcenter, Subcenter):
        #    raise SubcenterTypeIsNotValidException('node_subcenter is not a valid subcenter node')

        # to verified if id is not duplicated
        if node_periphery.id in self.__nodes_id or node_subcenter.id in self.__nodes_id:
            raise NodeIdDuplicatedException('id_node is duplicated')

        self.__nodes.append(node_periphery)
        self.__nodes.append(node_subcenter)
        self.__nodes_id.append(node_periphery.id)
        self.__nodes_id.append(node_subcenter.id)

    def __build_edges(self):
        self.__edges = []
        self.__edges_id = []
        if len(self.__zones) == 1:
            # p <-> sc
            # sc <-> cbd
            p = self.__zones[0].periphery
            sc = self.__zones[0].subcenter
            cbd = self.__nodes[0]
            self.__add_edge(Edge(len(self.__edges) + 1, p, sc))
            self.__add_edge(Edge(len(self.__edges) + 1, sc, p))
            self.__add_edge(Edge(len(self.__edges) + 1, sc, cbd))
            self.__add_edge(Edge(len(self.__edges) + 1, cbd, sc))
        if len(self.__zones) == 2:
            # p <-> sc
            # sc <-> cbd
            p1 = self.__zones[0].periphery
            sc1 = self.__zones[0].subcenter
            p2 = self.__zones[1].periphery
            sc2 = self.__zones[1].subcenter
            cbd = self.__nodes[0]
            self.__add_edge(Edge(len(self.__edges) + 1, p1, sc1))
            self.__add_edge(Edge(len(self.__edges) + 1, sc1, p1))
            self.__add_edge(Edge(len(self.__edges) + 1, sc1, cbd))
            self.__add_edge(Edge(len(self.__edges) + 1, cbd, sc1))
            self.__add_edge(Edge(len(self.__edges) + 1, sc1, sc2))
            self.__add_edge(Edge(len(self.__edges) + 1, sc2, sc1))
            self.__add_edge(Edge(len(self.__edges) + 1, p2, sc2))
            self.__add_edge(Edge(len(self.__edges) + 1, sc2, p2))
            self.__add_edge(Edge(len(self.__edges) + 1, sc2, cbd))
            self.__add_edge(Edge(len(self.__edges) + 1, cbd, sc2))

        if len(self.__zones) > 2:
            for i in range(len(self.__zones)):
                p = self.__zones[i].periphery
                sc = self.__zones[i].subcenter
                cbd = self.__nodes[0]
                j = i + 1
                if i == len(self.__zones) - 1:
                    j = 0
                sc2 = self.__zones[j].subcenter
                # p <-> sc
                # sc <-> cbd
                # sc <-> sc2
                self.__add_edge(Edge(len(self.__edges) + 1, p, sc))
                self.__add_edge(Edge(len(self.__edges) + 1, sc, p))
                self.__add_edge(Edge(len(self.__edges) + 1, sc, cbd))
                self.__add_edge(Edge(len(self.__edges) + 1, cbd, sc))
                self.__add_edge(Edge(len(self.__edges) + 1, sc, sc2))
                self.__add_edge(Edge(len(self.__edges) + 1, sc2, sc))

    def __add_edge(self, edge):
        # no need to check
        # if not isinstance(edge, Edge):
        #    raise EdgeDoesNotExistException('is not a valid edge')
        # if edge.id in self.__edges_id:
        #    raise IdEdgeIsDuplicatedException('id edge is duplicated')
        self.__edges.append(edge)
        self.__edges_id.append(edge.id)

    def __etha_asymmetry(self, etha, etha_zone):

        zone = self.__zones[etha_zone - 1]
        sc = zone.subcenter
        r_cbd = etha * sc.radius
        ang = sc.angle

        x_cbd, y_cbd = self.get_xy(r_cbd, ang)

        for node in range(len(self.__nodes)):
            if isinstance(self.__nodes[node], CBD):
                self.__nodes[node].x = x_cbd
                self.__nodes[node].y = y_cbd
                self.__nodes[node].radius = r_cbd
                self.__nodes[node].angle = ang

        # must build all the edges
        self.__build_edges()

    def __Hi_asymmetry(self, Hi):

        for i in range(len(self.__zones)):
            hi = Hi[i]
            p = self.__zones[i].periphery

            r_p = hi * p.radius
            ang = p.angle
            x_p, y_p = self.get_xy(r_p, ang)

            # change values in nodes list
            for node in range(len(self.__nodes)):

                if self.__nodes[node] == p:
                    self.__nodes[node].x = x_p
                    self.__nodes[node].y = y_p
                    self.__nodes[node].radius = r_p

            # change values in zones nodes information
            self.__zones[i].periphery.x = x_p
            self.__zones[i].periphery.y = y_p
            self.__zones[i].periphery.radius = r_p

        # must build all the edges
        self.__build_edges()

    def __Gi_asymmetry(self, Gi):

        for i in range(len(self.__zones)):
            gi = Gi[i]
            sc = self.__zones[i].subcenter

            r_sc = gi * sc.radius
            ang = sc.angle
            x_sc, y_sc = self.get_xy(r_sc, ang)

            # change values in nodes list
            for node in range(len(self.__nodes)):

                if self.__nodes[node] == sc:
                    self.__nodes[node].x = x_sc
                    self.__nodes[node].y = y_sc
                    self.__nodes[node].radius = r_sc

            # change values in zones nodes information
            self.__zones[i].subcenter.x = x_sc
            self.__zones[i].subcenter.y = y_sc
            self.__zones[i].subcenter.radius = r_sc

        # must build all the edges
        self.__build_edges()

    def __angles_asymmetry(self, angles):

        for i in range(len(self.__zones)):
            ang = angles[i]

            p = self.__zones[i].periphery
            sc = self.__zones[i].subcenter

            r_p = p.radius
            r_sc = sc.radius
            x_p, y_p = self.get_xy(r_p, ang)
            x_sc, y_sc = self.get_xy(r_sc, ang)

            # change values in nodes list
            for node in range(len(self.__nodes)):
                if self.__nodes[node] == p:
                    self.__nodes[node].x = x_p
                    self.__nodes[node].y = y_p
                    self.__nodes[node].angle = ang
                if self.__nodes[node] == sc:
                    self.__nodes[node].x = x_sc
                    self.__nodes[node].y = y_sc
                    self.__nodes[node].angle = ang

            # change values in zones nodes information
            self.__zones[i].periphery.x = x_p
            self.__zones[i].periphery.y = y_p
            self.__zones[i].periphery.angle = ang

            self.__zones[i].subcenter.x = x_sc
            self.__zones[i].subcenter.y = y_sc
            self.__zones[i].subcenter.angle = ang

        # must build all the edges
        self.__build_edges()

    def get_cbd(self):
        """
        to obtain CBD node
        :return:
        """
        cbd = None
        for node in self.__nodes:
            if isinstance(node, CBD):
                cbd = node
                break
        return cbd

    def get_n(self):
        """
        to get parameters of numbers of zones
        :return:
        """
        return self.__n

    def get_zones(self):
        """
        to get all the zones built
        :return:
        """
        return self.__zones

    def get_nodes(self):
        """
        to get all the nodes built
        :return:
        """
        return self.__nodes

    def get_edges(self):
        """
        to get all the edges built
        :return:
        """
        return self.__edges

    def plot(self, file_path):
        """
        to plot graph
        :return:
        """

        # edges information and positions
        edges = []
        position = defaultdict(list)
        for edge in self.__edges:
            edges.append((edge.node1.id, edge.node2.id))
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

        for node in self.__nodes:
            if isinstance(node, CBD):
                info_cbd.append(node)
            if isinstance(node, Periphery):
                info_p.append(node)
            if isinstance(node, Subcenter):
                info_sc.append(node)
        id_cbd = []
        id_sc = []
        id_p = []
        x_cbd = []
        y_cbd = []
        x_sc = []
        y_sc = []
        x_p = []
        y_p = []

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

        G = nx.DiGraph()
        G.add_edges_from(edges)

        # separate calls to draw labels, nodes and edges
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_p, node_color='red', node_size=300)
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_sc, node_color='blue', node_size=300)
        nx.draw_networkx_nodes(G, position, cmap=plt.get_cmap('Set2'), nodelist=id_cbd, node_color='purple',
                               node_size=300)
        nx.draw_networkx_labels(G, position)
        nx.draw_networkx_edges(G, position, edgelist=edges, edge_color='orange', arrows=True)

        plt.title("City graph")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().set_aspect('equal')
        plt.savefig(file_path)
