import pytest

import logging_http_client as requests


@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch", "head", "options"])
def test_single_use_session_methods(wiremock_server, method):
    wiremock_server.for_endpoint("/smoke", method=method.upper())
    response = getattr(requests, method)(wiremock_server.get_url("/smoke"))
    assert response.status_code == 200


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def test_reusable_session_client(wiremock_server, method):
    wiremock_server.for_endpoint("/smoke", method=method)
    client = requests.create(reusable_session=True)
    response = getattr(client, method)(wiremock_server.get_url("/smoke"))
    assert response.status_code == 200
