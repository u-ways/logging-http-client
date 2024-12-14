"""
Logging HTTP Client Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logging HTTP client is a library that allows logging of HTTP requests and
responses, with an option to use a reusable session. It is built on top
of the requests library to provide a familiar interface for sending HTTP
requests.

Basic GET usage: (with reusable session)

```python
import logging_http_client

client = logging_http_client.create(reusable_session=True)

response = client.get('https://www.python.org')
response.status_code

# Output: 200
```

Given it's built as a wrapper around the requests library, you can alias the
import to `requests` and use it as drop-in replacement for the requests' library.

```python
import logging_http_client as requests

response = requests.get('https://www.python.org')
response.status_code

# Output: 200
```

The other HTTP methods are supported - see `requests.api`.
Full documentation is at <https://requests.readthedocs.io>.
"""

import logging
from typing import Mapping

# noinspection PyUnresolvedReferences
from requests import packages, utils  # noqa: F401

# noinspection PyUnresolvedReferences
from requests.exceptions import (  # noqa: F401
    ConnectionError,
    ConnectTimeout,
    FileModeWarning,
    HTTPError,
    JSONDecodeError,
    ReadTimeout,
    RequestException,
    Timeout,
    TooManyRedirects,
    URLRequired,
)

# noinspection PyUnresolvedReferences
from requests.models import PreparedRequest, Request, Response  # noqa: F401

# noinspection PyUnresolvedReferences
from requests.sessions import Session, session  # noqa: F401

# noinspection PyUnresolvedReferences
from requests.status_codes import codes  # noqa: F401

from .logging_default_hooks import default_request_logging_hook, default_response_logging_hook
from .http_log_record import HttpLogRecord  # noqa: F401
from .logging_http_client_class import LoggingHttpClient
from .logging_http_client_config import (  # noqa: F401
    set_correlation_id_provider,
    set_request_log_record_obscurers,
    set_response_log_record_obscurers,
    set_request_log_record_obscurer,
    set_response_log_record_obscurer,
    set_request_logging_hooks,
    set_response_logging_hooks,
    set_custom_request_logging_hook,
    set_custom_response_logging_hook,
    disable_request_logging,
    disable_response_logging,
    enable_request_body_logging,
    enable_response_body_logging,
    set_default_hooks_logging_level,
)

set_default_hooks_logging_level(logging.INFO)
set_request_logging_hooks([default_request_logging_hook])
set_response_logging_hooks([default_response_logging_hook])


def create(
    source: str = None,
    reusable_session: bool = True,
    logger: logging.Logger = logging.getLogger(),
    shared_headers: Mapping[str, str | bytes] = None,
) -> LoggingHttpClient:
    """
    Factory function to create a new logging HTTP client instance.

    :param source: The source of the request. This is used to identify the source/system of the request.
    :param reusable_session: Whether to use a reusable session for all requests.
    :param logger: The logger to use for logging requests and responses.
    :param shared_headers: The headers to include with every request.
    :return: A new LoggingHttpClient instance.
    """
    return LoggingHttpClient(
        source=source,
        logger=logger,
        reusable_session=reusable_session,
        shared_headers=shared_headers,
    )


def request(method, url, **kwargs) -> Response:
    """
    Sends a request to the specified URL.

    :param method: The HTTP method to use.
    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).request(method, url, **kwargs)


def get(url: str, **kwargs) -> Response:
    """
    Sends a GET request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).get(url, **kwargs)


def post(url: str, **kwargs) -> Response:
    """
    Sends a POST request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).post(url, **kwargs)


def put(url: str, **kwargs) -> Response:
    """
    Sends a PUT request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).put(url, **kwargs)


def delete(url: str, **kwargs) -> Response:
    """
    Sends a DELETE request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).delete(url, **kwargs)


def patch(url: str, **kwargs) -> Response:
    """
    Sends a PATCH request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).patch(url, **kwargs)


def head(url: str, **kwargs) -> Response:
    """
    Sends a HEAD request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).head(url, **kwargs)


def options(url: str, **kwargs) -> Response:
    """
    Sends a OPTIONS request to the specified URL.

    :param url: The URL to send the request to.
    :param kwargs: Additional arguments to pass to the request method.
    :return: A new LoggingHttpClient instance.
    """
    return create(reusable_session=False).options(url, **kwargs)
