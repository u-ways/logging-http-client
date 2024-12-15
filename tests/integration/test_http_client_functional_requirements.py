import inspect
import logging
import uuid
from logging import LogRecord

import pytest
from requests import PreparedRequest, Response, Timeout, Session
from wiremock.resources.mappings import HttpMethods

import logging_http_client
from http_headers import X_REQUEST_ID_HEADER, X_SOURCE_HEADER, X_CORRELATION_ID_HEADER
from logging_http_client import HttpLogRecord


def test_client_returns_correct_response_details(wiremock_server):
    wiremock_server.for_endpoint("/ping", return_status=418, return_body='{ "message": "pong!" }')

    response = logging_http_client.create().get(
        url=wiremock_server.get_url("/ping"), headers={"accept": "application/json"}
    )

    assert response.status_code == 418
    assert response.content == b'{ "message": "pong!" }'
    assert response.headers["content-type"] == "application/json"


def test_client_should_raise_timeout_error_on_request_timeout(wiremock_server):
    wiremock_server.for_endpoint("/create", method=HttpMethods.POST, return_status=201, fixed_delay_ms=1500)

    with pytest.raises(Timeout):
        logging_http_client.create().post(
            url=wiremock_server.get_url("/create"),
            timeout=1,
        )


@pytest.mark.parametrize("http_method", [HttpMethods.GET, HttpMethods.POST, HttpMethods.PUT, HttpMethods.DELETE])
def test_client_does_not_raise_exception_for_expected_optional_arguments(wiremock_server, http_method):
    wiremock_server.for_endpoint("/create", method=http_method, return_status=201, return_body='{ "message": "done!" }')

    optional_arguments = {
        key: None
        for key in inspect.signature(Session.request).parameters.keys()
        if key not in ["self", "method", "url", "headers"]
    }

    request_func = getattr(logging_http_client.create(), http_method.lower())

    request_func(
        url=wiremock_server.get_url("/create"),
        headers={"accept": "application/json"},
        **optional_arguments,
    )


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
    logging_http_client.enable_request_body_logging(enable=True)
    logging_http_client.enable_response_body_logging(enable=True)

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
    if hasattr(request_log, "http"):
        assert request_log.http["request_method"] == "POST"
        assert request_log.http["request_headers"]["accept"] == "application/json"
        assert request_log.http["request_body"] == '"{ \\"key\\": \\"value\\" }"'
    else:
        pytest.fail("Request log does not contain 'http' record attribute")

    assert response_log.message == "RESPONSE"
    if hasattr(response_log, "http"):
        assert response_log.http["response_status"] == 201
        assert response_log.http["response_headers"]["Content-Type"] == "application/json"
        assert response_log.http["response_body"] == '{ "message": "done!" }'
    else:
        pytest.fail("Response log does not contain 'http' record attribute")


def test_client_should_log_with_logging_disabled(wiremock_server, caplog):
    logging_http_client.disable_request_logging(disabled=True)
    logging_http_client.disable_response_logging(disabled=True)

    wiremock_server.for_endpoint("/secret")

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/secret"),
        )

    relevant_logs = [record for record in caplog.records if record.message in ["REQUEST", "RESPONSE"]]

    assert len(relevant_logs) == 0, f"Expected 0 logs, found {len(relevant_logs)}"


def test_client_should_log_with_custom_request_logging_hook(wiremock_server, caplog):
    def custom_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
        logger.debug("Custom request logging for %s", request.url)

    logging_http_client.set_request_logging_hooks([custom_request_logging_hook])

    wiremock_server.for_endpoint("/custom")

    with caplog.at_level(logging.DEBUG):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/custom"),
        )

    relevant_logs = [record for record in caplog.records if "Custom request logging" in record.message]

    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log: LogRecord = relevant_logs.pop()

    assert request_log.message == "Custom request logging for " + wiremock_server.get_url("/custom")


def test_client_should_log_with_custom_response_logging_hook(wiremock_server, caplog):
    def custom_response_logging_hook(logger: logging.Logger, response: Response):
        logger.debug("Custom response logging for %s", response.url)

    logging_http_client.set_response_logging_hooks([custom_response_logging_hook])

    wiremock_server.for_endpoint("/custom")

    with caplog.at_level(logging.DEBUG):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/custom"),
        )

    relevant_logs = [record for record in caplog.records if "Custom response logging" in record.message]

    assert len(relevant_logs) == 1, f"Expected 1 response log, found {len(relevant_logs)}"

    response_log: LogRecord = relevant_logs.pop()

    assert response_log.message == "Custom response logging for " + wiremock_server.get_url("/custom")


def test_client_should_log_with_multiple_request_logging_hooks(wiremock_server, caplog):
    def first_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
        logger.debug("First request hook triggered for %s", request.url)

    def second_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
        logger.debug("Second request hook triggered for %s", request.url)

    logging_http_client.set_request_logging_hooks([first_request_logging_hook, second_request_logging_hook])

    wiremock_server.for_endpoint("/multiple_hooks")

    with caplog.at_level(logging.DEBUG):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/multiple_hooks"),
        )

    first_hook_logs = [record for record in caplog.records if "First request hook triggered" in record.message]
    second_hook_logs = [record for record in caplog.records if "Second request hook triggered" in record.message]

    assert len(first_hook_logs) == 1, f"Expected logs from first request hook, found {len(first_hook_logs)}"
    assert len(second_hook_logs) == 1, f"Expected logs from second request hook, found {len(second_hook_logs)}"
    assert wiremock_server.get_url("/multiple_hooks") in first_hook_logs[0].message
    assert wiremock_server.get_url("/multiple_hooks") in second_hook_logs[0].message


def test_client_should_log_with_multiple_response_logging_hooks(wiremock_server, caplog):
    def first_response_logging_hook(logger: logging.Logger, response: Response):
        logger.debug("First response hook triggered for %s with status %s", response.url, response.status_code)

    def second_response_logging_hook(logger: logging.Logger, response: Response):
        logger.debug("Second response hook triggered for %s with status %s", response.url, response.status_code)

    logging_http_client.set_response_logging_hooks([first_response_logging_hook, second_response_logging_hook])

    wiremock_server.for_endpoint("/multiple_hooks", return_status=202, return_body="test response")

    with caplog.at_level(logging.DEBUG):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/multiple_hooks"),
        )

    first_hook_logs = [record for record in caplog.records if "First response hook triggered" in record.message]
    second_hook_logs = [record for record in caplog.records if "Second response hook triggered" in record.message]

    assert len(first_hook_logs) == 1, f"Expected logs from first response hook, found {len(first_hook_logs)}"
    assert len(second_hook_logs) == 1, f"Expected logs from second response hook, found {len(second_hook_logs)}"
    assert wiremock_server.get_url("/multiple_hooks") in first_hook_logs[0].message
    assert "202" in first_hook_logs[0].message
    assert wiremock_server.get_url("/multiple_hooks") in second_hook_logs[0].message
    assert "202" in second_hook_logs[0].message


def test_client_should_obscure_request_details(wiremock_server, caplog):
    def request_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        record.request_method = "REDACTED"
        if record.request_headers.get("Authorization") is not None:
            record.request_headers["Authorization"] = "Bearer ****"
        return record

    logging_http_client.set_request_log_record_obscurers([request_log_record_obscurer])

    wiremock_server.for_endpoint("/secret")

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/secret"),
            headers={"accept": "application/json", "Authorization": "Bearer secret"},
        )

    relevant_logs = [record for record in caplog.records if record.message == "REQUEST"]

    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log: LogRecord = relevant_logs.pop()

    if hasattr(request_log, "http"):
        assert request_log.http["request_method"] == "REDACTED"
        assert request_log.http["request_headers"]["Authorization"] == "Bearer ****"
    else:
        pytest.fail("Request log does not contain 'http' record attribute")


def test_client_should_obscure_response_details(wiremock_server, caplog):
    def response_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        record.response_status = 999
        if record.response_body is not None:
            record.response_body = record.response_body.replace("SENSITIVE", "****")
        return record

    logging_http_client.set_response_log_record_obscurers([response_log_record_obscurer])
    logging_http_client.enable_response_body_logging()

    wiremock_server.for_endpoint(
        url="/secret", return_status=418, return_body="some response body with SENSITIVE information"
    )

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/secret"),
        )

    relevant_logs = [record for record in caplog.records if record.message == "RESPONSE"]

    assert len(relevant_logs) == 1, f"Expected 1 response log, found {len(relevant_logs)}"

    response_log: LogRecord = relevant_logs.pop()

    if hasattr(response_log, "http"):
        assert response_log.http["response_status"] == 999
        assert response_log.http["response_body"] == "some response body with **** information"
    else:
        pytest.fail("Response log does not contain 'http' record attribute")


def test_client_should_obscure_request_details_with_multiple_obscurers(wiremock_server, caplog):
    def first_request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        if record.request_headers.get("Authorization"):
            record.request_headers["Authorization"] = "Bearer ****"
        return record

    def second_request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        if record.request_body:
            record.request_body = "OBSCURED_BODY"
        return record

    logging_http_client.set_request_log_record_obscurers([first_request_obscurer, second_request_obscurer])
    logging_http_client.enable_request_body_logging(True)

    wiremock_server.for_endpoint("/secret")
    with caplog.at_level(logging.INFO):
        logging_http_client.create().post(
            url=wiremock_server.get_url("/secret"),
            headers={"accept": "application/json", "Authorization": "Bearer secret"},
            json={"sensitive": "data"},
        )

    relevant_logs = [record for record in caplog.records if record.message == "REQUEST"]
    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log = relevant_logs.pop()
    if hasattr(request_log, "http"):
        assert (
            request_log.http["request_headers"]["Authorization"] == "Bearer ****"
        ), "Expected the Authorization header to be obscured"
        assert request_log.http["request_body"] == "OBSCURED_BODY", "Expected the request body to be obscured"
    else:
        pytest.fail("Request log does not contain 'http' record attribute")


def test_client_should_obscure_response_details_with_multiple_obscurers(wiremock_server, caplog):
    def first_response_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        if record.response_body:
            record.response_body = record.response_body.replace("secret", "****")
        return record

    def second_response_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        record.response_status = 999
        return record

    logging_http_client.set_response_log_record_obscurers([first_response_obscurer, second_response_obscurer])
    logging_http_client.enable_response_body_logging(True)

    wiremock_server.for_endpoint("/classified", return_status=200, return_body="this is a secret message")

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/classified"),
        )

    relevant_logs = [record for record in caplog.records if record.message == "RESPONSE"]
    assert len(relevant_logs) == 1, f"Expected 1 response log, found {len(relevant_logs)}"

    response_log = relevant_logs.pop()
    if hasattr(response_log, "http"):
        assert response_log.http["response_status"] == 999, "Expected the response status to be changed to 999"
        assert (
            response_log.http["response_body"] == "this is a **** message"
        ), "Expected the response body to have secret obscured"
    else:
        pytest.fail("Response log does not contain 'http' record attribute")


def test_client_should_support_traceability(wiremock_server, caplog):
    def correlation_id_provider() -> str:
        return str(uuid.uuid4())

    logging_http_client.set_correlation_id_provider(correlation_id_provider)

    wiremock_server.for_endpoint("/traceable")

    with caplog.at_level(logging.INFO):
        logging_http_client.create().get(
            url=wiremock_server.get_url("/traceable"),
        )

    relevant_logs = [record for record in caplog.records if record.message in ["REQUEST"]]

    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log: LogRecord = relevant_logs.pop()

    if hasattr(request_log, "http"):
        reqeust_correlation_id = request_log.http["request_headers"][X_CORRELATION_ID_HEADER]
        assert isinstance(
            uuid.UUID(reqeust_correlation_id), uuid.UUID
        ), f"Expected request correlation id to be a valid UUID, but got {reqeust_correlation_id}"
    else:
        pytest.fail("Request log does not contain 'http' record attribute")


def test_client_should_run_obscurers_on_a_custom_hook_when_http_log_record_processor_is_used(wiremock_server, caplog):
    def custom_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
        logger.debug(
            "Custom request logging for %s",
            request.url,
            # IMPORTANT: Usage of this static method will automatically apply the obscurers for you.
            extra=HttpLogRecord.from_request(request),
        )

    def first_request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        if record.request_headers.get("Authorization"):
            record.request_headers["Authorization"] = "Bearer ****"
        return record

    def second_request_obscurer(record: HttpLogRecord) -> HttpLogRecord:
        if record.request_body:
            record.request_body = "OBSCURED_BODY"
        return record

    logging_http_client.enable_request_body_logging()
    logging_http_client.set_request_logging_hooks([custom_request_logging_hook])
    logging_http_client.set_request_log_record_obscurers([first_request_obscurer, second_request_obscurer])

    wiremock_server.for_endpoint("/secret")
    with caplog.at_level(logging.DEBUG):
        logging_http_client.create().post(
            url=wiremock_server.get_url("/secret"),
            headers={"accept": "application/json", "Authorization": "Bearer secret"},
            json={"sensitive": "data"},
        )

    relevant_logs = [record for record in caplog.records if "Custom request logging for" in record.message]
    assert len(relevant_logs) == 1, f"Expected 1 request log, found {len(relevant_logs)}"

    request_log = relevant_logs.pop()
    if hasattr(request_log, "http"):
        assert "OBSCURED_BODY" in request_log.http.get("request_body")
        assert "Bearer ****" in request_log.http.get("request_headers").get("Authorization")
    else:
        pytest.fail("Request log does not contain 'http' record attribute")
