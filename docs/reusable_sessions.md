# Using the HTTP Client with Reusable Sessions

The library provides a `LoggingHttpClient` class which is essentially a wrapper around the core component of the
requests library, the `Session` object, with additional features such as enabling reusable sessions or not.

```python
import logging_http_client

client = logging_http_client.create()

response = client.get('https://www.python.org')
print(response.status_code)
# => 200
```

## 1. Disabling Reusable Sessions For The HTTP Client

By default, the `LoggingHttpClient` class is created with a reusable session. If you want to disable this behaviour, you
can pass the `reusable_session=False` argument to the `create` method.

```python
import logging_http_client

client = logging_http_client.create(reusable_session=False)

response = client.get('https://www.python.org')
print(response.status_code)
# => 200
```

## 2. Adding Shared Headers to the HTTP Client

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

## 3. Setting the client's `x-source`

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

## 4. `x-request-id` is automatically set

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

## 5. `x-correlation-id` can be automatically set

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

def correlation_id_provider() -> str:
    return str(uuid.uuid4())

logging_http_client.set_correlation_id_provider(correlation_id_provider)

logging_http_client.create().get('https://www.python.org')
# => The client will append the `x-correlation-id` header to the request 
#
# => The request log records will include:
#    { http { request_headers: { "x-correlation-id": "<uuid>", ... }, ... } }
```

Do note we do NOT set the `x-correlation-id` header on the response, it's the responsibility of the server to set it
back on the response, if they don't, then you need to rely on your logging setup to append the `correlation_id` as an 
extra log record attribute on the client side by other means.