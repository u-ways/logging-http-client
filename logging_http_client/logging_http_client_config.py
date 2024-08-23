"""
This module contains type definitions for the logging_http_client configuration.

We move the type definitions to a separate file to avoid circular imports.
"""

import logging
from typing import Optional, Callable

from requests import Response, PreparedRequest

import logging_http_client_config_globals
from logging_http_client import HttpLogRecord

CorrelationIdProviderType = Optional[Callable[[], str]]

ResponseHookType = Optional[Callable[[logging.Logger, Response], None]]
RequestHookType = Optional[Callable[[logging.Logger, PreparedRequest], None]]

ResponseLogRecordObscurerType = Optional[Callable[[HttpLogRecord], HttpLogRecord]]
RequestLogRecordObscurerType = Optional[Callable[[HttpLogRecord], HttpLogRecord]]


def set_correlation_id_provider(provider: CorrelationIdProviderType) -> None:
    """
    Set a provider for the correlation id.

    This is useful for setting a unique value that you can use to correlate
    logs across different services within a distributed system, or an event
    chain lifecycle.

    The provider should be a callable that returns a string.
    """
    logging_http_client_config_globals.set_correlation_id_provider(provider)


def set_request_log_record_obscurer(obscurer: RequestLogRecordObscurerType) -> None:
    """
    Sets an obscurer for all requests logged.

    This is useful for redacting sensitive information from the log records.

    The obscurer will run on the log record JUST BEFORE it is logged by the
    request logger. When using the request obscurer, you are also responsible
    for returning the log record in the correct data structure.
    """
    logging_http_client_config_globals.set_request_log_record_obscurer(obscurer)


def set_response_log_record_obscurer(obscurer: ResponseLogRecordObscurerType) -> None:
    """
    Sets an obscurer for all responses logged.

    This is useful for redacting sensitive information from the log records.

    The obscurer will run on the log record JUST BEFORE it is logged by the
    response logger. When using the response obscurer, you are also responsible
    for returning the log record in the correct data structure.
    """
    logging_http_client_config_globals.set_response_log_record_obscurer(obscurer)


def set_custom_request_logging_hook(hook: RequestHookType) -> None:
    """
    Set a custom hook for logging all requests.
    """
    logging_http_client_config_globals.set_custom_request_logging_hook(hook)


def set_custom_response_logging_hook(hook: ResponseHookType) -> None:
    """
    Set a custom hook for logging all responses.
    """
    logging_http_client_config_globals.set_custom_response_logging_hook(hook)


def disable_request_logging(disabled: bool = True) -> None:
    """
    Enable or disable request logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    logging_http_client_config_globals.set_request_logging_enabled(not disabled)


def disable_response_logging(disabled: bool = True) -> None:
    """
    Enable or disable response logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    logging_http_client_config_globals.set_response_logging_enabled(not disabled)


def enable_request_body_logging(enable: bool = True) -> None:
    """
    Enable or disable request body logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    logging_http_client_config_globals.set_request_body_logging_enabled(enable)


def enable_response_body_logging(enable: bool = True) -> None:
    """
    Enable or disable response body logging.

    NOTE:
        These has no effect if you have set up custom logging hooks. (i.e.
        these are for modifying the default logging setup)
    """
    logging_http_client_config_globals.set_response_body_logging_enabled(enable)
