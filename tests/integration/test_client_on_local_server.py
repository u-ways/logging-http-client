import logging
from logging import LogRecord

import pytest
from wiremock.resources.mappings import HttpMethods

import logging_http_client
import logging_http_client_config
from http_headers import X_REQUEST_ID_HEADER, X_SOURCE_HEADER


def test_client_returns_correct_response_details(wiremock_server):
    wiremock_server.for_endpoint("/ping", return_status=418, return_body='{ "message": "pong!" }')

    response = logging_http_client.create().get(
        url=wiremock_server.get_url("/ping"), headers={"accept": "application/json"}
    )

    assert response.status_code == 418
    assert response.content == b'{ "message": "pong!" }'
    assert response.headers["content-type"] == "application/json"


def test_client_should_log_request_details_by_default(wiremock_server, caplog):
    wiremock_server.for_endpoint("/some_endpoint")

    with caplog.at_level(logging.INFO):
        logging_http_client.create(source="test_client").get(
            url=wiremock_server.get_url("/some_endpoint"), headers={"accept": "application/json"}
        )

    relevant_logs = [record for record in caplog.records if record.message == "REQUEST"]

    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log: LogRecord = relevant_logs.pop()

    if hasattr(request_log, "http"):
        assert request_log.http["request_source"] == "test_client"
        assert request_log.http["request_method"] == "GET"
        assert request_log.http["request_url"] == wiremock_server.get_url("/some_endpoint")
        assert request_log.http["request_headers"]["accept"] == "application/json"
        assert request_log.http["request_headers"][X_SOURCE_HEADER] == request_log.http["request_source"]
        assert request_log.http["request_headers"][X_REQUEST_ID_HEADER] == request_log.http["request_id"]
        assert request_log.http.get("request_body") is None
    else:
        pytest.fail("Request log does not contain 'http' attribute")


def test_client_should_log_response_details_by_default(wiremock_server, caplog):
    wiremock_server.for_endpoint("/another_endpoint", return_status=500)

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/another_endpoint"), headers={"accept": "application/json"}
        )

    relevant_logs = [record for record in caplog.records if record.message == "RESPONSE"]

    assert len(relevant_logs) == 1, f"Expected 1 response log, found {len(relevant_logs)}"

    response_log: LogRecord = relevant_logs.pop()

    if hasattr(response_log, "http"):
        assert response_log.http["request_id"] is not None
        assert response_log.http["response_status"] == 500
        assert response_log.http["response_duration_ms"] > 0
        assert response_log.http.get("response_body") is None
    else:
        pytest.fail("Response log does not contain 'http' attribute")


def test_client_should_log_request_with_body_logging_enabled(wiremock_server, caplog):
    logging_http_client_config.enable_request_body_logging(enable=True)
    logging_http_client_config.enable_response_body_logging(enable=True)

    wiremock_server.for_endpoint(
        "/create", method=HttpMethods.POST, return_status=201, return_body='{ "message": "done!" }'
    )

    with caplog.at_level(logging.INFO):
        logging_http_client.create().post(
            url=wiremock_server.get_url("/create"), headers={"accept": "application/json"}, json='{ "key": "value" }'
        )

    relevant_logs = [record for record in caplog.records if record.message in ["REQUEST", "RESPONSE"]]

    assert len(relevant_logs) == 2, f"Expected 2 logs, found {len(relevant_logs)}"

    request_log, response_log = relevant_logs

    assert request_log.message == "REQUEST"
    assert request_log.http["request_method"] == "POST"
    assert request_log.http["request_headers"]["accept"] == "application/json"
    assert request_log.http["request_body"] == '"{ \\"key\\": \\"value\\" }"'

    assert response_log.message == "RESPONSE"
    assert response_log.http["response_status"] == 201
    assert response_log.http["response_headers"]["Content-Type"] == "application/json"
    assert response_log.http["response_body"] == '{ "message": "done!" }'


def test_client_should_log_with_logging_disabled(wiremock_server, caplog):
    logging_http_client_config.enable_request_logging(enable=False)
    logging_http_client_config.enable_response_logging(enable=False)

    wiremock_server.for_endpoint("/secret")

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/secret"),
        )

    relevant_logs = [record for record in caplog.records if record.message in ["REQUEST", "RESPONSE"]]

    assert len(relevant_logs) == 0, f"Expected 0 logs, found {len(relevant_logs)}"
