# General exception
class SIDERMITException(Exception):
    pass


# Graph exception
class GraphException(SIDERMITException):
    pass


# Demand exception
class DemandException(SIDERMITException):
    pass


# Graph Exceptions


# build Zone
class PeripheryNodeTypeIsNotValidException(GraphException):
    pass


class SubcenterNodeTypeIsNotValidException(GraphException):
    pass


# build Node
class NodeRadiusIsNotValidException(GraphException):
    pass


class NodeAngleIsNotValidException(GraphException):
    pass


class NodeWidthIsNotValidException(GraphException):
    pass


# build graph
class CBDDoesNotExistException(GraphException):
    pass


class ZoneIdIsNotValidException(GraphException):
    pass


class AddPreviousZonesException(GraphException):
    pass


class PeripheryTypeIsNotValidException(GraphException):
    pass


class SubcenterTypeIsNotValidException(GraphException):
    pass


class CBDTypeIsNotValidException(GraphException):
    pass


class CBDDuplicatedException(GraphException):
    pass


class NodeIdDuplicatedException(GraphException):
    pass


class EdgeDoesNotExistException(GraphException):
    pass


class EdgeIdDuplicatedException(GraphException):
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


class EdgeIsNotAvailableException(GraphException):
    pass


class PajekFormatIsNotValidException(GraphException):
    pass


class FileFormatIsNotValidException(GraphException):
    pass


class NodeTypeIsNotValidException(GraphException):
    pass


class EthaValueRequiredException(GraphException):
    pass


class EthaZoneValueRequiredException(GraphException):
    pass


class EthaValueIsNotValidException(GraphException):
    pass


class EthaZoneValueIsNotValidException(GraphException):
    pass


class AngleListLengthIsNotValidException(GraphException):
    pass


class AngleValueIsNotValidException(GraphException):
    pass


class GiListLengthIsNotValidException(GraphException):
    pass


class GiValueIsNotValidException(GraphException):
    pass


class HiListLengthIsNotValidException(GraphException):
    pass


class HiValueIsNotValidException(GraphException):
    pass


class LineNumberInFileIsNotValidException(GraphException):
    pass


class PeripherySubcenterNumberForZoneException(GraphException):
    pass


class PeripheryDoesNotExistException(GraphException):
    pass


class SubcenterDoesNotExistException(GraphException):
    pass


class NodeIdIsNotValidException(GraphException):
    pass


class EdgeIdIsNotValidException(GraphException):
    pass


class NodeDoesNotExistException(GraphException):
    pass


class WritePajekFileException(GraphException):
    pass


class NameIsNotDefinedException(GraphException):
    pass


# Demand Exceptions
class GraphIsNotValidException(DemandException):
    pass


class NIsNotValidException(DemandException):
    pass


class YIsNotValidException(DemandException):
    pass


class AIsNotValidException(DemandException):
    pass


class AlphaIsNotValidException(DemandException):
    pass


class BetaIsNotValidException(DemandException):
    pass


class NOutOfRangeException(DemandException):
    pass


class YOutOfRangeException(DemandException):
    pass


class AOutOfRangeException(DemandException):
    pass


class AlphaOutOfRangeException(DemandException):
    pass


class BetaOutOfRangeException(DemandException):
    pass


class AlphaBetaOutOfRangeException(DemandException):
    pass


class DestinationIdDoesNotFoundException(DemandException):
    pass


class OriginIdDoesNotFoundException(DemandException):
    pass


class TripsValueIsNotValidException(DemandException):
    pass
