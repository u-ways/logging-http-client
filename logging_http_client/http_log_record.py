from dataclasses import dataclass, asdict
from typing import Any, Dict, Union

from requests.models import PreparedRequest, Response

import logging_http_client.logging_http_client_config_globals as config
from http_headers import X_SOURCE_HEADER, X_REQUEST_ID_HEADER

# Define Primitive type
Primitive = Union[int, float, str, bool]


@dataclass
class BaseLogRecord:
    """
    A base class for all custom log record extensions.
    """

    def to_dict(self) -> Dict[str, Primitive]:
        # Clean dictionary, removing empty and default values
        # noinspection PyTypeChecker
        to_dict_cleaned = {k: v for k, v in asdict(self).items() if v not in (None, {}, [], "", 0, 0.0)}
        return to_dict_cleaned


@dataclass
class HttpLogRecord(BaseLogRecord):
    request_id: str = ""
    request_source: str = "UNKNOWN"
    request_method: str = ""
    request_url: str = ""
    request_query_params: Dict[str, Any] = None
    request_headers: Dict[str, Any] = None
    request_body: str = ""
    response_status: int = 0
    response_headers: Dict[str, Any] = None
    response_duration_ms: int = 0
    response_body: str = ""

    @staticmethod
    def from_request(request: PreparedRequest) -> Dict[str, Any]:
        record = HttpLogRecord()

        record.request_id = request.headers.get(X_REQUEST_ID_HEADER, None)
        record.request_source = request.headers.get(X_SOURCE_HEADER, None)
        record.request_method = request.method
        record.request_url = request.url
        record.request_query_params = request.params if hasattr(request, "params") else {}
        record.request_headers = dict(request.headers) if request.headers else {}

        if request.body and config.is_request_body_logging_enabled():
            if isinstance(request.body, bytes):
                record.request_body = request.body.decode()
            else:
                record.request_body = request.body

        for obscurer in config.get_request_log_record_obscurers():
            record = obscurer(record)

        return {"http": record.to_dict()}

    @staticmethod
    def from_response(response: Response) -> Dict[str, Any]:
        record = HttpLogRecord()

        record.request_id = response.request.headers.get(X_REQUEST_ID_HEADER, None)
        record.response_status = response.status_code
        record.response_headers = dict(response.headers) if response.headers else {}
        record.response_duration_ms = int(response.elapsed.microseconds // 1000)

        if response.content and config.is_response_body_logging_enabled():
            record.response_body = response.content.decode()

        for obscurer in config.get_response_log_record_obscurers():
            record = obscurer(record)

        return {"http": record.to_dict()}
