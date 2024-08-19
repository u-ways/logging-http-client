from typing import Optional, Callable

from requests import Response, PreparedRequest

_request_logging_enabled: bool = True
_response_logging_enabled: bool = True

_request_body_logging_enabled: bool = False
_response_body_logging_enabled: bool = False

ResponseHookType = Optional[Callable[[Response], None]]
RequestHookType = Optional[Callable[[PreparedRequest], None]]

_request_logging_hook: RequestHookType = None
_response_logging_hook: ResponseHookType = None


def get_custom_request_logging_hook() -> RequestHookType:
    """
    Get the custom hook for logging all requests.
    """
    global _request_logging_hook
    return _request_logging_hook


def get_custom_response_logging_hook() -> ResponseHookType:
    """
    Get the custom hook for logging all responses.
    """
    global _response_logging_hook
    return _response_logging_hook


def set_custom_request_logging_hook(hook: RequestHookType) -> None:
    """
    Set a custom hook for logging all requests.
    """
    global _request_logging_hook
    _request_logging_hook = hook


def set_custom_response_logging_hook(hook: ResponseHookType) -> None:
    """
    Set a custom hook for logging all responses.
    """
    global _response_logging_hook
    _response_logging_hook = hook


def is_request_logging_enabled() -> bool:
    return _request_logging_enabled


def is_response_logging_enabled() -> bool:
    return _response_logging_enabled


def is_request_body_logging_enabled() -> bool:
    return _request_body_logging_enabled


def is_response_body_logging_enabled() -> bool:
    return _response_body_logging_enabled


def enable_request_logging(enable: bool = True) -> None:
    """
    Enable or disable request logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    global _request_logging_enabled
    _request_logging_enabled = enable


def enable_response_logging(enable: bool = True) -> None:
    """
    Enable or disable response logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    global _response_logging_enabled
    _response_logging_enabled = enable


def enable_request_body_logging(enable: bool = True) -> None:
    """
    Enable or disable request body logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    global _request_body_logging_enabled
    _request_body_logging_enabled = enable


def enable_response_body_logging(enable: bool = True) -> None:
    """
    Enable or disable response body logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    global _response_body_logging_enabled
    _response_body_logging_enabled = enable
