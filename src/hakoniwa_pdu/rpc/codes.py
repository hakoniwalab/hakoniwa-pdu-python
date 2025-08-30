from enum import IntEnum

class SystemControlOpCode(IntEnum):
    """
    Opcodes for the SystemControl service request.
    """
    ACTIVATE = 0
    START = 1
    STOP = 2
    RESET = 3
    TERMINATE = 4
    STATUS = 5
    # Note: 'activate' is not yet assigned a value.

class SystemControlStatusCode(IntEnum):
    """
    Status codes for the SystemControl service response.
    """
    OK = 0
    ERROR = 1
    FATAL = 2
    INTERNAL = 3
    # Add other status codes as needed.
