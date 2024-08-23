"""
This module contains the global configuration for the logging_http_client.

We separate the configuration globals and getters from the main configuration module to
avoid circular imports when using the configuration getters within the implementation code.
"""

# Correlation ID Provider =====================================================

_correlation_id_provider = None


def get_correlation_id_provider():
    global _correlation_id_provider
    return _correlation_id_provider


def set_correlation_id_provider(value):
    global _correlation_id_provider
    _correlation_id_provider = value


# Request/Response Log Record Obscurers ======================================

_request_log_record_obscurer = None
_response_log_record_obscurer = None


def get_request_log_record_obscurer():
    global _request_log_record_obscurer
    return _request_log_record_obscurer


def get_response_log_record_obscurer():
    global _response_log_record_obscurer
    return _response_log_record_obscurer


def set_request_log_record_obscurer(value):
    global _request_log_record_obscurer
    _request_log_record_obscurer = value


def set_response_log_record_obscurer(value):
    global _response_log_record_obscurer
    _response_log_record_obscurer = value


# Request/Response Hooks =====================================================

_request_logging_hook = None
_response_logging_hook = None


def get_custom_request_logging_hook():
    global _request_logging_hook
    return _request_logging_hook


def get_custom_response_logging_hook():
    global _response_logging_hook
    return _response_logging_hook


def set_custom_request_logging_hook(value):
    global _request_logging_hook
    _request_logging_hook = value


def set_custom_response_logging_hook(value):
    global _response_logging_hook
    _response_logging_hook = value


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
