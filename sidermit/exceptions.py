# General exception
class SIDERMITException(Exception):
    pass


# Graph exception
class GraphException(SIDERMITException):
    pass


# Demand exception
class DemandException(SIDERMITException):
    pass


# Transport Mode exception
class TransportModeException(SIDERMITException):
    pass


# Transport User exception
class TransportUserException(SIDERMITException):
    pass


# Transport Network Exceptions
class TransportNetworkException(SIDERMITException):
    pass


class HyperpathException(SIDERMITException):
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


# TransportModeException
class ByaIsNotValidExceptions(TransportModeException):
    pass


class C2IsNotValidExceptions(TransportModeException):
    pass


class C1IsNotValidExceptions(TransportModeException):
    pass


class KmaxIsNotValidExceptions(TransportModeException):
    pass


class TIsNotValidExceptions(TransportModeException):
    pass


class FmaxIsNotValidExceptions(TransportModeException):
    pass


class ThetaIsNotValidExceptions(TransportModeException):
    pass


class DIsNotValidExceptions(TransportModeException):
    pass


class TatIsNotValidExceptions(TransportModeException):
    pass


class VIsNotValidExceptions(TransportModeException):
    pass


class CoIsNotValidExceptions(TransportModeException):
    pass


class ModeIsNotValidException(TransportModeException):
    pass


class NameIsNotValidExceptions(TransportModeException):
    pass


class AddModeExceptions(TransportModeException):
    pass


class ModeDoesNotExistExceptions(TransportModeException):
    pass


class ModeNotFoundExceptions(TransportModeException):
    pass


# transport user exceptions
class PvIsNotValidExceptions(TransportUserException):
    pass


class PaIsNotValidExceptions(TransportUserException):
    pass


class VaIsNotValidExceptions(TransportUserException):
    pass


class PwIsNotValidExceptions(TransportUserException):
    pass


class SpvIsNotValidExceptions(TransportUserException):
    pass


class SpaIsNotValidExceptions(TransportUserException):
    pass


class PtIsNotValidExceptions(TransportUserException):
    pass


class SpwIsNotValidExceptions(TransportUserException):
    pass


class SptIsNotValidExceptions(TransportUserException):
    pass


class RouteIdIsNotValidException(TransportNetworkException):
    pass


class ModeNameIsNotValidException(TransportNetworkException):
    pass


class SequencesLenException(TransportNetworkException):
    pass


class StopsSequencesException(TransportNetworkException):
    pass


class FirstStopIsNotValidException(TransportNetworkException):
    pass


class LastStopIsNotValidException(TransportNetworkException):
    pass


class NotCycleException(TransportNetworkException):
    pass


class NodeSequencesIsNotValidException(TransportNetworkException):
    pass


class RouteIdNotFoundException(TransportNetworkException):
    pass


class RouteIdDuplicatedException(TransportNetworkException):
    pass


class ModeNameNotFoundException(TransportNetworkException):
    pass


class JumpIsNotValidException(TransportNetworkException):
    pass


class BanRouteIdException(TransportNetworkException):
    pass


class CircularRouteIsNotValidException(TransportNetworkException):
    pass


class RouteIsNotvalidException(TransportNetworkException):
    pass


class TransportNetworkIsNotValidException(HyperpathException):
    pass
