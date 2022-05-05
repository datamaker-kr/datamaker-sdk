from requests import RequestException


class ClientError(RequestException):
    """A Client error occurred."""
