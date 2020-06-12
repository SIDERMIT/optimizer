# General exception
class SIDERMITException(Exception):
    pass


# Graph exception
class GraphException(SIDERMITException):
    pass


# Demand exception
class DemandException(SIDERMITException):
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


class EthaValueRequiredExceptions(GraphException):
    pass


class EthaZoneValueRequiredExceptions(GraphException):
    pass


class EthaValueIsNotValidExceptions(GraphException):
    pass


class EthaZoneValueIsNotValidExceptions(GraphException):
    pass


class LenAnglesIsNotValidExceptions(GraphException):
    pass


class AngleValueIsNotValidEceptions(GraphException):
    pass


class LenGiIsNotValidExceptions(GraphException):
    pass


class GiValueIsNotValidEceptions(GraphException):
    pass


class LenHiIsNotValidExceptions(GraphException):
    pass


class HiValueIsNotValidEceptions(GraphException):
    pass


class NumberLinesInTheFileIsNotValidExceptions(GraphException):
    pass


class PeripherySubcenterNumberForZoneExceptions(GraphException):
    pass


class PeripheryDoesNotExistExceptions(GraphException):
    pass


class SubcenterDoesNotExistExceptions(GraphException):
    pass


class NodeIdIsNotValidExceptions(GraphException):
    pass


class EdgeIdIsNotValidExceptions(GraphException):
    pass


class NodeDoesNotExistExceptions(GraphException):
    pass


class WritePajekFileExceptions(GraphException):
    pass


class NameDoesNotDefinedExceptions(GraphException):
    pass

# Exceptions Demand
class GraphIsNotValidExceptions(DemandException):
    pass


class NIsNotValidExceptions(DemandException):
    pass


class YIsNotValidExceptions(DemandException):
    pass


class AIsNotValidExceptions(DemandException):
    pass


class AlphaIsNotValidExceptions(DemandException):
    pass


class BetaIsNotValidExceptions(DemandException):
    pass


class NOutRangeExceptions(DemandException):
    pass


class YOutRangeExceptions(DemandException):
    pass


class AOutRangeExceptions(DemandException):
    pass


class AlphaOutRangeExceptions(DemandException):
    pass


class BetaOutRangeExceptions(DemandException):
    pass


class AlphaBetaOutRangeExceptions(DemandException):
    pass


class IdDestinationnDoesNotFoundExceptions(DemandException):
    pass


class IdOriginDoesNotFoundExceptions(DemandException):
    pass
