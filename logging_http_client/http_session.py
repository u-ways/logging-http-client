import inspect
import uuid
from functools import wraps
from logging import Logger
from typing import KeysView

from requests import Session, Response, Request, PreparedRequest

import logging_http_client.logging_http_client_config_globals as config
from logging_http_client.http_headers import (
    X_SOURCE_HEADER,
    X_REQUEST_ID_HEADER,
    HEADERS_KWARG,
    X_CORRELATION_ID_HEADER,
)
from logging_http_client.http_log_record import HttpLogRecord


class LoggingSession(Session):
    """
    A subclass of requests.Session that logs the request and response details.
    """

    REQUEST_CLASS_PARAMS: KeysView[str] = inspect.signature(Request).parameters.keys()

    def __init__(self, source: str, logger: Logger) -> None:
        super().__init__()

        methods_to_decorate = [
            self.request,
            self.get,
            self.post,
            self.put,
            self.delete,
            self.patch,
            self.head,
            self.options,
        ]

        for method in methods_to_decorate:
            method_name = method.__name__
            decorated_method = self.decorate(source, logger, method)
            setattr(self, method_name, decorated_method)

    def decorate(self, source: str, logger: Logger, original_method: callable) -> callable:
        @wraps(original_method)
        def _apply(**kwargs) -> Response:
            request_object_kwargs = {k: v for k, v in kwargs.items() if k in self.REQUEST_CLASS_PARAMS}
            req = Request(**request_object_kwargs)
            prepared: PreparedRequest = self.prepare_request(req)
            request_id = prepared.headers.get(X_REQUEST_ID_HEADER, None)
            correlation_id = prepared.headers.get(X_CORRELATION_ID_HEADER, None)
            source_system = prepared.headers.get(X_SOURCE_HEADER, None)

            kwargs.setdefault(HEADERS_KWARG, {})

            if request_id is None:
                kwargs[HEADERS_KWARG][X_REQUEST_ID_HEADER] = str(uuid.uuid4())
                request_id = kwargs[HEADERS_KWARG][X_REQUEST_ID_HEADER]
                prepared.headers.update({X_REQUEST_ID_HEADER: request_id})

            correlation_id_provider = config.get_correlation_id_provider()
            if correlation_id is None and correlation_id_provider is not None:
                kwargs[HEADERS_KWARG][X_CORRELATION_ID_HEADER] = correlation_id_provider()
                correlation_id = kwargs[HEADERS_KWARG][X_CORRELATION_ID_HEADER]
                prepared.headers.update({X_CORRELATION_ID_HEADER: correlation_id})

            if source_system is None:
                kwargs[HEADERS_KWARG][X_SOURCE_HEADER] = source
                source_system = kwargs[HEADERS_KWARG][X_SOURCE_HEADER]
                prepared.headers.update({X_SOURCE_HEADER: source_system})

            request_logging_hook = config.get_custom_request_logging_hook()
            if request_logging_hook is not None:
                request_logging_hook(logger, prepared)
            else:
                if config.is_request_logging_enabled():
                    logger.info(
                        msg="REQUEST",
                        extra=HttpLogRecord.request_processor(
                            source_system=source_system, request_id=request_id, request=prepared
                        ),
                    )

            # Call the original method... (with modified **kwargs)
            response: Response = original_method(**kwargs)

            response_logging_hook = config.get_custom_response_logging_hook()
            if response_logging_hook is not None:
                response_logging_hook(logger, response)
            else:
                if config.is_response_logging_enabled():
                    logger.info(
                        msg="RESPONSE", extra=HttpLogRecord.response_processor(request_id=request_id, response=response)
                    )

            return response

        return _apply
