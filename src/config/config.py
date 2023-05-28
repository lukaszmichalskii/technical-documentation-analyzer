import os
from urllib3.util import parse_url


class Config:
    """security issue, better way to handle user credentials needed."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.STARDOG_ENDPOINT = os.environ.get("STARDOG_ENDPOINT")
        self.STARDOG_USERNAME = os.environ.get("STARDOG_USERNAME")
        self.STARDOG_PASSWORD = os.environ.get("STARDOG_PASSWORD")

        self.validate_url(self.STARDOG_ENDPOINT)

        self._initialized = True

    @staticmethod
    def validate_url(url: str):
        try:
            parse_url(url)
        except Exception:
            raise ValueError(f"Invalid URL: {url}")
