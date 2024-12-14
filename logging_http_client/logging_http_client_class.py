from __future__ import annotations

import logging
from typing import Mapping

from requests import Session

from logging_http_client.http_headers import with_source_header
from logging_http_client.http_session import LoggingSession


class LoggingHttpClient:
    """
    A client that allows logging of HTTP requests and responses, with an option to use a reusable session.
    """

    _source: str | None
    _reusable_session: bool
    _logger: logging.Logger
    _shared_headers: Mapping[str, str | bytes]

    _session: LoggingSession | None

    def __init__(
        self,
        source: str = None,
        reusable_session: bool = False,
        logger: logging.Logger = logging.getLogger(),
        shared_headers: Mapping[str, str | bytes] = None,
    ) -> None:
        self._source = source
        self._reusable_session = reusable_session
        self._logger = logger
        self._shared_headers = shared_headers if shared_headers is not None else {}

        if self._reusable_session:
            reusable = LoggingSession(source, logger)
            self._session = self._decorate_session(reusable)

    def __getattr__(self, name: str):
        """
        Dynamically get an attribute from the session.

        :param name: The name of the attribute to get.
        :return: The attribute.
        :raises AttributeError: If the attribute does not exist.
        """
        if name in Session.__dict__:
            return getattr(self.session, name)
        else:
            raise AttributeError(f"Unsupported attribute: '{name}'")

    def __del__(self) -> None:
        """
        Destructor to ensure the session is closed when the client is garbage collected.
        """
        if self._session is not None:
            self._session.close()

    @property
    def session(self) -> LoggingSession:
        """
        Get the session that is used to send requests.

        If the client is configured to use a reusable session,
        this will return the same session for every request.

        Otherwise, a new session will be created for each request.

        :return: The session.
        """
        if self._reusable_session:
            return self._session
        else:
            disposable = LoggingSession(self._source, self._logger)
            return self._decorate_session(disposable)

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

    def _decorate_session(self, session: LoggingSession) -> LoggingSession:
        """
        Decorate the session with the shared headers and source.

        :param session: The session to decorate.
        :return: The decorated session.
        """
        if self._source is not None:
            session.headers.update(with_source_header(self._source))
        if self._shared_headers:
            session.headers.update(self._shared_headers)
        return session
