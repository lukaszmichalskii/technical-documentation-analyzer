import stardog
from dotenv import find_dotenv, load_dotenv
from src.application import logs
import os


class StardogAdminConnection:
    """
    Class for initializing admin connection with Stardog database based on environment parameters
    """

    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("STARDOG_ENDPOINT")
        self.username = os.environ.get("STARDOG_USERNAME")
        self.password = os.environ.get("STARDOG_PASSWORD")
        self.logger = logs.setup_logger()
        self.connection = self.connect()

    def connect(self):
        try:
            return stardog.Admin(self.endpoint, self.username, self.password)
        except stardog.exceptions.StardogException as exception:
            self.logger.error(
                f"An error while connecting to the database. "
                f"Username: {self.username}, "
                f"Password: {self.password}, "
                f"Endpoint: {self.endpoint}"
                f"Exception: {exception}"
            )

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.client.close()
        return True
