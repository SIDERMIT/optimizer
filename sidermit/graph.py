from enum import Enum
import pandas as pd
import math
from sidermit.exceptions import *


class GraphFileFormat(Enum):
    # [node number] [node name] [x] [y] [type] [zone]
    PAJEK = 1


class Zone:

    def __init__(self, zone_id, node_periphery, node_subcenter):

        if not isinstance(node_periphery, Periphery):
            raise NodePeripheryTypeIsNotValidException('node must be periphery')

        if not isinstance(node_subcenter, Subcenter):
            raise NodeSubcenterTypeIsNotValidException('node must be subcenter')

        self.id = zone_id
        self.periphery = node_periphery
        self.subcenter = node_subcenter


class Node:

    def __init__(self, node_id, x, y, radius, angle, width, name=None):
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


class CBD(Node):

    def __init__(self, node_id, x, y, radius, angle, width, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, name)


class Periphery(Node):

    def __init__(self, node_id, x, y, radius, angle, width, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, name)


class Subcenter(Node):

    def __init__(self, node_id, x, y, radius, angle, width, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, name)


class Edge:

    def __init__(self, edge_id, node1, node2):
        if isinstance(node1, Periphery) and isinstance(node2, Periphery):
            raise EdgeNotAvailable("edge between periphery nodes is not available")
        if isinstance(node1, Periphery) and isinstance(node2, CBD):
            raise EdgeNotAvailable("edge between periphery  and CBD is not available")
        if isinstance(node1, CBD) and isinstance(node2, Periphery):
            raise EdgeNotAvailable("edge between periphery  and CBD is not available")
        self.id = edge_id
        self.node1 = node1
        self.node2 = node2


class Graph:

    def __init__(self):
        self.zones = []
        self.nodes = []
        self.edges = []

    def add_zone(self, node_periphery, node_subcenter, zone_id=None):
        # zones can only be added if CBD is included
        if len(self.nodes) == 0:
            raise CBDDoesNotExistExceptions("Need add CBD node previously")
        # always add last zone
        if zone_id is None:
            zone_id = len(self.zones) + 1
        if zone_id is not None:
            if zone_id < 1:
                raise ZoneIdIsNotValidExceptions("zone_id number must be >=1")
            if zone_id != len(self.zones) + 1:
                raise AddPreviousZonesExceptions("need to specify zone {} previously".format(len(self.zones) + 1))
        # need periphery and subcenter nodes
        if not isinstance(node_periphery, Periphery):
            raise PeripheryTypeIsNotValidException('node_periphery is not a valid periphery node')
        if not isinstance(node_subcenter, Subcenter):
            raise SubcenterTypeIsNotValidException('node_subcenter is not a valid subcenter node')

        self.zones.append(Zone(zone_id, node_periphery, node_subcenter))
        self.__add_nodes(node_periphery, node_subcenter)

        # must build all the edges
        self.__build_edges()

    def __add_cbd(self, CBD_node):
        if not isinstance(CBD_node, CBD):
            raise CBDTypeIsNotValidException('CBD_node is not a valid CBD node')
        for node in self.nodes:
            if isinstance(node, CBD):
                raise CBDDuplicatedException('a CBD already exists')

    def __add_nodes(self, node_periphery, node_subcenter):
        if not isinstance(node_periphery, Periphery):
            raise PeripheryTypeIsNotValidException('node_periphery is not a valid periphery node')
        if not isinstance(node_subcenter, Node):
            raise SubcenterTypeIsNotValidException('node_subcenter is not a valid subcenter node')

        # to verified if id is not duplicated
        for nodes in self.nodes:
            if nodes.id == node_periphery.id:
                raise IdNodeIsDuplicatedException('id_node is duplicated')
            if nodes.id == node_subcenter.id:
                raise IdNodeIsDuplicatedException('id_node is duplicated')

        self.nodes.append(node_periphery)
        self.nodes.append(node_subcenter)

    def __build_edges(self):
        self.edges = []
        if len(self.zones) == 1:
            # p <-> sc
            # sc <-> cbd
            p = self.zones[0].periphery
            sc = self.zones[0].subcenter
            cbd = self.nodes[0]
            self.add_edge(Edge(len(self.edges) + 1, p, sc))
            self.add_edge(Edge(len(self.edges) + 1, sc, p))
            self.add_edge(Edge(len(self.edges) + 1, sc, cbd))
            self.add_edge(Edge(len(self.edges) + 1, cbd, sc))
        if len(self.zones) > 1:
            for i in range(len(self.zones)):
                p = self.zones[i].periphery
                sc = self.zones[i].subcenter
                cbd = self.nodes[0]
                j = i + 1
                if i == len(self.zones) - 1:
                    j = 0
                sc2 = self.zones[j].subcenter
                # p <-> sc
                # sc <-> cbd
                # sc <-> sc2
                self.__add_edge(Edge(len(self.edges) + 1, p, sc))
                self.__add_edge(Edge(len(self.edges) + 1, sc, p))
                self.__add_edge(Edge(len(self.edges) + 1, sc, cbd))
                self.__add_edge(Edge(len(self.edges) + 1, cbd, sc))
                self.__add_edge(Edge(len(self.edges) + 1, sc, sc2))
                self.__add_edge(Edge(len(self.edges) + 1, sc2, sc))

    def __add_edge(self, edge):
        if not isinstance(edge, Edge):
            raise EdgeDoesNotExistException('is not a valid edge')
        for edges in self.edges:
            if edge.id == edges.id:
                raise IdEdgeIsDuplicatedException('id edge is duplicated')
        self.edges.append(edge)

    @staticmethod
    def build_from_parameters(n, l, g, p, etha = None, etha_zone = None, angles = None, Gi = None, Hi =None):
        """
        create symetric
        :param n:
        :param l:
        :param g:
        :param p:
        :return:
        """
        if n is None:
            raise NIsNotDefined('must specify value for n')
        if n is not None:
            if n < 0:
                raise NIsNotValidNumberException('n cannot be a negative number')
        if l is None:
            raise LIsNotDefined('must specify value for L')
        if l is not None:
            if l < 0:
                raise LIsNotValidNumberException('L cannot be a negative number')
        if g is None:
            raise GIsNotDefined('must specify value for g')
        if g is not None:
            if g < 0:
                raise GIsNotValidNumberException('G cannot be a negative number')
        if p is None:
            raise PIsNotDefined('must specify value for p')
        if p is not None:
            if p < 0:
                raise PIsNotValidNumberException('n cannot be a negative number')

        graph_obj = Graph()
        # build nodes and edges
        # build nodes
        # ADD CBD

        CBD_node = CBD(0, 0, 0, 0, 0, p)
        graph_obj.__add_cbd(CBD_node)
        # for each zone add P and SC nodes
        for zone in range(n):
            id_p = 2 * zone + 1
            id_sc = 2 * zone + 2
            radius_p = l + g * l
            radius_sc = l
            angle_p = 360 / n * zone
            angle_sc = 360 / n * zone
            x_p, y_p = radius_p * math.cos(math.radians(angle_p)), radius_p * math.sin(math.radians(angle_p))
            x_sc, y_sc = radius_sc * math.cos(math.radians(angle_sc)), radius_sc * math.sin(math.radians(angle_sc))

            node_p = Node(id_p, x_p, y_p, radius_p, angle_p, p)
            node_sc = Node(id_sc, x_sc, y_sc, radius_sc, angle_sc, p)

            graph_obj.add_zone(node_p, node_sc, n + 1)

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

        with open(file_path, mode='r', encoding='utf-8') as f_obj:
            nnodes = 0
            for line in f_obj.readlines():
                if line.lower().startswith("*vertices"):
                    _, nnodes = line.split()
                    continue
                if nnodes > 0:
                    try:
                        id, name, x, y, type, zone = line.split()
                        if type != "CBD" or type != "SC" or type != "P":
                            raise NodeTypeIsNotValidExceptions("Node type is not valid. Try with CBD, SC or P")
                        if int(zone) < 0:
                            raise ZoneIdIsNotValidExceptions("zone is not valid. Try with a positive value")
                        col_id.append(id)
                        col_name.append(name)
                        col_x.append(x)
                        col_y.append(y)
                        col_type.append(type)
                        col_zone.append(zone)

                        nnodes = nnodes - 1
                    except:
                        raise PajekFormatIsNotValidExceptions(
                            "each node line must provide information about [id] [name] [x] [y] [type] [zone]")

            df_file["node_id"] = col_id
            df_file["name"] = col_name
            df_file["x"] = x
            df_file["y"] = y
            df_file["type"] = type
            df_file["zone"] = zone

            return df_file

    @staticmethod
    def build_from_file(file_path, file_format=GraphFileFormat.PAJEK):
        """
        :param file_path:
        :param file_format:
        :return: Graph instance
        """
        graph_obj = Graph()

        if file_format == GraphFileFormat.PAYEK:

            df_file = graph_obj.__pajekfile_to_dataframe(file_path)

            df_file = df_file.sort_values(["zone", "type"], ascending=[True, True])

            n = (len(df_file["node_id"]) - 1) / 2

            for n in range(n + 1)



        else:
            raise FileFormatIsNotValidExceptions("File don't have a valid format. Try with Pajek format")

        return graph_obj
