import stardog
from src.application import logs


class StardogConnection:
    """
    Class for initializing connection with Stardog database based on environment parameters
    """

    def __init__(self, config, db_name=None, is_admin=False):
        self.endpoint = config.STARDOG_ENDPOINT
        self.username = config.STARDOG_USERNAME
        self.password = config.STARDOG_PASSWORD
        self.logger = logs.setup_logger()
        self.db_name = db_name
        self.is_admin = is_admin
        self.connection = None

    def __enter__(self):
        if self.is_admin:
            self.logger.info(f"Establishing admin connection")
            self.connection = stardog.Admin(self.endpoint, self.username, self.password)
            self.logger.info(f"Successfully established admin connection")
        else:
            if not self.db_name:
                raise ValueError("db_name must be provided for non-admin connection")
            self.logger.info(f"Connecting to database {self.db_name}")
            self.connection = stardog.Connection(
                self.db_name, self.endpoint, self.username, self.password
            )
            self.logger.info(f"Successfully connected to database {self.db_name}")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_admin:
            self.connection.client.close()
        else:
            self.connection.close()
