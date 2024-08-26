import pytest

from logging_http_client.logging_http_client_config import (
    disable_request_logging,
    enable_request_body_logging,
    disable_response_logging,
    enable_response_body_logging,
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
