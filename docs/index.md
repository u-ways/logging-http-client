# Welcome to Logging-HTTP-Client

Welcome to Logging-HTTP-Client, a logging library built on top of the [requests](https://pypi.org/project/requests/) library to provide a familiar interface for sending HTTP requests with observability features out-of-the-box.

## Background

The [requests](https://pypi.org/project/requests/) library is a popular library for sending HTTP requests in Python. 
However, it does not provide adequate observability features out of the box such as tracing and logging. As such, 
this library was built to decorate the requests library API to provide these opinionated features for common use 
cases.

For example, by simply using this library for your requests, the following will be appended to your logs:

``` py
import logging
import logging_http_client as requests

# Basic logging configuration for demonstration purposes 
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s - %(http)s'
)

requests.get(
    url="https://www.python.org",
    headers={"x-foo": "bar"},
)

# => Log records will include:
#    message: REQUEST, 
#    http: { 
#       request_id: "6a09ec23-b318-43d2-81a1-8c1fcaf77d05", 
#       request_method: "GET", 
#       request_url: "https://www.python.org", 
#       request_headers: { "x-foo": "bar", "x-request-id": "6a09ec23-b318-43d2-81a1-8c1fcaf77d05", ... } 
#   }
#
#    message: RESPONSE,
#    http: {
#       request_id: "6a09ec23-b318-43d2-81a1-8c1fcaf77d05",
#       response_status: 200,
#       response_headers: { "content-type": "text/html", ... },
#       response_duration_ms: 30
#    }
```

You have full control over the logging behaviour, and you can customise it to suit your needs. The library provides
hooks for custom logging, and you can disable or enable request or response logging as needed. You can also obscure
sensitive data in the log records, and set shared headers for the client instances that relies on reusable sessions
for better performance by default.
