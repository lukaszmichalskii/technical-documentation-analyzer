import stardog
from src.application import logs


class StardogConnection:
    """
    Class for initializing connection with Stardog database based on environment parameters
    """

    def __init__(self, config):
        self.endpoint = config.STARDOG_ENDPOINT
        self.username = config.STARDOG_USERNAME
        self.password = config.STARDOG_PASSWORD
        self.logger = logs.setup_logger()
        self.connection = None

    def __enter__(self, db_name=None, is_admin=False):
        self.logger.info(f"Connecting to database {db_name}")
        if is_admin:
            self.connection = stardog.Admin(self.endpoint, self.username, self.password)
            self.logger.info(f"Successfully established admin connection")
        else:
            if not db_name:
                raise ValueError("db_name must be provided for non-admin connection")
            self.connection = stardog.Connection(db_name, self.endpoint, self.username, self.password)
            self.logger.info(f"Successfully connected to database {db_name}")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
