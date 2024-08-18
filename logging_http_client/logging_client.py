from __future__ import annotations

import logging

from http_methods import HttpMethod
from http_session import LoggingSession


class LoggingHttpClient:
    """
    A client that allows logging of HTTP requests and responses, with an option to use a reusable session.
    """

    _logger: logging.Logger
    _session: LoggingSession | None
    _reusable_session: bool

    def __init__(self, logger: logging.Logger, reusable_session: bool = False) -> None:
        self._logger = logger
        self._reusable_session = reusable_session
        self._session = LoggingSession(self._logger) if reusable_session else None

    def __getattr__(self, name: str):
        """
        Dynamically handle the HTTP methods like GET, POST, PUT, DELETE, etc.

        :param name: The name of the attribute to get.
        :return: A lambda function that sends a request using the specified HTTP method.
        :raises AttributeError: If the attribute name is not a valid HTTP method.
        """
        method: HttpMethod | None = HttpMethod.__members__.get(name.upper())

        if method is not None:
            if self._reusable_session is True:
                return lambda url, **kwargs: self._session.request(method=str(method.value), url=url, **kwargs)
            else:

                def request_with_single_use_session(url, **kwargs):
                    with LoggingSession(self._logger) as session:
                        return session.request(method=str(method.value), url=url, **kwargs)

                return request_with_single_use_session
        else:
            raise AttributeError(f"Attribute requested is not a valid HTTP method: {name}")

    def __del__(self) -> None:
        """
        Destructor to ensure the session is closed when the client is garbage collected.
        """
        if self._session is not None:
            self._session.close()
