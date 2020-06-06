# General exception
class SIDERMITException(Exception):
    pass


# Graph exception
class GraphException(SIDERMITException):
    pass

# Exceptions Graph


# build Zone
class NodePeripheryTypeIsNotValidException(GraphException):
    pass


class NodeSubcenterTypeIsNotValidException(GraphException):
    pass


# build Node
class NodeRadiusIsNotValidException(GraphException):
    pass


class NodeAngleIsNotValidException(GraphException):
    pass


class NodeWidthIsNotValidException(GraphException):
    pass


# build graph
class CBDDoesNotExistExceptions(GraphException):
    pass


class ZoneIdIsNotValidExceptions(GraphException):
    pass


class AddPreviousZonesExceptions(GraphException):
    pass


class PeripheryTypeIsNotValidException(GraphException):
    pass


class SubcenterTypeIsNotValidException(GraphException):
    pass


class CBDTypeIsNotValidException(GraphException):
    pass


class CBDDuplicatedException(GraphException):
    pass


class IdNodeIsDuplicatedException(GraphException):
    pass


class EdgeDoesNotExistException(GraphException):
    pass


class IdEdgeIsDuplicatedException(GraphException):
    pass


class NIsNotDefined(GraphException):
    pass


class NIsNotValidNumberException(GraphException):
    pass


class LIsNotDefined(GraphException):
    pass


class LIsNotValidNumberException(GraphException):
    pass


class GIsNotDefined(GraphException):
    pass


class GIsNotValidNumberException(GraphException):
    pass


class PIsNotDefined(GraphException):
    pass


class PIsNotValidNumberException(GraphException):
    pass


class EdgeNotAvailable(GraphException):
    pass


class PajekFormatIsNotValidExceptions(GraphException):
    pass


class FileFormatIsNotValidExceptions(GraphException):
    pass


class NodeTypeIsNotValidExceptions(GraphException):
    pass













