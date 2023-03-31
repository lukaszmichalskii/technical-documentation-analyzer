import stardog
from dotenv import find_dotenv, load_dotenv
from src.application import logs
import os


class StardogConnection:
    """
    Class for initializing connection with Stardog database based on environment parameters
    """

    def __init__(self, db_name):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("STARDOG_ENDPOINT")
        self.username = os.environ.get("STARDOG_USERNAME")
        self.password = os.environ.get("STARDOG_PASSWORD")
        self.logger = logs.setup_logger()
        self.connection = self.connect(db_name)

    def connect(self, db_name):
        try:
            return stardog.Connection(
                db_name, self.endpoint, self.username, self.password
            )
        except stardog.exceptions.StardogException as exception:
            self.logger.error(
                f"An error while connecting to the database. "
                f"Database name: {db_name}, "
                f"Username: {self.username}, "
                f"Password: {self.password}, "
                f"Endpoint: {self.endpoint}"
                f"Exception: {exception}"
            )

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        return True
