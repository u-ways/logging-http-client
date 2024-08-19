from __future__ import annotations

import logging
from typing import Mapping

from http_headers import with_source_header
from http_methods import HttpMethod
from http_session import LoggingSession


class LoggingHttpClient:
    """
    A client that allows logging of HTTP requests and responses, with an option to use a reusable session.
    """

    _logger: logging.Logger
    _reusable_session: bool
    _shared_headers: Mapping[str, str | bytes]
    _source: str | None
    _session: LoggingSession | None

    def __init__(
        self,
        logger: logging.Logger,
        reusable_session: bool = False,
        shared_headers: Mapping[str, str | bytes] = None,
        source: str = None,
    ) -> None:
        self._logger = logger
        self._reusable_session = reusable_session
        self._shared_headers = shared_headers if shared_headers is not None else {}
        self._source = source

        if self._reusable_session is not None:
            self._session = LoggingSession(self._source, self._logger)
            self._session.headers.update(self._shared_headers)
            if self._source is not None:
                self._session.headers.update(with_source_header(self._source))
        else:
            self._session = None

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
                    with LoggingSession(self._source, self._logger) as session:
                        session.headers.update(self._shared_headers)
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

    @property
    def shared_headers(self) -> Mapping[str, str | bytes]:
        """
        Get the shared headers that are sent with every request.

        :return: The shared headers.
        """
        return self._shared_headers

    @shared_headers.setter
    def shared_headers(self, headers: Mapping[str, str | bytes] | None) -> None:
        """
        Set the shared headers that are sent with every request.

        :param headers: The shared headers to set.
        """
        self._shared_headers = headers if headers is not None else {}
        if self._reusable_session is not None:
            self._session.headers.update(self._shared_headers)

    @shared_headers.deleter
    def shared_headers(self) -> None:
        """
        Delete the shared headers that are sent with every request.
        """
        self._shared_headers = {}
        if self._reusable_session is not None:
            self._session.headers.update(self._shared_headers)
