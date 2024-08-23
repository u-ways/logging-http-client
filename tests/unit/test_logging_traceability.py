import time

from logging_http_client_config_globals import get_correlation_id_provider, set_correlation_id_provider

MOCK_CORRELATION_ID = f"test-correlation-id-{time.time()}"


def mock_correlation_id_provider() -> str:
    return MOCK_CORRELATION_ID


# Global Getters and Setters Smoke Tests ======================================


def test_default_correlation_id_provider_is_none():
    assert get_correlation_id_provider() is None


def test_set_correlation_id_provider():
    set_correlation_id_provider(mock_correlation_id_provider)
    assert get_correlation_id_provider() is mock_correlation_id_provider


def test_reset_correlation_id_provider():
    set_correlation_id_provider(mock_correlation_id_provider)
    set_correlation_id_provider(None)
    assert get_correlation_id_provider() is None


# Functionality Tests =========================================================


def test_correlation_id_provider_functionality():
    set_correlation_id_provider(mock_correlation_id_provider)

    provider = get_correlation_id_provider()
    assert provider is not None  # Ensure provider is set
    assert provider() == MOCK_CORRELATION_ID  # Check the return value from provider
