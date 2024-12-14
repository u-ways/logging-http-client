import copy
import uuid
from logging import Logger

from requests import Session, Response, Request, PreparedRequest
from typing_extensions import override

import logging_http_client.logging_http_client_config_globals as config
from http_headers import X_REQUEST_ID_HEADER, X_CORRELATION_ID_HEADER, X_SOURCE_HEADER


class LoggingSession(Session):
    """
    A subclass of :class:`requests.Session` decorates the request and response details
    in the :meth:`requests.sessions.Session.request <requests.sessions.Session.request>` method.
    """

    _logger: Logger
    _source: str

    def __init__(self, source: str, logger: Logger) -> None:
        super().__init__()

        self._source = source
        self._logger = logger

    @override
    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ) -> Response:
        """
        Delegates the request call to a prepared request to wire our observability configurations.
        """
        prepared_request = self.prepare_request(
            Request(
                method=method,
                url=url,
                headers=headers,
                files=files,
                data=data,
                params=params,
                auth=auth,
                cookies=cookies,
                hooks=hooks,
                json=json,
            )
        )
        response = self.send(
            request=prepared_request,
            stream=stream,
            verify=verify,
            proxies=proxies,
            cert=cert,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
        return response

    @override
    def send(self, request: PreparedRequest, **kwargs) -> Response:
        """
        We override the send method to apply our logging hooks before and after the request is made.

        NOTE:
            The logging hooks are applied BEFORE (request) and AFTER (response) the request is made.
            In the event of a hook exception, the request will NOT be blocked. Instead, we gracefully
            catch the exception and log it to avoid disturbing the request/response flow.
        """
        self._run_logging_request_hooks(request)
        response = super().send(request, **kwargs)
        self._run_logging_response_hooks(response)
        return response

    @override
    def prepare_request(self, request) -> PreparedRequest:
        """
        Prepares the request by adding the observability headers to the request.

        NOTE:
            The observability headers are added to the request if they do NOT exist
            in the request headers. The request headers are then updated based on
            the set client configuration. If an exception occurs during the preparation
            of the request, we catch the exception and log it to avoid disturbing the
            request flow.
        """
        prepared = super().prepare_request(request)
        try:
            request_id = prepared.headers.get(X_REQUEST_ID_HEADER, None)
            correlation_id = prepared.headers.get(X_CORRELATION_ID_HEADER, None)
            source_system = prepared.headers.get(X_SOURCE_HEADER, None)

            correlation_id_provider = config.get_correlation_id_provider()

            if request_id is None:
                prepared.headers.update({X_REQUEST_ID_HEADER: str(uuid.uuid4())})
            if source_system is None and self._source is not None:
                prepared.headers.update({X_SOURCE_HEADER: self._source})
            if correlation_id is None and correlation_id_provider is not None:
                prepared.headers.update({X_CORRELATION_ID_HEADER: correlation_id_provider()})
        except Exception as e:
            self._logger.exception("Error preparing observability request headers", exc_info=e)
        finally:
            return prepared

    def _run_logging_request_hooks(self, request: PreparedRequest) -> None:
        if config.is_request_logging_enabled():
            try:
                for hook in config.get_request_logging_hooks():
                    hook(self._logger, copy.deepcopy(request))
            except Exception as e:
                self._logger.exception("Error applying request logging hooks", exc_info=e)

    def _run_logging_response_hooks(self, response: Response) -> None:
        if config.is_response_logging_enabled():
            try:
                for hook in config.get_response_logging_hooks():
                    hook(self._logger, copy.deepcopy(response))
            except Exception as e:
                self._logger.exception("Error applying response logging hooks", exc_info=e)
