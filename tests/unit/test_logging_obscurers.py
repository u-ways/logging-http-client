import pytest
from requests import Response, PreparedRequest

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.http_log_record import HttpLogRecord
from logging_http_client.logging_http_client_config import (
    set_request_log_record_obscurer,
    set_response_log_record_obscurer,
    set_request_log_record_obscurers,
    set_response_log_record_obscurers,
)


def request_hook(_, request: PreparedRequest) -> None:
    print(f"Request method: {request.method}")


def response_hook(_, response: Response) -> None:
    print(f"Response status code: {response.status_code}")


def request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    if record.request_headers:
        record.request_headers["X-Request-Obscured"] = "******"
    else:
        record.request_headers = {"X-Request-Obscured": "******"}
    return record


def response_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.response_body = "OBSCURED"
    return record


def another_request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.request_body = "ANOTHER_OBSCURED"
    return record


def another_response_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.response_status = 999
    return record


# Tests for defaults =======================================================================================


def test_default_request_log_record_obscurers_is_empty():
    assert isinstance(config.get_request_log_record_obscurers(), list)
    assert len(config.get_request_log_record_obscurers()) == 0


def test_default_response_log_record_obscurers_is_empty():
    assert isinstance(config.get_response_log_record_obscurers(), list)
    assert len(config.get_response_log_record_obscurers()) == 0


# Tests for setting obscurers ==============================================================================


def test_set_request_log_record_obscurers():
    set_request_log_record_obscurers([request_obscurer, another_request_obscurer])
    assert config.get_request_log_record_obscurers() == [request_obscurer, another_request_obscurer]


def test_set_response_log_record_obscurers():
    set_response_log_record_obscurers([response_obscurer, another_response_obscurer])
    assert config.get_response_log_record_obscurers() == [response_obscurer, another_response_obscurer]


def test_reset_request_log_record_obscurers():
    set_request_log_record_obscurers([request_obscurer])
    set_request_log_record_obscurers([])
    assert config.get_request_log_record_obscurers() == []


def test_reset_response_log_record_obscurers():
    set_response_log_record_obscurers([response_obscurer])
    set_response_log_record_obscurers([])
    assert config.get_response_log_record_obscurers() == []


# Tests for obscurers functionality ========================================================================


def test_request_obscurers_functionality():
    set_request_log_record_obscurers([request_obscurer, another_request_obscurer])

    request = PreparedRequest()
    request.method = "POST"
    request.url = "http://example.com"
    request.headers = {"Authorization": "secret"}
    request.body = "sensitive_data"

    result = HttpLogRecord.request_processor("TEST_SYSTEM", "req-123", request)
    http_data = result["http"]

    assert http_data["request_headers"]["X-Request-Obscured"] == "******"
    assert http_data["request_body"] == "ANOTHER_OBSCURED"


def test_response_obscurers_functionality():
    set_response_log_record_obscurers([response_obscurer, another_response_obscurer])

    response = Response()
    response.status_code = 200
    response._content = b"original_response_body"
    response.elapsed = type("Elapsed", (object,), {"microseconds": 5000})()

    result = HttpLogRecord.response_processor("req-123", response)
    http_data = result["http"]

    assert http_data["response_body"] == "OBSCURED"
    assert http_data["response_status"] == 999


# DEPRECATED FUNCTIONS TESTS ==========================================================================================


def test_set_request_log_record_obscurer_deprecated():
    with pytest.warns(DeprecationWarning, match="set_request_log_record_obscurer is deprecated"):
        set_request_log_record_obscurer(request_obscurer)

    assert config.get_request_log_record_obscurers() == [request_obscurer]


def test_set_response_log_record_obscurer_deprecated():
    with pytest.warns(DeprecationWarning, match="set_response_log_record_obscurer is deprecated"):
        set_response_log_record_obscurer(response_obscurer)

    assert config.get_response_log_record_obscurers() == [response_obscurer]
