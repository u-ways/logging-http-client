import pytest

import logging_http_client.logging_http_client_config_globals as config
from http_session import LoggingSession
from logging_http_client.logging_http_client_config import (
    disable_request_logging,
    disable_response_logging,
)


@pytest.mark.parametrize("switch", [True, False])
def test_enable_request_logging(switch):
    disable_request_logging(switch)
    assert config.is_request_logging_enabled() == (not switch)


@pytest.mark.parametrize("switch", [True, False])
def test_enable_response_logging(switch):
    disable_response_logging(switch)
    assert config.is_response_logging_enabled() == (not switch)


def test_disabled_request_logging_hooks(mocker):
    def failing_request_hook(_, __) -> None:
        pytest.fail("Hook should NOT be called")

    config.set_request_logging_hooks([failing_request_hook])
    config.set_request_logging_enabled(False)

    logging_session = LoggingSession("TEST", mocker.Mock())
    logging_session._run_logging_request_hooks(mocker.Mock())


def test_enabled_request_logging_hooks(mocker):
    hook_has_been_called = False

    def successful_request_hook(_, __) -> None:
        nonlocal hook_has_been_called
        hook_has_been_called = True

    config.set_request_logging_hooks([successful_request_hook])
    config.set_request_logging_enabled(True)

    logging_session = LoggingSession("TEST", mocker.Mock())
    logging_session._run_logging_request_hooks(mocker.Mock())

    assert hook_has_been_called


def test_disabled_response_logging_hooks(mocker):
    def failing_response_hook(_, __) -> None:
        pytest.fail("Hook should NOT be called")

    config.set_response_logging_hooks([failing_response_hook])
    config.set_response_logging_enabled(False)

    logging_session = LoggingSession("TEST", mocker.Mock())
    logging_session._run_logging_response_hooks(mocker.Mock())


def test_enabled_response_logging_hooks(mocker):
    hook_has_been_called = False

    def successful_response_hook(_, __) -> None:
        nonlocal hook_has_been_called
        hook_has_been_called = True

    config.set_response_logging_hooks([successful_response_hook])
    config.set_response_logging_enabled(True)

    logging_session = LoggingSession("TEST", mocker.Mock())
    logging_session._run_logging_response_hooks(mocker.Mock())

    assert hook_has_been_called
