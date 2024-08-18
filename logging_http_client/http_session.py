import uuid
from functools import wraps
from logging import Logger

from requests import Session, Response, Request, PreparedRequest

from http_log_record import HttpLogRecord
from logging_default_config import default_logging_with_request, default_logging_with_response
from logging_hooks import request_logging_hook, response_logging_hook


class LoggingSession(Session):
    """
    A subclass of requests.Session that logs the request and response details.
    """

    def __init__(self, logger: Logger) -> None:
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
            decorated_method = self.decorate(logger, method)
            setattr(self, method_name, decorated_method)

    def decorate(self, logger: Logger, original_method: callable) -> callable:
        @wraps(original_method)
        def _apply(**kwargs) -> Response:
            prepared: PreparedRequest = self.prepare_request(Request(**kwargs))
            request_id = prepared.headers.get("x-request-id", None)

            if request_id is None:
                kwargs.setdefault("headers", {})
                kwargs["headers"]["x-request-id"] = str(uuid.uuid4())
                request_id = kwargs["headers"]["x-request-id"]

            if request_logging_hook:
                request_logging_hook(prepared)
            else:
                if default_logging_with_request:
                    logger.info(
                        msg="REQUEST", extra=HttpLogRecord.request_processor(request_id=request_id, request=prepared)
                    )

            response: Response = original_method(**kwargs)
            if response_logging_hook:
                response_logging_hook(response)
            else:
                if default_logging_with_response:
                    logger.info(
                        msg="RESPONSE", extra=HttpLogRecord.response_processor(request_id=request_id, response=response)
                    )

            return response

        return _apply
