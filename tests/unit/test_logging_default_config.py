import pytest

from logging_http_client.logging_http_client_config import (
    disable_request_logging,
    enable_request_body_logging,
    disable_response_logging,
    enable_response_body_logging,
    set_logging_level,
    LogLevel,
)
import logging_http_client.logging_http_client_config_globals as config


@pytest.mark.parametrize("switch", [True, False])
def test_enable_request_logging(switch):
    disable_request_logging(switch)
    assert config.is_request_logging_enabled() == (not switch)


@pytest.mark.parametrize("switch", [True, False])
def test_enable_request_body_logging(switch):
    enable_request_body_logging(switch)
    assert config.is_request_body_logging_enabled() == switch


@pytest.mark.parametrize("switch", [True, False])
def test_enable_response_logging(switch):
    disable_response_logging(switch)
    assert config.is_response_logging_enabled() == (not switch)


@pytest.mark.parametrize("switch", [True, False])
def test_enable_response_body_logging(switch):
    enable_response_body_logging(switch)
    assert config.is_response_body_logging_enabled() == switch


@pytest.mark.parametrize("switch", [LogLevel.INFO, LogLevel.DEBUG, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL])
def test_set_logging_level_enum(switch):
    set_logging_level(switch)
    assert config.get_logging_level() == switch.value


@pytest.mark.parametrize("switch", [10, 20, 30, 40, 50])
def test_set_logging_level_int(switch):
    set_logging_level(switch)
    assert config.get_logging_level() == 20


@pytest.mark.parametrize("switch", ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"])
def test_set_logging_level_string(switch):
    set_logging_level(switch)
    assert config.get_logging_level() == 20


@pytest.mark.parametrize("switch", ["INVALID", "INFODEBUG", 60, 11, 35, 45, 11010210120201, None])
def test_set_logging_level_edgecases(switch):
    set_logging_level(switch) == 20
    assert config.get_logging_level() == 20
