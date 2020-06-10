from enum import Enum
import pandas as pd
from sidermit.exceptions import *
import math


class GraphFileFormat(Enum):
    # [node_id] [node name] [x] [y] [type] [zone] [width]
    PAJEK = 1


class Zone:

    def __init__(self, zone_id, node_periphery, node_subcenter):

        if zone_id is None:
            raise ZoneIdIsNotValidExceptions("zone_id is not valid")

        if not isinstance(node_periphery, Periphery):
            raise NodePeripheryTypeIsNotValidException('node must be periphery')

        if not isinstance(node_subcenter, Subcenter):
            raise NodeSubcenterTypeIsNotValidException('node must be subcenter')

        if node_periphery.zone_id != zone_id or node_subcenter.zone_id != zone_id:
            raise ZoneIdIsNotValidExceptions("node_periphery and node_subcenter must be equal to zone_id")

        self.id = zone_id
        self.periphery = node_periphery
        self.subcenter = node_subcenter


class Node:

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):

        if name is None:
            raise NameDoesNotDefinedExceptions("must define a name to node")
        if node_id is None:
            raise NodeIdIsNotValidExceptions("zone_id is not valid")
        if zone_id is None:
            raise ZoneIdIsNotValidExceptions("zone_id is not valid")
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
            raise ZoneIdIsNotValidExceptions("CBD node_id must be equal to 0")
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Periphery(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Subcenter(Node):

    def __init__(self, node_id, x, y, radius, angle, width, zone_id, name):
        # atributos de nodos
        Node.__init__(self, node_id, x, y, radius, angle, width, zone_id, name)


class Edge:

    def __init__(self, edge_id, node1, node2):
        if edge_id is None:
            raise EdgeIdIsNotValidExceptions("edge_id is not valid")
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

        self.__nodes_id = []
        self.__edges_id = []
        self.__CBD_exist = False

        self.zones = []
        self.nodes = []
        self.edges = []

        self.n = None
        self.l = None
        self.g = None
        self.p = None
        self.etha = None
        self.etha_zone = None
        self.angles = None
        self.Gi = None
        self.Hi = None

    def graph_to_pajek(self, file_path):

        if self.is_valid():
            file = open(file_path, 'w')
            file.write("*vertices {}{}".format(len(self.nodes), "\n"))
            for node in self.nodes:
                if isinstance(node, CBD):
                    file.write(
                        "{} {} {} {} CBD {} {}{}".format(node.id, node.name, node.x, node.y, node.zone_id, node.width,
                                                         "\n"))
                if isinstance(node, Periphery):
                    file.write(
                        "{} {} {} {} P {} {}{}".format(node.id, node.name, node.x, node.y, node.zone_id, node.width,
                                                       "\n"))
                if isinstance(node, Subcenter):
                    file.write(
                        "{} {} {} {} SC {} {}{}".format(node.id, node.name, node.x, node.y, node.zone_id, node.width,
                                                        "\n"))
            file.close()

        else:
            raise WritePajekFileExceptions("a error writing the Pajek file")


    def is_valid(self):
        n = self.n
        l = self.l
        g = self.g
        p = self.p
        etha = self.etha
        etha_zone = self.etha_zone
        angles = self.angles
        Gi = self.Gi
        Hi = self.Hi

        self.parameters_validator(n, l, g, p, etha, etha_zone, angles, Gi, Hi)
        self.__zones_validator()
        self.__nodes_validator()
        self.__edges_validator()

        return True

    def __zones_validator(self):
        # zone id list to verified duplicated id and existence of the nodes in nodes list
        zone_id_list = []
        for zone in self.zones:
            if zone.id not in zone_id_list:
                zone_id_list.append(zone.id)
            else:
                raise ZoneIdIsNotValidExceptions("Zone id is duplicated")
            # verified periphery and subcenter nodes
            if not isinstance(zone.periphery, Periphery):
                raise PeripheryTypeIsNotValidException("node periphery is not valid")
            if not isinstance(zone.subcenter, Subcenter):
                raise SubcenterTypeIsNotValidException("node subcenter is not valid")

            # to verified periphery and subcenter nodes in node list
            p_exist = False
            sc_exist = False
            for node in self.nodes:
                if node == zone.periphery:
                    p_exist = True
                if node == zone.subcenter:
                    sc_exist = True
            if not p_exist:
                raise PeripheryDoesNotExistExceptions("Node periphery does not exist in nodes list")
            if not sc_exist:
                raise SubcenterDoesNotExistExceptions("Node subcenter does not exist in nodes list")
        # to verified existences and uniqueness of all zones [1, ..., n]
        for i in range(len(self.zones)):
            j = i + 1
            i_exist = False
            for zone_id in zone_id_list:
                if j == zone_id:
                    i_exist = True
                    break
            if not i_exist:
                raise ZoneIdIsNotValidExceptions("must give zone_id in order [1, ..., n]")

    def __nodes_validator(self):
        # numbers of the cbd, p and sc
        n_cbd = 0
        n_p = 0
        n_sc = 0
        # node_id list to duplicated
        node_id_list = []
        for node in self.nodes:
            if isinstance(node, CBD):
                n_cbd = n_cbd + 1
            if isinstance(node, Periphery):
                n_p = n_p + 1
            if isinstance(node, Subcenter):
                n_sc = n_sc + 1
            # node id duplicated
            if node.id not in node_id_list:
                node_id_list.append(node.id)
            else:
                raise IdNodeIsDuplicatedException("node_id is duplicated")
        # only one CBD
        if n_cbd == 0:
            raise CBDDoesNotExistExceptions("a CBD is required")
        if n_cbd > 1:
            raise CBDDoesNotExistExceptions("only a CBD is required")
        # periphery numbers = subcenter numbers
        if n_p != n_sc:
            raise PeripherySubcenterNumberForZoneExceptions("number of P and SC must be equal")

    def __edges_validator(self):

        edge_id_list = []
        for edge in self.edges:
            # node id duplicated
            if edge.id not in edge_id_list:
                edge_id_list.append(edge.id)
            else:
                raise IdEdgeIsDuplicatedException("edge_id is duplicated")
            n1 = edge.node1
            n2 = edge.node2

            n1_exist = False
            n2_exist = False
            for node in self.nodes:
                if node == n1:
                    n1_exist = True
                if node == n2:
                    n2_exist = True
            if not n1_exist:
                raise NodeDoesNotExistExceptions("node 1 does not exist")
            if not n2_exist:
                raise NodeDoesNotExistExceptions("node 2 does not exist")

    @staticmethod
    def parameters_validator(n, l, g, p, etha=None, etha_zone=None, angles=None, Gi=None, Hi=None):
        if n < 0 or not isinstance(n, int):
            raise NIsNotValidNumberException('n cannot be a negative number')
        if l < 0:
            raise LIsNotValidNumberException('L cannot be a negative number')
        if g < 0:
            raise GIsNotValidNumberException('G cannot be a negative number')
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
            CBD_node = CBD(0, 0, 0, 0, 0, p, 0, "CBD")
            graph_obj.__add_cbd(CBD_node)

            # Add zones
            for zone in range(n):
                id_p = 2 * zone + 1
                id_sc = 2 * zone + 2
                radius_p = l + g * l
                radius_sc = l
                angle_p = 360 / n * zone
                angle_sc = 360 / n * zone
                x_p, y_p = graph_obj.obtain_xy(radius_p, angle_p)
                x_sc, y_sc = graph_obj.obtain_xy(radius_sc, angle_sc)

                node_p = Periphery(id_p, x_p, y_p, radius_p, angle_p, p, zone + 1, "P_{}".format(zone + 1))
                node_sc = Subcenter(id_sc, x_sc, y_sc, radius_sc, angle_sc, p, zone + 1, "SC_{}".format(zone + 1))

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

        graph_obj.n = n
        graph_obj.l = l
        graph_obj.g = g
        graph_obj.p = p
        graph_obj.etha = etha
        graph_obj.etha_zone = etha_zone
        graph_obj.angles = angles
        graph_obj.Gi = Gi
        graph_obj.Hi = Hi

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
            nnodes = 0
            for line in f_obj.readlines():
                if line.lower().startswith("*vertices"):
                    _, nnodes = line.split()
                    nnodes = int(nnodes)
                    continue
                if nnodes > 0:
                    if len(line.split()) == 7:
                        node_id, name, x, y, node_type, zone, width = line.split()
                        if node_type != "CBD" and node_type != "SC" and node_type != "P":
                            raise NodeTypeIsNotValidExceptions("Node type is not valid. Try with CBD, SC or P")
                        if int(zone) < 0:
                            raise ZoneIdIsNotValidExceptions("zone is not valid. Try with a positive value")
                        col_id.append(node_id)
                        col_name.append(name)
                        col_x.append(x)
                        col_y.append(y)
                        col_type.append(node_type)
                        col_zone.append(zone)
                        col_width.append(width)

                        nnodes = nnodes - 1
                    else:
                        raise PajekFormatIsNotValidExceptions("each node line must provide information about [id] ["
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
    def obtain_angle(x, y):
        a = 1
        b = 0
        c = x
        d = y

        if x == 0 and y == 0:
            return 0

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
    def obtain_xy(radius, angle):
        x, y = radius * math.cos(math.radians(angle)), radius * math.sin(math.radians(angle))
        return x, y

    @staticmethod
    def build_from_file(file_path, file_format=GraphFileFormat.PAJEK):

        """
        :param file_path:
        :param file_format:
        :return: Graph instance
        """
        graph_obj = Graph()

        if file_format == GraphFileFormat.PAJEK:

            df_file = graph_obj.__pajekfile_to_dataframe(file_path)

            df_file = df_file.sort_values(["zone", "type"], ascending=[True, True])

            n = int((len(df_file["node_id"]) - 1) / 2)

            if not isinstance(n, int):
                raise NumberLinesInTheFileIsNotValidExceptions("The number of lines in the file must be 2n+1")

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
                angle = graph_obj.obtain_angle(x, y)

                if node_type == "CBD":
                    cbd.append(CBD(node_id, x, y, radius, angle, width, zone, name))
                if node_type == "P":
                    periphery.append(Periphery(node_id, x, y, radius, angle, width, zone, name))
                if node_type == "SC":
                    subcenter.append(Subcenter(node_id, x, y, radius, angle, width, zone, name))
                if node_type != "CBD" and node_type != "P" and node_type != "SC":
                    raise NodeTypeIsNotValidExceptions("node type is not valid, try with CBD, P or SC")

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

        graph_obj.n = n
        graph_obj.l = L
        graph_obj.g = g
        graph_obj.p = width
        graph_obj.etha = etha
        graph_obj.etha_zone = etha_zone
        graph_obj.angles = angles
        graph_obj.Gi = Gi
        graph_obj.Hi = Hi

        return graph_obj

    def __add_cbd(self, CBD_node):
        if CBD_node.id in self.__nodes_id:
            raise IdEdgeIsDuplicatedException("node id is duplicated")
        if not isinstance(CBD_node, CBD):
            raise CBDTypeIsNotValidException('CBD_node is not a valid CBD node')
        if self.__CBD_exist:
            raise CBDDuplicatedException('a CBD already exists')
        self.__CBD_exist = True
        self.__nodes_id.append(CBD_node.id)
        self.nodes.append(CBD_node)

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
        if node_subcenter.zone_id != len(self.zones) + 1 or node_periphery.zone_id != len(self.zones) + 1:
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
        if node_periphery.id in self.__nodes_id:
            raise IdNodeIsDuplicatedException('id_node periphery is duplicated')
        if node_subcenter.id in self.__nodes_id:
            raise IdNodeIsDuplicatedException('id_node subcenter is duplicated')

        self.nodes.append(node_periphery)
        self.nodes.append(node_subcenter)
        self.__nodes_id.append(node_periphery.id)
        self.__nodes_id.append(node_subcenter.id)

    def __build_edges(self):
        self.edges = []
        self.__edges_id = []
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
                if i != 1 and j != 0:
                    self.__add_edge(Edge(len(self.edges) + 1, sc, sc2))
                    self.__add_edge(Edge(len(self.edges) + 1, sc2, sc))

    def __add_edge(self, edge):
        if not isinstance(edge, Edge):
            raise EdgeDoesNotExistException('is not a valid edge')
        if edge.id in self.__edges_id:
            raise IdEdgeIsDuplicatedException('id edge is duplicated')
        self.edges.append(edge)
        self.__edges_id.append(edge.id)

    def __etha_asymmetry(self, etha, etha_zone):

        zone = self.zones[etha_zone - 1]
        sc = zone.subcenter
        r_cbd = etha * sc.radius
        ang = sc.angle

        x_cbd, y_cbd = self.obtain_xy(r_cbd, ang)

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
            x_p, y_p = self.obtain_xy(r_p, ang)

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
            x_sc, y_sc = self.obtain_xy(r_sc, ang)

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
            x_p, y_p = self.obtain_xy(r_p, ang)
            x_sc, y_sc = self.obtain_xy(r_sc, ang)

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
