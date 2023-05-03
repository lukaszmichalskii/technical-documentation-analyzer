import unittest
from unittest.mock import MagicMock, patch
from src.database.stardog_connection import StardogConnection


class MockConfig:
    STARDOG_ENDPOINT = "http://localhost:5820"
    STARDOG_USERNAME = "admin"
    STARDOG_PASSWORD = "admin"


class TestStardogConnection(unittest.TestCase):
    @patch("src.application.logs.setup_logger")
    @patch("stardog.Admin")
    def test_enter_admin_connection(self, mock_stardog_admin_connection, mock_logger):
        mock_logger.return_value = MagicMock()
        mock_stardog_admin_connection.return_value = MagicMock()

        with StardogConnection(MockConfig, is_admin=True) as connection:
            pass

        mock_stardog_admin_connection.assert_called_once_with(
            MockConfig.STARDOG_ENDPOINT,
            MockConfig.STARDOG_USERNAME,
            MockConfig.STARDOG_PASSWORD,
        )

    @patch("src.application.logs.setup_logger")
    @patch("stardog.Connection")
    def test_enter_non_admin_connection(self, mock_stardog_connection, mock_logger):
        mock_logger.return_value = MagicMock()
        mock_stardog_connection.return_value = MagicMock()
        db_name = "test_db"

        with StardogConnection(MockConfig, db_name=db_name) as connection:
            pass

        mock_stardog_connection.assert_called_once_with(
            db_name,
            MockConfig.STARDOG_ENDPOINT,
            MockConfig.STARDOG_USERNAME,
            MockConfig.STARDOG_PASSWORD,
        )

    @patch("src.application.logs.setup_logger")
    def test_enter_no_db_name(self, mock_setup_logger):
        mock_setup_logger.return_value = MagicMock()

        with self.assertRaises(ValueError):
            with StardogConnection(MockConfig) as connection:
                pass

    @patch("src.application.logs.setup_logger")
    @patch("stardog.Admin")
    def test_exit_admin_connection(self, mock_stardog_admin, mock_logger):
        mock_logger.return_value = MagicMock()
        mock_stardog_admin.return_value = MagicMock()
        mock_stardog_admin.return_value.client.close = MagicMock()

        with StardogConnection(MockConfig, is_admin=True) as connection:
            pass

        mock_stardog_admin.return_value.client.close.assert_called_once()

    @patch("src.application.logs.setup_logger")
    @patch("stardog.Connection")
    def test_exit_non_admin_connection(self, mock_stardog_connection, mock_logger):
        mock_logger.return_value = MagicMock()
        mock_stardog_connection.return_value = MagicMock()
        mock_stardog_connection.return_value.close = MagicMock()
        db_name = "test_db"

        with StardogConnection(MockConfig, db_name=db_name) as connection:
            pass

        mock_stardog_connection.return_value.close.assert_called_once()
