from __future__ import annotations

from enum import Enum


class HttpMethod(Enum):
    """
    An Enum representing the standard HTTP methods.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
