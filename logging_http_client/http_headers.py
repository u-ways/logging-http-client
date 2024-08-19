HEADERS_KWARG = "headers"

X_SOURCE_HEADER = "x-source"
X_REQUEST_ID_HEADER = "x-request-id"


def with_source_header(value: str) -> dict:
    return {X_SOURCE_HEADER: value}
