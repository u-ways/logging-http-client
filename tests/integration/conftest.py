import pytest
from wiremock.client import Mappings, Mapping, MappingRequest, MappingResponse, HttpMethods
from wiremock.constants import Config
from wiremock.testing.testcontainer import wiremock_container


@pytest.fixture(scope="session")
def wiremock_server():
    with wiremock_container(secure=False) as server:
        Config.base_url = server.get_url("__admin")

        def for_endpoint(
            url,
            method=HttpMethods.GET,
            return_status=200,
            return_body="",
            headers=None,
            persistent=False,
            fixed_delay_ms=None,
        ):
            mapping_response = MappingResponse(
                status=return_status,
                body=return_body,
                headers=headers or {"content-type": "application/json"},
                fixed_delay_milliseconds=fixed_delay_ms,
            )
            Mappings.create_mapping(
                Mapping(
                    request=MappingRequest(method=method, url=url),
                    response=mapping_response,
                    persistent=persistent,
                )
            )

        server.for_endpoint = for_endpoint

        yield server
