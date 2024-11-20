# Drop-in Replacement for requests

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