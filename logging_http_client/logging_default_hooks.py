from __future__ import annotations

import logging

from requests import PreparedRequest, Response

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.http_headers import X_SOURCE_HEADER, X_REQUEST_ID_HEADER
from logging_http_client.http_log_record import HttpLogRecord


def default_request_logging_hook(logger: logging.Logger, request: PreparedRequest) -> None:
    logging_level = config.get_default_hooks_logging_level()

    source_system = request.headers.get(X_SOURCE_HEADER, None)
    request_id = request.headers.get(X_REQUEST_ID_HEADER, None)

    logger.log(
        level=logging_level,
        msg="REQUEST",
        extra=HttpLogRecord.request_processor(source_system=source_system, request_id=request_id, request=request),
    )


def default_response_logging_hook(logger: logging.Logger, response: Response) -> None:
    logging_level = config.get_default_hooks_logging_level()

    request_id = response.request.headers.get(X_REQUEST_ID_HEADER, None)

    logger.log(
        level=logging_level,
        msg="RESPONSE",
        extra=HttpLogRecord.response_processor(request_id=request_id, response=response),
    )
