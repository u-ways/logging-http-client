from logging_http_client import HttpLogRecord
from logging_http_client_config import (
    set_request_log_record_obscurer,
    set_response_log_record_obscurer,
)
from logging_http_client_config_globals import (
    get_request_log_record_obscurer,
    get_response_log_record_obscurer,
)


def mock_request_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.request_method = "REDACTED"
    if record.request_headers.get("Authorization") is not None:
        record.request_headers["Authorization"] = "Bearer ****"
    return record


def mock_response_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.response_status = 999
    if record.response_body is not None:
        record.response_body = record.response_body.replace("SENSITIVE", "****")
    return record


# Global Getters and Setters Smoke Tests ======================================


def test_default_request_log_record_obscurer_is_none():
    assert get_request_log_record_obscurer() is None


def test_default_response_log_record_obscurer_is_none():
    assert get_response_log_record_obscurer() is None


def test_set_request_log_record_obscurer():
    set_request_log_record_obscurer(mock_request_log_record_obscurer)
    assert get_request_log_record_obscurer() is mock_request_log_record_obscurer


def test_set_response_log_record_obscurer():
    set_response_log_record_obscurer(mock_response_log_record_obscurer)
    assert get_response_log_record_obscurer() is mock_response_log_record_obscurer


def test_reset_request_log_record_obscurer():
    set_request_log_record_obscurer(mock_request_log_record_obscurer)
    set_request_log_record_obscurer(None)
    assert get_request_log_record_obscurer() is None


def test_reset_response_log_record_obscurer():
    set_response_log_record_obscurer(mock_response_log_record_obscurer)
    set_response_log_record_obscurer(None)
    assert get_response_log_record_obscurer() is None


# Functionality Tests =========================================================


def test_request_log_record_obscurer_functionality():
    set_request_log_record_obscurer(mock_request_log_record_obscurer)

    http_log_record = HttpLogRecord(
        request_method="GET",
        request_headers={"Authorization": "Bearer super-secret-token"},
        request_body="some request body that should not be changed",
    )

    obscurer = get_request_log_record_obscurer()
    obscured_record: HttpLogRecord = obscurer(http_log_record)

    assert obscured_record.request_method == "REDACTED"
    assert obscured_record.request_headers["Authorization"] == "Bearer ****"
    assert obscured_record.request_body == "some request body that should not be changed"


def test_response_log_record_obscurer_functionality():
    set_response_log_record_obscurer(mock_response_log_record_obscurer)

    http_log_record = HttpLogRecord(
        response_status=200,
        response_body="some response body with SENSITIVE information",
    )
    obscurer = get_response_log_record_obscurer()
    obscured_record: HttpLogRecord = obscurer(http_log_record)

    assert obscured_record.response_status == 999
    assert obscured_record.response_body == "some response body with **** information"
