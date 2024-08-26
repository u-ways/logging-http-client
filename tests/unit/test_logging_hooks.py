from requests import Response, PreparedRequest

from logging_http_client.logging_http_client_config import (
    set_custom_request_logging_hook,
    set_custom_response_logging_hook,
)
import logging_http_client.logging_http_client_config_globals as config


def mock_request_hook(_, request: PreparedRequest) -> None:
    print(f"Request method: {request.method}")


def mock_response_hook(_, response: Response) -> None:
    print(f"Response status code: {response.status_code}")


# Global Getters and Setters Smoke Tests ======================================


def test_default_request_logging_hook_is_none():
    assert config.get_custom_request_logging_hook() is None


def test_default_response_logging_hook_is_none():
    assert config.get_custom_response_logging_hook() is None


def test_set_custom_request_logging_hook():
    set_custom_request_logging_hook(mock_request_hook)
    assert config.get_custom_request_logging_hook() is mock_request_hook


def test_set_custom_response_logging_hook():
    set_custom_response_logging_hook(mock_response_hook)
    assert config.get_custom_response_logging_hook() is mock_response_hook


def test_reset_request_logging_hook():
    set_custom_request_logging_hook(mock_request_hook)
    set_custom_request_logging_hook(None)
    assert config.get_custom_request_logging_hook() is None


def test_reset_response_logging_hook():
    set_custom_response_logging_hook(mock_response_hook)
    set_custom_response_logging_hook(None)
    assert config.get_custom_response_logging_hook() is None


# Functionality Tests =========================================================


def test_request_logging_hook_functionality(capsys):
    set_custom_request_logging_hook(mock_request_hook)

    request = PreparedRequest()
    request.method = "GET"

    hook = config.get_custom_request_logging_hook()
    hook(None, request)

    captured = capsys.readouterr()
    assert "Request method: GET" in captured.out


def test_response_logging_hook_functionality(capsys):
    set_custom_response_logging_hook(mock_response_hook)

    response = Response()
    response.status_code = 200

    hook = config.get_custom_response_logging_hook()
    hook(None, response)

    captured = capsys.readouterr()
    assert "Response status code: 200" in captured.out
