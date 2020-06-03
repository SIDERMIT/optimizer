from enum import Enum
from sidermit.exceptions import NodeTypeIsNotValidException


class GraphFileFormat(Enum):
    PAYEK = 1


class NodeType(Enum):
    CBD = 1
    SUBCENTER = 2
    PERIPHERY = 3


class Node:

    def __init__(self, x, y, id, type, name=None):
        if not isinstance(type, NodeType):
            raise NodeTypeIsNotValidException('"{0}" is not valid'.format(type))

        self.x = x
        self.y = y
        self.id = id
        self.type = type
        self.name = name


class Edge:

    def __init__(self, node1, node2, id):
        if not isinstance(node1, Node):
            raise ValueError('node1 is not a valid node')
        if not isinstance(node2, Node):
            raise ValueError('node2 is not a valid node')

        self.node1 = node1
        self.node2 = node2


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def build_from_file(file_path, format=GraphFileFormat.PAYEK):
        """

        :param format:
        :return: Graph instance
        """
        graph_obj = Graph()
        if format == GraphFileFormat.PAYEK:
            with open(file_path, mode='r', encoding='utf-8') as f_obj:
                for line in f_obj.readlines():
                    pass


        return graph_obj

    def build_from_parameters(self, n, l, g):
        """
        create symetric
        :param n:
        :param l:
        :param g:
        :return:
        """

        if n < 0:
            raise ValueError('n no puede ser un número negativo')


        graph_obj = Graph()

        # buld nodes and edges

        return graph_obj
