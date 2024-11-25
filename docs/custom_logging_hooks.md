# Custom Logging Hooks

The library provides a way to attach custom logging hooks at the global level. They're intended to REPLACE the
default logging behaviour with your own logging logic. Here is how you can apply:

## 1. Request Logging Hook

The request logging hook is called **before** the request is sent. It gives you access to the client logger, and
the [prepared request](https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests) object. You can
use this hook to log the request before it's sent.

```python
import logging

from requests import PreparedRequest

import logging_http_client


def custom_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
    logger.debug("Custom request logging for %s", request.url)


logging_http_client.set_custom_request_logging_hook(custom_request_logging_hook)

logging_http_client.create().get('https://www.python.org')

# => Log record will include:
#    { message { "Custom request logging for https://www.python.org" } }
```

## 2. Response Logging Hook

The response logging hook is called **after** the response is received. It gives you access to the client logger, and
the [response object](https://requests.readthedocs.io/en/latest/api/#requests.Response). You can use this hook to log
the response after it's received.

```python
import logging

from requests import Response

import logging_http_client


def custom_response_logging_hook(logger: logging.Logger, response: Response):
    logger.debug("Custom response logging for %s", response.url)


logging_http_client.set_custom_response_logging_hook(custom_response_logging_hook)

logging_http_client.create().get('https://www.python.org')

# => Log record will include:
#    { message { "Custom response logging for https://www.python.org" } }
```