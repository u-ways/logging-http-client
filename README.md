# Logging HTTP Client

[![CICD](https://github.com/u-ways/logging-http-client/actions/workflows/CICD.yml/badge.svg)](https://github.com/u-ways/logging-http-client/actions/workflows/CICD.yml)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Python: 3.12](https://img.shields.io/badge/python-3.12-008be1.svg)](https://www.python.org/downloads/release/python-3110/)
[![Linter: Flake8](https://img.shields.io/badge/linter-Flake8-008be1.svg)](https://flake8.pycqa.org/en/latest/)
[![Style: Black](https://img.shields.io/badge/style-Black-000.svg)](https://github.com/psf/black)

A logging library built on top of the [requests](https://pypi.org/project/requests/) library to provide a familiar
interface for sending HTTP requests with observability features out-of-the-box.

## Table of Contents

- [Background](#background)
- [Usage](#usage)
    - [1. Drop-in Replacement for requests](#1-drop-in-replacement-for-requests)
    - [2. Using the HTTP Client with reusable Sessions](#2-using-the-http-client-with-reusable-sessions)
        - [i. Disabling Reusable Sessions For The HTTP Client](#i-disabling-reusable-sessions-for-the-http-client)
        - [ii. Adding Shared Headers to the HTTP Client](#ii-adding-shared-headers-to-the-http-client)
        - [iii. Setting the client's `x-source`](#iii-setting-the-clients-x-source)
        - [iii. `x-request-id` is automatically set](#iii-x-request-id-is-automatically-set)
        - [iv. `x-correlation-id` can be automatically set](#iv-x-correlation-id-can-be-automatically-set)
    - [3. Custom Logging Hooks](#3-custom-logging-hooks)
        - [i. Request Logging Hook](#i-request-logging-hook)
        - [ii. Response Logging Hook](#ii-response-logging-hook)
    - [4. Default Logging Configurations](#4-default-logging-configurations)
        - [i. Disabling Request or Response Logging](#i-disabling-request-or-response-logging)
        - [ii. Enabling Request or Response Body Logging](#ii-enabling-request-or-response-body-logging)
    - [5. Obscuring Sensitive Data](#5-obscuring-sensitive-data)
        - [i. Request Log Record Obscurer](#i-request-log-record-obscurer)
        - [ii. Response Log Record Obscurer](#ii-response-log-record-obscurer)
- [HTTP Log Record Structure](#http-log-record-structure)
- [Contributing](#contributing)
    - [Prerequisites](#prerequisites)
    - [Environment Setup](#environment-setup)
    - [Code Quality](#code-quality)

## Background

The requests library is a popular library for sending HTTP requests in Python. However, it does not provide adequate
observability features out of the box such as tracing and logging. As such, this library was built to decorate the
requests library API to provide these opinionated features for common use cases.

## Usage

The quickest way to get started is to install the package from PyPI:

```shell
pip install logging-http-client
```

For poetry users:

```shell
poetry add logging-http-client
```

### 1. Drop-in Replacement for requests

The library is designed to decorate requests library existing API.
Hence, you can use it in the same way you would use the [requests](https://pypi.org/project/requests/) library:

```python
import logging_http_client

response = logging_http_client.get('https://www.python.org')
print(response.status_code)
# => 200
```

Given it's built as a wrapper around the requests library, you can alias the
import to `requests` and use it as drop-in replacement for the requests' library.

```python
import logging_http_client as requests

response = requests.get('https://www.python.org')
print(response.status_code)
# => 200
```

The other HTTP methods are supported - see `requests.api`.
Full documentation is at: https://requests.readthedocs.io

### 2. Using the HTTP Client with reusable Sessions

The library provides a `LoggingHttpClient` class which is essentially a wrapper around the core component of the
requests library, the `Session` object, with additional features such as enabling reusable sessions or not.

```python
import logging_http_client

client = logging_http_client.create()

response = client.get('https://www.python.org')
print(response.status_code)
# => 200
```

#### i. Disabling Reusable Sessions For The HTTP Client

By default, the `LoggingHttpClient` class is created with a reusable session. If you want to disable this behaviour, you
can pass the `reusable_session=False` argument to the `create` method.

```python
import logging_http_client

client = logging_http_client.create(reusable_session=False)

response = client.get('https://www.python.org')
print(response.status_code)
# => 200
```

#### ii. Adding Shared Headers to the HTTP Client

You also have access to the session object headers within the `LoggingHttpClient` class, so you can add shared headers to the
session object [just like you would with the requests library](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects).

```python
import logging_http_client

client = logging_http_client.create()

client.shared_headers = {"Authorization": "Bearer <token>"}

# To clear the headers, you can set it to None
client.shared_headers = None
# or delete the attribute
del client.shared_headers
```

#### iii. Setting the client's `x-source`

It's common to set a `x-source` header to identify the source of the request.
You can set this header on the client by passing the `source` argument to the
`create` method.

```python
import logging

import logging_http_client

root_logger = logging.getLogger()
root_logger.setLevel(level=logging.INFO)

client = logging_http_client.create(source="my-system-name", logger=root_logger)

response = client.get('https://www.python.org')
# => Log record will include: 
#    { http { request_source: "my-system-name", ... } }
```

#### iii. `x-request-id` is automatically set

The library automatically sets a `x-request-id` header on the request, and is logged within the response as well. The
`x-request-id` is a UUID that is generated for each request, and it's attached on both the request and the response
logs.

```python
import logging

import logging_http_client

root_logger = logging.getLogger()
root_logger.setLevel(level=logging.INFO)

client = logging_http_client.create(source="my-system-name", logger=root_logger)

response = client.get('https://www.python.org')
# => The client will append the `x-request-id` header to the request
#
# => Both request and response log records will include: 
#    { http { request_id: "<uuid>", ... } }
# => The reqeust log record will also attach it as a header: 
#    { http { request_headers: { "x-request-id": "<uuid>", ... }, ... } }
```

#### iv. `x-correlation-id` can be automatically set

It's common to set a `x-correlation-id` header to identify the correlation of the request within a distributed system.
Instead of having to set this header manually every single request you make, you can pass a correlation ID generator
function to the client, and it will automatically set the `x-correlation-id` header for each request.

> [!WARNING]
> Be aware that `x-request-id` is not the same as `x-correlation-id`.
> 
> The `x-request-id` is unique to each request, while the `x-correlation-id` is used to correlate requests within a
> chain of events that can span multiple services, this is common in a microservice architecture. Please ensure you
> understand the difference between the two whilst using them with this library.

```python
import uuid
import logging_http_client
import logging_http_client_config 

def correlation_id_provider() -> str:
    return str(uuid.uuid4())

logging_http_client_config.set_correlation_id_provider(correlation_id_provider)

logging_http_client.create().get('https://www.python.org')
# => The client will append the `x-correlation-id` header to the request 
#
# => The request log records will include:
#    { http { request_headers: { "x-correlation-id": "<uuid>", ... }, ... } }
```

Do note we do NOT set the `x-correlation-id` header on the response, it's the responsibility of the server to set it
back on the response, if they don't, then you need to relay on your logging setup to append the `correlation_id` as an 
extra log record attribute on the client side by other means.

### 3. Custom Logging Hooks

The library provides a way to attach custom logging hooks at the global level. They're intended to REPLACE the
default logging behaviour with your own logging logic. Here is how you can apply:

#### i. Request Logging Hook

The request logging hook is called **before** the request is sent. It gives you access to the client logger, and
the [prepared request](https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests) object. You can
use this hook to log the request before it's sent.

```python
import logging

from requests import PreparedRequest

import logging_http_client
import logging_http_client_config


def custom_request_logging_hook(logger: logging.Logger, request: PreparedRequest):
    logger.debug("Custom request logging for %s", request.url)


logging_http_client_config.set_custom_request_logging_hook(custom_request_logging_hook)

logging_http_client.create().get('https://www.python.org')

# => Log record will include:
#    { message { "Custom request logging for https://www.python.org" } }
```

#### ii. Response Logging Hook

The response logging hook is called **after** the response is received. It gives you access to the client logger, and
the [response object](https://requests.readthedocs.io/en/latest/api/#requests.Response). You can use this hook to log
the response after it's received.

```python
import logging

from requests import Response

import logging_http_client
import logging_http_client_config


def custom_response_logging_hook(logger: logging.Logger, response: Response):
    logger.debug("Custom response logging for %s", response.url)


logging_http_client_config.set_custom_response_logging_hook(custom_response_logging_hook)

logging_http_client.create().get('https://www.python.org')

# => Log record will include:
#    { message { "Custom response logging for https://www.python.org" } }
```

### 4. Default Logging Configurations

The default logging comes with a set of configurations that can be customised to suit your needs.

#### i. Disabling Request or Response Logging

You can disable request or response logging by calling the `disable_request_logging` or `disable_response_logging`
methods respectively. This will prevent the library from generating log records for requests or responses UNLESS you
have custom logging hooks set.

```python
import logging_http_client
import logging_http_client_config

logging_http_client_config.disable_request_logging()
logging_http_client_config.disable_response_logging()

logging_http_client.create().get('https://www.python.org')
# => No request log record will be generated
# => No response log record will be generated
```

#### ii. Enabling Request or Response Body Logging

By default, the library does not log the request or response body. You can enable this by calling the `enable_request_body_logging`
or `enable_response_body_logging` methods respectively. This will log the request or response body in the log record.

```python
import logging_http_client
import logging_http_client_config

logging_http_client_config.enable_request_body_logging()
logging_http_client_config.enable_response_body_logging()

logging_http_client.create().get('https://www.python.org')
# => Log record will include the request or response body (if present)
```

### 5. Obscuring Sensitive Data

The library provides a way to obscure sensitive data in the request or response log records. This is useful when you
want to log the request or response body but want to obscure sensitive data such as passwords, tokens, etc.

#### i. Request Log Record Obscurer

You can set a request log record obscurer by calling the `set_request_log_record_obscurer` method. The obscurer
function should take a `HttpLogRecord` object and expects to return a modified `HttpLogRecord` object. The obscurer
function will be called JUST BEFORE the request is logged.

```python
import logging_http_client
import logging_http_client_config
from logging_http_client import HttpLogRecord


def request_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.request_method = "REDACTED"
    if record.request_headers.get("Authorization") is not None:
        record.request_headers["Authorization"] = "****"
    return record


logging_http_client_config.set_request_log_record_obscurer(request_log_record_obscurer)

logging_http_client.create().get(
    url='https://www.python.org',
    headers={"Authorization": "Bearer SOME-SECRET-TOKEN"}
)

# => Log record will include:
#    { http { request_headers: { "Authorization ": "****", ... }, ... } }
```

#### ii. Response Log Record Obscurer

Likewise, you can set a response log record obscurer by calling the `set_response_log_record_obscurer` method.
The obscurer function should take a `HttpLogRecord` object and expects to return a modified `HttpLogRecord` object.

```python
import logging_http_client
import logging_http_client_config
from logging_http_client import HttpLogRecord


def response_log_record_obscurer(record: HttpLogRecord) -> HttpLogRecord:
    record.response_status = 999
    if record.response_body is not None:
        record.response_body = record.response_body.replace("SENSITIVE", "****")
    return record


logging_http_client_config.set_response_log_record_obscurer(response_log_record_obscurer)
logging_http_client_config.enable_response_body_logging()

logging_http_client.create().get('https://www.python.org')
# Assume the response body contains "some response body with SENSITIVE information" 

# => Log record will include:
#    { http { response_status: 999, response_body: "some response body with **** information", ... } }
```

## HTTP Log Record Structure

The library logs HTTP requests and responses as structured log records. The log records are structured as JSON
object passed to the logger's `extra` keyword argument. The log records are structured as follows:

```json
{
  "http": {
    "request_id": "<uuid>",
    "request_source": "<source>",
    "request_method": "<method>",
    "request_url": "<url>",
    "request_query_params": "<query_params>",
    "request_headers": "<headers>",
    "request_body": "<body>",
    "response_status": "<status>",
    "response_headers": "<headers>",
    "response_duration_ms": "<duration>",
    "response_body": "<body>"
  }
}
```

If any of those top-level fields are `None`, `{}`, `[]`, `""`, `0`, or `0.0`,
they will be omitted from the log record for brevity purposes.

The actual data class used to represent the log record is `HttpLogRecord` and is available in the `logging_http_client`.

## Contributing

If you have any suggestions or improvements, feel free to open a PR or an issue. The build and development process has
been made to be as seamless as possible, so you can easily run and test your changes locally before submitting a PR.

### Prerequisites

- [Python](https://www.python.org/downloads/): The project is built with Python 3.12.
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer): The dependency management tool of
  choice for this project.
- [Docker](https://docs.docker.com/engine/install/): For containerisation support, so it can be completely built and run
  in an isolated environment.
- [Make](https://www.gnu.org/software/make/): For running common tasks such as installing dependencies, building the
  project, running tests, etc.

### Environment Setup

Before opening the project in your IDE, I highly recommend running the following recipe:

```shell
make setup
```

This will create your Poetry's virtual environment, install the project's dependencies, set up the code quality
pre-commit hook, and configure your IDE (VSCode and PyCharm) as appropriate.

### Code Quality

We ask for adequate test coverage and adherence to the project's code quality standards. This includes running the
tests, formatter, and linter before submitting a PR. You can run the following command to ensure your changes are in
line with the project standards:

```bash
make check-code-quality
```

___