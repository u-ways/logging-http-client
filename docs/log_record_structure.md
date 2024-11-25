# Log Record Structure

The library logs HTTP requests and responses as structured log records. The log records are structured as JSON
object passed to the logger's `extra` keyword argument. The log records are structured as follows:

```json
{
  "http": {
    "request_id": "<uuid>",
    "request_source": "<source>",
    "request_method": "<method>",
    "request_url": "<url>",
    "request_query_params": "<query_params>",
    "request_headers": "<headers>",
    "request_body": "<body>",
    "response_status": "<status>",
    "response_headers": "<headers>",
    "response_duration_ms": "<duration>",
    "response_body": "<body>"
  }
}
```

If any of those top-level fields are `None`, `{}`, `[]`, `""`, `0`, or `0.0`,
they will be omitted from the log record for brevity purposes.

The actual data class used to represent the log record is `HttpLogRecord` and is available in the `logging_http_client`.