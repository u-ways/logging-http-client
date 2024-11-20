# Obscuring Sensitive Data

The library provides a way to obscure sensitive data in the request or response log records. This is useful when you
want to log the request or response body but want to obscure sensitive data such as passwords, tokens, etc.

## 1. Request Log Record Obscurer

You can set a request log record obscurer by calling the `set_request_log_record_obscurer` method. The obscurer
function should take a `HttpLogRecord` object and expects to return a modified `HttpLogRecord` object. The obscurer
function will be called JUST BEFORE the request is logged.

```python
import logging_http_client
from logging_http_client import HttpLogRecord


def request_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.request_method = "REDACTED"
    if record.request_headers.get("Authorization") is not None:
        record.request_headers["Authorization"] = "****"
    return record


logging_http_client.set_request_log_record_obscurer(request_log_record_obscurer)

logging_http_client.create().get(
    url='https://www.python.org',
    headers={"Authorization": "Bearer SOME-SECRET-TOKEN"}
)

# => Log record will include:
#    { http { request_headers: { "Authorization ": "****", ... }, ... } }
```

## 2. Response Log Record Obscurer

Likewise, you can set a response log record obscurer by calling the `set_response_log_record_obscurer` method.
The obscurer function should take a `HttpLogRecord` object and expects to return a modified `HttpLogRecord` object.

```python
import logging_http_client
from logging_http_client import HttpLogRecord


def response_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.response_status = 999
    if record.response_body is not None:
        record.response_body = record.response_body.replace("SENSITIVE", "****")
    return record


logging_http_client.set_response_log_record_obscurer(response_log_record_obscurer)
logging_http_client.enable_response_body_logging()

logging_http_client.create().get('https://www.python.org')
# Assume the response body contains "some response body with SENSITIVE information" 

# => Log record will include:
#    { http { response_status: 999, response_body: "some response body with **** information", ... } }
```