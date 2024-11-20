# Default Logging Configurations

The default logging comes with a set of configurations that can be customised to suit your needs.

## 1. Disabling Request or Response Logging

You can disable request or response logging by calling the `disable_request_logging` or `disable_response_logging`
methods respectively. This will prevent the library from generating log records for requests or responses UNLESS you
have custom logging hooks set.

```python
import logging_http_client

logging_http_client.disable_request_logging()
logging_http_client.disable_response_logging()

logging_http_client.create().get('https://www.python.org')
# => No request log record will be generated
# => No response log record will be generated
```

## 2. Enabling Request or Response Body Logging

By default, the library does not log the request or response body. You can enable this by calling the `enable_request_body_logging`
or `enable_response_body_logging` methods respectively. This will log the request or response body in the log record.

```python
import logging_http_client

logging_http_client.enable_request_body_logging()
logging_http_client.enable_response_body_logging()

logging_http_client.create().get('https://www.python.org')
# => Log record will include the request or response body (if present)
```

## 3. Customizing the logging level

By default, the library logs at the 'INFO' level. To adjust this, use the set_logging_level method. You can specify the desired level as either an integer (10, 20, 30, 40, 50) or a string ("INFO", "DEBUG", etc.).
```python
import logging_http_client

logging_http_client.set_logging_level(logging_http_client.LogLevel.DEBUG)

logging_http_client.create().get('https://www.python.org')
# => Logs will be recorded at the DEBUG level now.
```