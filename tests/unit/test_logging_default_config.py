import pytest

from logging_http_client.logging_http_client_config import (
    disable_request_logging,
    enable_request_body_logging,
    disable_response_logging,
    enable_response_body_logging,
    set_logging_level,
)
import logging_http_client.logging_http_client_config_globals as config

level_map = {"INFO": 20, "DEBUG": 10, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


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


@pytest.mark.parametrize("switch", [10, 20, 30, 40, 50])
def test_set_logging_level(switch):
    set_logging_level(switch)
    assert config.get_logging_level() == switch


@pytest.mark.parametrize("switch", ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"])
def test_set_logging_level_string(switch):
    set_logging_level(switch)
    assert config.get_logging_level() == level_map[switch]


@pytest.mark.parametrize("switch", ["INVALID", "INFODEBUG", 60, 11, 35, 45, 11010210120201, None])
def test_set_logging_level_edgecases(switch):
    set_logging_level(switch) == 20
    assert config.get_logging_level() == 20
