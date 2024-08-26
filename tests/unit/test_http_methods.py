import pytest

from logging_http_client.http_methods import HttpMethod


@pytest.mark.parametrize(
    "http_method, expected_value",
    [
        (HttpMethod.GET, "GET"),
        (HttpMethod.POST, "POST"),
        (HttpMethod.PUT, "PUT"),
        (HttpMethod.DELETE, "DELETE"),
        (HttpMethod.PATCH, "PATCH"),
        (HttpMethod.HEAD, "HEAD"),
        (HttpMethod.OPTIONS, "OPTIONS"),
    ],
)
def test_http_method_values_has_no_typos(http_method, expected_value):
    assert http_method.value == expected_value
