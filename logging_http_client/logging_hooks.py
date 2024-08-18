from typing import Optional, Callable

from requests import Response, PreparedRequest

ResponseHookType = Optional[Callable[[Response], None]]
RequestHookType = Optional[Callable[[PreparedRequest], None]]

request_logging_hook: RequestHookType = None
response_logging_hook: ResponseHookType = None


def set_custom_request_logging_hook(hook: RequestHookType) -> None:
    """
    Set a custom hook for logging all requests.
    """
    global request_logging_hook
    request_logging_hook = hook


def set_custom_response_logging_hook(hook: ResponseHookType) -> None:
    """
    Set a custom hook for logging all responses.
    """
    global response_logging_hook
    response_logging_hook = hook
