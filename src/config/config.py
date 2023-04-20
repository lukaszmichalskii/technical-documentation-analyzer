import os


class Config:
    STARDOG_ENDPOINT = os.environ.get("STARDOG_ENDPOINT")
    STARDOG_USERNAME = os.environ.get("STARDOG_USERNAME")
    STARDOG_PASSWORD = os.environ.get("STARDOG_PASSWORD")
    STARDOG_DATABASE = os.environ.get("STARDOG_DATABASE")
