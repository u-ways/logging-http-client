"""
This module contains the global configuration for the logging_http_client.

We separate the configuration globals and getters from the main configuration module to
avoid circular imports when using the configuration getters within the implementation code.
"""

import logging

# Correlation ID Provider =====================================================

_correlation_id_provider = None


def get_correlation_id_provider():
    global _correlation_id_provider
    return _correlation_id_provider


def set_correlation_id_provider(value):
    global _correlation_id_provider
    _correlation_id_provider = value


# Request/Response Log Record Obscurers ======================================

_request_log_record_obscurers: list = []
_response_log_record_obscurers: list = []


def get_request_log_record_obscurers():
    global _request_log_record_obscurers
    return _request_log_record_obscurers


def get_response_log_record_obscurers():
    global _response_log_record_obscurers
    return _response_log_record_obscurers


def set_request_log_record_obscurers(value):
    global _request_log_record_obscurers
    _request_log_record_obscurers = value


def set_response_log_record_obscurers(value):
    global _response_log_record_obscurers
    _response_log_record_obscurers = value


# Request/Response Hooks =====================================================

_request_logging_hooks: list = []
_response_logging_hooks: list = []


def get_request_logging_hooks():
    global _request_logging_hooks
    return _request_logging_hooks


def get_response_logging_hooks():
    global _response_logging_hooks
    return _response_logging_hooks


def set_request_logging_hooks(value):
    global _request_logging_hooks
    _request_logging_hooks = value


def set_response_logging_hooks(value):
    global _response_logging_hooks
    _response_logging_hooks = value


# Request/Response Logging Toggle =============================================

_request_logging_enabled: bool = True
_response_logging_enabled: bool = True


def is_request_logging_enabled() -> bool:
    global _request_logging_enabled
    return _request_logging_enabled


def is_response_logging_enabled() -> bool:
    global _response_logging_enabled
    return _response_logging_enabled


def set_request_logging_enabled(value: bool):
    global _request_logging_enabled
    _request_logging_enabled = value


def set_response_logging_enabled(value: bool):
    global _response_logging_enabled
    _response_logging_enabled = value


# Request/Response Body Logging Toggle ========================================

_request_body_logging_enabled: bool = False
_response_body_logging_enabled: bool = False


def is_request_body_logging_enabled() -> bool:
    global _request_body_logging_enabled
    return _request_body_logging_enabled


def is_response_body_logging_enabled() -> bool:
    global _response_body_logging_enabled
    return _response_body_logging_enabled


def set_request_body_logging_enabled(value: bool):
    global _request_body_logging_enabled
    _request_body_logging_enabled = value


def set_response_body_logging_enabled(value: bool):
    global _response_body_logging_enabled
    _response_body_logging_enabled = value


# Default Hooks Logging Level =============================================

_default_hooks_logging_level: int = logging.INFO


def set_default_hooks_logging_level(value: int):
    global _default_hooks_logging_level
    _default_hooks_logging_level = value


def get_default_hooks_logging_level():
    global _default_hooks_logging_level
    return _default_hooks_logging_level
