from __future__ import annotations

import logging

from requests import PreparedRequest, Response

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.http_log_record import HttpLogRecord


def default_request_logging_hook(logger: logging.Logger, request: PreparedRequest) -> None:
    logger.log(
        level=config.get_default_hooks_logging_level(),
        msg="REQUEST",
        extra=HttpLogRecord.from_request(request),
    )


def default_response_logging_hook(logger: logging.Logger, response: Response) -> None:
    logger.log(
        level=config.get_default_hooks_logging_level(),
        msg="RESPONSE",
        extra=HttpLogRecord.from_response(response),
    )
