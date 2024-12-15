"""
This module contains type definitions for the logging_http_client configuration.

We move the type definitions to a separate file to avoid circular imports.
"""

import logging
import warnings
from typing import Callable, List, Optional

from requests import Response, PreparedRequest

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.http_log_record import HttpLogRecord

CorrelationIdProviderType = Optional[Callable[[], str]]

ResponseHookType = Callable[[logging.Logger, Response], None]
RequestHookType = Callable[[logging.Logger, PreparedRequest], None]

ResponseLogRecordObscurerType = Callable[[HttpLogRecord], HttpLogRecord]
RequestLogRecordObscurerType = Callable[[HttpLogRecord], HttpLogRecord]


def set_correlation_id_provider(provider: CorrelationIdProviderType) -> None:
    """
    Set a provider for the correlation id.

    This is useful for setting a unique value that you can use to correlate
    logs across different services within a distributed system, or an event
    chain lifecycle.

    The provider should be a callable that returns a string.
    """
    config.set_correlation_id_provider(provider)


def set_request_log_record_obscurers(obscurers: List[RequestLogRecordObscurerType]) -> None:
    """
    Sets obscurers for all requests logged.

    This is useful for redacting sensitive information from the log records.

    NOTE:
      - The obscurers are applicable to hooks that utilize the `http_log_record.HttpLogRecord`
        data structure, and which call the `http_log_record.HttpLogRecord.from_request`
        method to generate the log record within the logging hook.
      - The obscurers will run on the log record JUST BEFORE it is logged by the
        request logger. When using the request obscurer, you are also responsible
        for returning the log record in the correct data structure.
      - The obscurers will run in the order they are provided, and they're
        accumulative. This means that the output of the first obscurer will be
        passed to the next obscurer, and so on.
    """
    config.set_request_log_record_obscurers(obscurers)


def set_response_log_record_obscurers(obscurers: List[ResponseLogRecordObscurerType]) -> None:
    """
    Sets obscurers for all responses logged.

    This is useful for redacting sensitive information from the log records.

    NOTE:
      - The obscurers are applicable to hooks that utilise the `http_log_record.HttpLogRecord`
        data structure, and which call the `http_log_record.HttpLogRecord.from_response`
        method to generate the log record within the logging hook.
      - The obscurers will run on the log record JUST BEFORE it is logged by the
        response logger. When using the response obscurer, you are also responsible
        for returning the log record in the correct data structure.
      - The obscurers will run in the order they are provided, and they're
        accumulative. This means that the output of the first obscurer will be
        passed to the next obscurer, and so on.
    """
    config.set_response_log_record_obscurers(obscurers)


def set_request_logging_hooks(hooks: List[RequestHookType]) -> None:
    """
    Set custom hooks for logging all requests.

    The hooks will be called in the order they are provided.
    Each hook will receive an IMMUTABLE request object.
    """
    config.set_request_logging_hooks(hooks)


def set_response_logging_hooks(hooks: List[ResponseHookType]) -> None:
    """
    Set custom hooks for logging all responses.

    The hooks will be called in the order they are provided.
    Each hook will receive an IMMUTABLE response object.
    """
    config.set_response_logging_hooks(hooks)


def disable_request_logging(disabled: bool = True) -> None:
    """
    Enable or disable request logging.
    """
    config.set_request_logging_enabled(not disabled)


def disable_response_logging(disabled: bool = True) -> None:
    """
    Enable or disable response logging.
    """
    config.set_response_logging_enabled(not disabled)


def enable_request_body_logging(enable: bool = True) -> None:
    """
    Enable or disable request body logging on the DEFAULT request logging hook.
    """
    config.set_request_body_logging_enabled(enable)


def enable_response_body_logging(enable: bool = True) -> None:
    """
    Enable or disable response body logging on the DEFAULT response logging hook
    """
    config.set_response_body_logging_enabled(enable)


def set_default_hooks_logging_level(level: int = 20) -> None:
    """
    Set the logging level for the logger.

    CRITICAL = 50
    ERROR    = 40
    WARNING = 30
    INFO    = 20
    DEBUG   = 10
    NOTSET  = 0
    """
    config.set_default_hooks_logging_level(level)


# DEPRECATED ###########################################################################################################


def set_request_log_record_obscurer(obscurer: RequestLogRecordObscurerType) -> None:
    """
    Deprecated: Use `set_request_log_record_obscurers` instead.
    """
    warnings.warn(
        "set_request_log_record_obscurer is deprecated and will be removed in a future release. "
        "Please use set_request_log_record_obscurers instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    set_request_log_record_obscurers([obscurer])


def set_response_log_record_obscurer(obscurer: ResponseLogRecordObscurerType) -> None:
    """
    Deprecated: Use `set_response_log_record_obscurers` instead.
    """
    warnings.warn(
        "set_response_log_record_obscurer is deprecated and will be removed in a future release. "
        "Please use set_response_log_record_obscurers instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    set_response_log_record_obscurers([obscurer])


def set_custom_request_logging_hook(hook: RequestHookType) -> None:
    """
    Deprecated: Use `set_request_logging_hooks` instead.
    """
    warnings.warn(
        "set_custom_request_logging_hook is deprecated and will be removed in a future release. "
        "Please use set_request_logging_hooks instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    set_request_logging_hooks([hook])


def set_custom_response_logging_hook(hook: ResponseHookType) -> None:
    """
    Deprecated: Use `set_response_logging_hooks` instead.
    """
    warnings.warn(
        "set_custom_response_logging_hook is deprecated and will be removed in a future release. "
        "Please use set_response_logging_hooks instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    set_response_logging_hooks([hook])
