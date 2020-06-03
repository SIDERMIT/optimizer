
class SIDERMITException(Exception):
    pass


class NIsNotValidNumberException(SIDERMITException):
    pass

class NIsNegative(NIsNotValidNumberException):
    pass

class NIsTooBig(NIsNotValidNumberException):
    pass


class NodeDoesNotExistException(SIDERMITException):
    pass


class NodeTypeIsNotValidException(SIDERMITException):
    pass