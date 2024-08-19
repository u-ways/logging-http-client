import pytest
from wiremock.client import Mappings, Mapping, MappingRequest, MappingResponse, HttpMethods
from wiremock.constants import Config
from wiremock.testing.testcontainer import wiremock_container


@pytest.fixture(scope="session")
def wiremock_server():
    with wiremock_container(secure=False) as server:
        # Configure the base URL for the WireMock server
        Config.base_url = server.get_url("__admin")

        # Add a method to the wm object for adding mappings
        def for_endpoint(
            url, method=HttpMethods.GET, return_status=200, return_body="", headers=None, persistent=False
        ):
            headers = headers or {"content-type": "application/json"}
            Mappings.create_mapping(
                Mapping(
                    request=MappingRequest(method=method, url=url),
                    response=MappingResponse(status=return_status, body=return_body, headers=headers),
                    persistent=persistent,
                )
            )

        # Attach the method to the wm instance
        server.for_endpoint = for_endpoint

        yield server
