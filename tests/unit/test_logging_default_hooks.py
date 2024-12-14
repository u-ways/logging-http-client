import logging

import pytest

import logging_http_client.logging_http_client_config_globals as config
from http_headers import X_SOURCE_HEADER, X_REQUEST_ID_HEADER
from logging_http_client import default_request_logging_hook, default_response_logging_hook
from logging_http_client.logging_http_client_config import (
    set_default_hooks_logging_level,
)


# Tests for defaults =======================================================================================


def test_default_request_logging_hooks_are_empty():
    hooks = config.get_request_logging_hooks()
    assert isinstance(hooks, list)
    assert len(hooks) == 1
    assert hooks[0].__name__ == default_request_logging_hook.__name__


def test_default_response_logging_hooks_are_empty():
    hooks = config.get_response_logging_hooks()
    assert isinstance(hooks, list)
    assert len(hooks) == 1
    assert hooks[0].__name__ == default_response_logging_hook.__name__


def test_default_log_level_should_be_info():
    assert config.get_default_hooks_logging_level() == logging.INFO


# Tests for default hook log level setting =================================================================


def test_set_logging_level_for_default_hooks():
    set_default_hooks_logging_level(logging.DEBUG)
    assert config.get_default_hooks_logging_level() == logging.DEBUG


def test_reset_logging_level_for_default_hooks():
    set_default_hooks_logging_level(logging.DEBUG)
    set_default_hooks_logging_level(logging.INFO)
    assert config.get_default_hooks_logging_level() == logging.INFO


# Tests for default hook functionality =====================================================================


@pytest.mark.parametrize("log_level", [logging.INFO, logging.DEBUG, logging.WARNING])
def test_default_request_logging_hook(mocker, log_level):
    logger = mocker.Mock()
    request = mocker.Mock(
        headers={
            X_SOURCE_HEADER: "source",
            X_REQUEST_ID_HEADER: "request_id",
        },
    )

    set_default_hooks_logging_level(log_level)
    default_request_logging_hook(logger, request)

    logger.log.assert_called_once_with(
        level=log_level,
        msg="REQUEST",
        extra=mocker.ANY,
    )


@pytest.mark.parametrize("log_level", [logging.ERROR, logging.CRITICAL])
def test_default_request_logging_hook_with_no_headers(mocker, log_level):
    logger = mocker.Mock()
    request = mocker.Mock(
        headers={},
    )

    set_default_hooks_logging_level(log_level)
    default_request_logging_hook(logger, request)

    logger.log.assert_called_once_with(
        level=log_level,
        msg="REQUEST",
        extra=mocker.ANY,
    )
