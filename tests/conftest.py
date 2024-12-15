import logging

import pytest

import logging_http_client_config
from logging_default_hooks import default_response_logging_hook, default_request_logging_hook


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_logger_after_each_test():
    """
    Fixture to clean up the "test" logger after each test.

    As I keep creating a new logger named "test" in each test,
    I need to clean it up after each test to avoid memory leaks
    or undesired side effects.
    """
    yield

    logger_name = "test"
    if logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        del logging.Logger.manager.loggerDict[logger_name]


@pytest.fixture(scope="function", autouse=True)
def reset_library_globals_after_each_test():
    """
    Fixture to clean up the global context and processors in the ContextualLogger after each test.

    As I keep modifying the global (static) context and processors in the ContextualLogger in each
    test, I need to clean them up after each test to avoid memory leaks or undesired side effects.
    """
    logging_http_client_config.set_correlation_id_provider(None)

    logging_http_client_config.set_request_log_record_obscurers([])
    logging_http_client_config.set_response_log_record_obscurers([])

    logging_http_client_config.set_default_hooks_logging_level(logging.INFO)

    logging_http_client_config.set_request_logging_hooks([default_request_logging_hook])
    logging_http_client_config.set_response_logging_hooks([default_response_logging_hook])

    logging_http_client_config.disable_request_logging(False)
    logging_http_client_config.disable_response_logging(False)

    logging_http_client_config.enable_request_body_logging(False)
    logging_http_client_config.enable_response_body_logging(False)
