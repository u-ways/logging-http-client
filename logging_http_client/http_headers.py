HEADERS_KWARG = "headers"

X_SOURCE_HEADER = "x-source"
X_REQUEST_ID_HEADER = "x-request-id"
X_CORRELATION_ID_HEADER = "x-correlation-id"


def with_source_header(value: str) -> dict:
    return {X_SOURCE_HEADER: value}
