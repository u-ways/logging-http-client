import pytest
from requests import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict

from logging_http_client.http_log_record import HttpLogRecord


def given_request(
    method="GET",
    url="http://example.com/api",
    headers=None,
    body=None,
    params=None,
):
    request = PreparedRequest()
    request.method = method
    request.url = url
    request.headers = CaseInsensitiveDict(headers or {})
    request.body = body
    request.params = params
    return request


def given_response(
    status_code=200,
    content=b"",
    headers=None,
    request=given_request(),
    elapsed_microseconds=0,
):
    response = Response()
    response.status_code = status_code
    response._content = content
    response.elapsed = type("Elapsed", (object,), {"microseconds": elapsed_microseconds})()
    response.headers = CaseInsensitiveDict(headers or {})
    response.request = request or given_request()
    return response


# from_request ====================================================================================


def test_from_request_processor_with_body_logging_disabled(mocker):
    request = given_request(body="This should not be logged")

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_request_body_logging_enabled", return_value=False
    )

    result = HttpLogRecord.from_request(request)["http"]
    assert "request_body" not in result


def test_from_request_with_request_body_logging_enabled(mocker):
    request = given_request(
        body="This should be logged",
    )

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_request_body_logging_enabled", return_value=True
    )

    result = HttpLogRecord.from_request(request)["http"]
    assert result["request_body"] == "This should be logged"


def test_from_request_with_complete_request(mocker):
    request = given_request(
        method="POST",
        url="http://example.com/api",
        headers={"X-Request-Id": "req-005", "X-Source": "Test"},
        body="This should be logged",
        params={"param1": "value1"},
    )

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_request_body_logging_enabled", return_value=True
    )

    result = HttpLogRecord.from_request(request)["http"]
    expected = {
        "request_id": "req-005",
        "request_source": "Test",
        "request_method": "POST",
        "request_url": "http://example.com/api",
        "request_headers": {"X-Request-Id": "req-005", "X-Source": "Test"},
        "request_body": "This should be logged",
        "request_query_params": {"param1": "value1"},
    }
    assert result == expected


# Tests for from_response ===================================================================================


def test_from_response_with_body_logging_disabled(mocker):
    response = given_response(content=b"This should not be logged")

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_response_body_logging_enabled",
        return_value=False,
    )

    result = HttpLogRecord.from_response(response)["http"]
    assert "response_body" not in result


def test_from_response_with_body_logging_enabled(mocker):
    response = given_response(content=b"This should be logged")

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_response_body_logging_enabled",
        return_value=True,
    )

    result = HttpLogRecord.from_response(response)["http"]
    assert result["response_body"] == "This should be logged"


def test_from_response_with_complete_response(mocker):
    request = given_request(
        method="POST",
        url="http://example.com/api",
        headers={"X-Request-Id": "req-005", "X-Source": "Test"},
        body="This is the request body",
    )

    response = given_response(
        status_code=201,
        content=b"Response body here",
        headers={"Content-Type": "application/json", "X-Source": "ResponseSource"},
        request=request,
        elapsed_microseconds=125000,  # 125 ms
    )

    mocker.patch(
        "logging_http_client.logging_http_client_config_globals.is_response_body_logging_enabled",
        return_value=True,
    )

    result = HttpLogRecord.from_response(response)["http"]
    expected = {
        "request_id": "req-005",
        "response_source": "ResponseSource",
        "response_status": 201,
        "response_headers": {"Content-Type": "application/json", "X-Source": "ResponseSource"},
        "response_duration_ms": 125,
        "response_body": "Response body here",
    }

    assert result == expected


@pytest.mark.parametrize(
    "response_url, expected_response_source",
    [
        ("https://test.com/api/resource", "test.com"),
        ("https://test.com:8080/api/resource", "test.com:8080"),
    ],
)
def test_from_response_without_source_header_should_fallback_to_request_url_host_value(
    response_url, expected_response_source
):
    response = given_response(
        headers={},  # No X-Source header
        request=(given_request(url=response_url)),
    )

    result = HttpLogRecord.from_response(response)["http"]
    assert result["response_source"] == expected_response_source
