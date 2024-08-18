default_logging_with_request: bool = True
default_logging_with_response: bool = True

default_logging_with_request_body_logging: bool = False
default_logging_with_response_body_logging: bool = False


def enable_request_logging(enable: bool = True) -> None:
    """
    Enable or disable request logging.
    """
    global default_logging_with_request
    default_logging_with_request = enable


def enable_request_body_logging(enable: bool = True) -> None:
    """
    Enable or disable request body logging.
    """
    global default_logging_with_request_body_logging
    default_logging_with_request_body_logging = enable


def enable_response_logging(enable: bool = True) -> None:
    """
    Enable or disable response logging.
    """
    global default_logging_with_response
    default_logging_with_response = enable


def enable_response_body_logging(enable: bool = True) -> None:
    """
    Enable or disable response body logging.
    """
    global default_logging_with_response_body_logging
    default_logging_with_response_body_logging = enable
