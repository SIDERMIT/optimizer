from enum import Enum
import pandas as pd
from sidermit.exceptions import *
import math


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

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name=None):
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

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Periphery(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Subcenter(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name=None):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


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

    @staticmethod
    def parameters_validator(n, l, g, p, etha=None, etha_zone=None, angles=None, Gi=None, Hi=None):
        if n is None:
            raise NIsNotDefined('must specify value for n')
        if n < 0 or not isinstance(n, int):
            raise NIsNotValidNumberException('n cannot be a negative number')
        if l is None:
            raise LIsNotDefined('must specify value for L')
        if l < 0:
            raise LIsNotValidNumberException('L cannot be a negative number')
        if g is None:
            raise GIsNotDefined('must specify value for g')
        if g < 0:
            raise GIsNotValidNumberException('G cannot be a negative number')
        if p is None:
            raise PIsNotDefined('must specify value for p')
        if p < 0:
            raise PIsNotValidNumberException('n cannot be a negative number')
        if etha is None and etha_zone is not None:
            raise EthaValueRequiredExceptions("must give value for etha")
        if etha is not None and etha_zone is None:
            raise EthaZoneValueRequiredExceptions("must give value for etha zone")
        if etha is not None and etha_zone is not None:
            if etha < 0 or etha > 1:
                raise EthaValueIsNotValidExceptions("etha value is not valid. Try with value belong in [0-1]")
            if etha_zone <= 0 or etha_zone > n or not isinstance(etha_zone, int):
                raise EthaZoneValueIsNotValidExceptions("etha zone is not valid. Try with value belong in [1,...,n]")
        if angles is not None:
            if len(angles) != n:
                raise LenAnglesIsNotValidExceptions("must give angle value for all zones")
            for angle in angles:
                if angle < 0 or angle > 360:
                    raise AngleValueIsNotValidEceptions("angle must belong in [0°-360°]")
        if Gi is not None:
            if len(Gi) != n:
                raise LenGiIsNotValidExceptions("must give Gi value for all zones")
            for gi in Gi:
                if gi < 0:
                    raise GiValueIsNotValidEceptions("Gi must be >= 0")
        if Hi is not None:
            if len(Hi) != n:
                raise LenHiIsNotValidExceptions("must give Hi value for all zones")
            for hi in Hi:
                if hi < 0:
                    raise HiValueIsNotValidEceptions("Hi must be >= 0")
        return True

    @staticmethod
    def build_from_parameters(n, l, g, p, etha=None, etha_zone=None, angles=None, Gi=None, Hi=None):
        """
        create symetric
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
            CBD_node = CBD(0, 0, 0, 0, 0, p, 0)
            graph_obj.__add_cbd(CBD_node)

            # Add zones
            for zone in range(n):
                id_p = 2 * zone + 1
                id_sc = 2 * zone + 2
                radius_p = l + g * l
                radius_sc = l
                angle_p = 360 / n * zone
                angle_sc = 360 / n * zone
                x_p, y_p = radius_p * math.cos(math.radians(angle_p)), radius_p * math.sin(math.radians(angle_p))
                x_sc, y_sc = radius_sc * math.cos(math.radians(angle_sc)), radius_sc * math.sin(math.radians(angle_sc))

                node_p = Periphery(id_p, x_p, y_p, radius_p, angle_p, p, zone + 1)
                node_sc = Subcenter(id_sc, x_sc, y_sc, radius_sc, angle_sc, p, zone + 1)

                # add periphery and subcenter nodes
                # build edges
                graph_obj.add_zone(node_p, node_sc, zone + 1)

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

        return graph_obj

    def __add_cbd(self, CBD_node):
        if not isinstance(CBD_node, CBD):
            raise CBDTypeIsNotValidException('CBD_node is not a valid CBD node')
        for node in self.nodes:
            if isinstance(node, CBD):
                raise CBDDuplicatedException('a CBD already exists')

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
        # zone_id of the nodes must be equal to zone_id og the zone
        if node_subcenter.id != len(self.zones) + 1 or node_periphery.id != len(self.zones) + 1:
            raise ZoneIdIsNotValidExceptions("nodes dont have zone_id equal to zone")

        self.zones.append(Zone(zone_id, node_periphery, node_subcenter))
        self.__add_nodes(node_periphery, node_subcenter)

        # must build all the edges
        self.__build_edges()

    def __add_nodes(self, node_periphery, node_subcenter):
        if not isinstance(node_periphery, Periphery):
            raise PeripheryTypeIsNotValidException('node_periphery is not a valid periphery node')
        if not isinstance(node_subcenter, Subcenter):
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
            self.__add_edge(Edge(len(self.edges) + 1, p, sc))
            self.__add_edge(Edge(len(self.edges) + 1, sc, p))
            self.__add_edge(Edge(len(self.edges) + 1, sc, cbd))
            self.__add_edge(Edge(len(self.edges) + 1, cbd, sc))
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

    def __etha_asymmetry(self, etha, etha_zone):

        zone = self.zones[etha_zone - 1]
        sc = zone.subcenter
        r_cbd = etha * sc.radius
        ang = sc.angle

        x_cbd, y_cbd = r_cbd * math.cos(math.radians(ang)), r_cbd * math.sin(math.radians(ang))

        for node in range(len(self.nodes)):
            if isinstance(self.nodes[node], CBD):
                self.nodes[node].x = x_cbd
                self.nodes[node].y = y_cbd
                self.nodes[node].radius = r_cbd
                self.nodes[node].angle = ang

        # must build all the edges
        self.__build_edges()

    def __Hi_asymmetry(self, Hi):

        for i in range(len(self.zones)):
            hi = Hi[i]
            p = self.zones[i].periphery

            r_p = hi * p.radius
            ang = p.angle
            x_p, y_p = r_p * math.cos(math.radians(ang)), r_p * math.sin(math.radians(ang))

            # change values in nodes list
            for node in range(len(self.nodes)):

                if self.nodes[node] == p:
                    self.nodes[node].x = x_p
                    self.nodes[node].y = y_p
                    self.nodes[node].radius = r_p

            # change values in zones nodes information
            self.zones[i].periphery.x = x_p
            self.zones[i].periphery.y = y_p
            self.zones[i].periphery.radius = r_p

        # must build all the edges
        self.__build_edges()

    def __Gi_asymmetry(self, Gi):

        for i in range(len(self.zones)):
            gi = Gi[i]
            sc = self.zones[i].subcenter

            r_sc = gi * sc.radius
            ang = sc.angle
            x_sc, y_sc = r_sc * math.cos(math.radians(ang)), r_sc * math.sin(math.radians(ang))

            # change values in nodes list
            for node in range(len(self.nodes)):

                if self.nodes[node] == sc:
                    self.nodes[node].x = x_sc
                    self.nodes[node].y = y_sc
                    self.nodes[node].radius = r_sc

            # change values in zones nodes information
            self.zones[i].subcenter.x = x_sc
            self.zones[i].subcenter.y = y_sc
            self.zones[i].subcenter.radius = r_sc

        # must build all the edges
        self.__build_edges()

    def __angles_asymmetry(self, angles):

        for i in range(len(self.zones)):
            ang = angles[i]

            p = self.zones[i].periphery
            sc = self.zones[i].subcenter

            r_p = p.radius
            r_sc = sc.radius
            x_p, y_p = r_p * math.cos(math.radians(ang)), r_p * math.sin(math.radians(ang))
            x_sc, y_sc = r_sc * math.cos(math.radians(ang)), r_sc * math.sin(math.radians(ang))

            # change values in nodes list
            for node in range(len(self.nodes)):
                if self.nodes[node] == p:
                    self.nodes[node].x = x_p
                    self.nodes[node].y = y_p
                    self.nodes[node].angle = ang
                if self.nodes[node] == sc:
                    self.nodes[node].x = x_sc
                    self.nodes[node].y = y_sc
                    self.nodes[node].angle = ang

            # change values in zones nodes information
            self.zones[i].periphery.x = x_p
            self.zones[i].periphery.y = y_p
            self.zones[i].periphery.angle = ang

            self.zones[i].subcenter.x = x_sc
            self.zones[i].subcenter.y = y_sc
            self.zones[i].subcenter.angle = ang

        # must build all the edges
        self.__build_edges()

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
                        node_id, name, x, y, node_type, zone = line.split()
                        if node_type != "CBD" or node_type != "SC" or node_type != "P":
                            raise NodeTypeIsNotValidExceptions("Node type is not valid. Try with CBD, SC or P")
                        if int(zone) < 0:
                            raise ZoneIdIsNotValidExceptions("zone is not valid. Try with a positive value")
                        col_id.append(node_id)
                        col_name.append(name)
                        col_x.append(x)
                        col_y.append(y)
                        col_type.append(node_type)
                        col_zone.append(zone)

                        nnodes = nnodes - 1
                    except PajekFormatIsNotValidExceptions:
                        raise PajekFormatIsNotValidExceptions("each node line must provide information about [id] ["
                                                              "name] [x] [y] [type] [zone]")

            df_file["node_id"] = col_id
            df_file["name"] = col_name
            df_file["x"] = col_x
            df_file["y"] = col_y
            df_file["type"] = col_type
            df_file["zone"] = col_zone

            return df_file

    @staticmethod
    def obtain_angle(x, y):
        a = 1
        b = 0
        c = x
        d = y
        dotProduct = a * c + b * d
        # for three dimensional simply add dotProduct = a*c + b*d  + e*f
        modOfVector1 = math.sqrt(a * a + b * b) * math.sqrt(c * c + d * d)
        # for three dimensional simply add modOfVector = math.sqrt( a*a + b*b + e*e)*math.sqrt(c*c + d*d +f*f)
        angle = dotProduct / modOfVector1
        # print("Cosθ =",angle)
        angleInDegree = math.degrees(math.acos(angle))
        if y < 0:
            if x >= 0:
                angleInDegree = 360 - angleInDegree
            if x < 0:
                angleInDegree = (180 - angleInDegree) + 180
        return angleInDegree

    @staticmethod
    def build_from_filef(p, file_path, file_format=GraphFileFormat.PAJEK):
        """
        :param p:
        :param file_path:
        :param file_format:
        :return: Graph instance
        """
        graph_obj = Graph()

        if file_format == GraphFileFormat.PAYEK:

            df_file = graph_obj.__pajekfile_to_dataframe(file_path)

            df_file = df_file.sort_values(["zone", "type"], ascending=[True, True])

            n = (len(df_file["node_id"]) - 1) / 2

            if not isinstance(n, int):
                raise NumberLinesInTheFileIsNotValidExceptions("The number of lines in the file must be 2n+1")

            cbd = []
            periphery = []
            subcenter = []

            # build nodes list
            for i in range(len(df_file["node_id"])):
                node_id = df_file.iloc[i]["node_id"]
                name = df_file.iloc[i]["name"]
                x = df_file.iloc[i]["x"]
                y = df_file.iloc[i]["y"]
                node_type = df_file.iloc[i]["type"]
                zone = df_file.iloc[i]["zone"]

                radius = math.sqrt(x ** 2 + y ** 2)
                width = p
                angle = graph_obj.obtain_angle(x, y)

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

            # verification of existence and uniqueness of CBD
            if len(cbd) == 0:
                raise CBDDoesNotExistExceptions("a CBD is required")
            if len(cbd) > 1:
                raise CBDDuplicatedException("only a CBD is required")
            if len(cbd) == 1:
                r_cbd = cbd[0].radius
                ang_cbd = cbd[0].angle

            etha = 0
            etha_zone = 0

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
                    raise PeripherySubcenterNumberForZoneExceptions(
                        "the number of periphery and subcenter nodes must be equal to 1")

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

            L = sum(r_sc) / len(r_sc)
            g = (sum(r_p) / len(r_p) - L) / L

            Gi = []
            Hi = []
            for i in range(n):
                Gi.append(r_sc[i] / L)
                Hi.append(r_p[i] / (L + g * L))

            angles = ang_sc

            # if parameters are valid
            if graph_obj.parameters_validator(n, L, g, p, etha, etha_zone, angles, Gi, Hi):

                graph_obj.__add_cbd(cbd[0])

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
                    graph_obj.add_zone(node_periphery, node_subcenter)

        else:
            raise FileFormatIsNotValidExceptions("File don't have a valid format. Try with Pajek format")

        return graph_obj
