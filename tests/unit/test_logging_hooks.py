import pytest
from requests import Response, PreparedRequest

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.logging_http_client_config import (
    set_custom_request_logging_hook,
    set_custom_response_logging_hook,
    set_request_logging_hooks,
    set_response_logging_hooks,
)


def request_hook(_, request: PreparedRequest) -> None:
    print(f"Request method: {request.method}")


def another_request_hook(_, request: PreparedRequest) -> None:
    print(f"Another request method: {request.method}")


def response_hook(_, response: Response) -> None:
    print(f"Response status code: {response.status_code}")


def another_response_hook(_, response: Response) -> None:
    print(f"Another response status code: {response.status_code}")


# Tests for setting hooks ==================================================================================


def test_set_request_logging_hooks():
    set_request_logging_hooks([request_hook, another_request_hook])
    hooks = config.get_request_logging_hooks()
    assert hooks == [request_hook, another_request_hook]


def test_set_response_logging_hooks():
    set_response_logging_hooks([response_hook, another_response_hook])
    hooks = config.get_response_logging_hooks()
    assert hooks == [response_hook, another_response_hook]


def test_reset_request_logging_hooks():
    set_request_logging_hooks([request_hook])
    set_request_logging_hooks([])
    hooks = config.get_request_logging_hooks()
    assert hooks == []


def test_reset_response_logging_hooks():
    set_response_logging_hooks([response_hook])
    set_response_logging_hooks([])
    hooks = config.get_response_logging_hooks()
    assert hooks == []


# Tests for hook functionality ==============================================================================


def test_request_logging_hooks_functionality(capsys):
    set_request_logging_hooks([request_hook, another_request_hook])
    request = PreparedRequest()
    request.method = "GET"

    for hook in config.get_request_logging_hooks():
        hook(None, request)

    captured = capsys.readouterr()
    assert "Request method: GET" in captured.out
    assert "Another request method: GET" in captured.out


def test_response_logging_hooks_functionality(capsys):
    set_response_logging_hooks([response_hook, another_response_hook])
    response = Response()
    response.status_code = 200

    for hook in config.get_response_logging_hooks():
        hook(None, response)

    captured = capsys.readouterr()
    assert "Response status code: 200" in captured.out
    assert "Another response status code: 200" in captured.out


# DEPRECATED FUNCTIONS TESTS ==========================================================================================


def test_set_custom_request_logging_hook_deprecated():
    with pytest.warns(DeprecationWarning, match="set_custom_request_logging_hook is deprecated"):
        set_custom_request_logging_hook(request_hook)
    # Check that a single hook is set as a list
    hooks = config.get_request_logging_hooks()
    assert hooks == [request_hook]


def test_set_custom_response_logging_hook_deprecated():
    with pytest.warns(DeprecationWarning, match="set_custom_response_logging_hook is deprecated"):
        set_custom_response_logging_hook(response_hook)
    # Check that a single hook is set as a list
    hooks = config.get_response_logging_hooks()
    assert hooks == [response_hook]
