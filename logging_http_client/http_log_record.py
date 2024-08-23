from dataclasses import dataclass, asdict
from typing import Any, Dict, Union

from requests.models import PreparedRequest, Response

from logging_http_client_config_globals import (
    is_request_body_logging_enabled,
    is_response_body_logging_enabled,
    get_request_log_record_obscurer,
    get_response_log_record_obscurer,
)

# Define Primitive type
Primitive = Union[int, float, str, bool]


@dataclass
class BaseLogRecord:
    """
    A base class for all custom log record extensions.
    """

    def to_dict(self) -> Dict[str, Primitive]:
        # Clean dictionary, removing empty and default values
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
    def request_processor(source_system: str, request_id: str, request: PreparedRequest) -> Dict[str, Any]:
        record = HttpLogRecord()

        record.request_id = request_id
        record.request_source = source_system
        record.request_method = request.method
        record.request_url = request.url
        record.request_query_params = request.params if hasattr(request, "params") else {}
        record.request_headers = dict(request.headers) if request.headers else {}

        if request.body and is_request_body_logging_enabled():
            if isinstance(request.body, bytes):
                record.request_body = request.body.decode()
            else:
                record.request_body = request.body

        obscurer = get_request_log_record_obscurer()
        record = obscurer(record) if obscurer is not None else record

        return {"http": record.to_dict()}

    @staticmethod
    def response_processor(request_id: str, response: Response) -> Dict[str, Any]:
        record = HttpLogRecord()

        record.request_id = request_id
        record.response_status = response.status_code
        record.response_headers = dict(response.headers) if response.headers else {}
        record.response_duration_ms = int(response.elapsed.microseconds // 1000)

        if response.content and is_response_body_logging_enabled():
            record.response_body = response.content.decode()

        obscurer = get_response_log_record_obscurer()
        record = obscurer(record) if obscurer is not None else record

        return {"http": record.to_dict()}
