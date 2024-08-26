import time

from logging_http_client.http_headers import with_source_header


def test_with_source_header():
    # Given
    source = f"test-{int(time.time())}"

    # When
    result = with_source_header(source)

    # Then
    assert {"x-source": source} == result
