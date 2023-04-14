import argparse
import logging
import os.path
import sys
import typing
import stardog

from src.application import common, logs
from src.database.stardog_connection import StardogConnection
from src.config.config import Config


def get_help_epilog():
    return """
Examples:
    Execute the query from the file on the sample data from the database 
    python src.database.main --query_path example.sparql
    Upload the data to the new database
    python src.database.main --ttl_path example.ttf --db_name example
"""


def run_app(
        args: argparse.Namespace,
        argv: typing.List[str],
        logger: logging.Logger,
        environment: common.Environment,
) -> int:
    if args.create_db:
        with StardogConnection(Config, is_admin=True) as admin_conn:
            database = admin_conn.new_database(args.db_name)
            logger.info(f"Created new database with name: {args.db_name}")
            database.drop()
            logger.info(f"Shut down of database with name: {args.db_name}")
        return 0

    if args.query_path is not None:
        with StardogConnection(Config, args.db_name) as conn:
            query_file = open(args.query_path, "r")
            result = conn.select(
                query_file.read(), content_type=stardog.content_types.SPARQL_JSON
            )
            logger.info(f"Result of query: {result}")
        return 0

    if args.ttl_path is not None:
        with StardogConnection(Config, is_admin=True) as admin_conn:
            database = admin_conn.new_database(args.db_name)
            logger.info(f"Created new database with name: {args.db_name}")
            with StardogConnection(Config, args.db_name) as conn:
                conn.begin()
                conn.add(stardog.content.File(args.ttl_path))
                results = conn.select("select * { ?a ?p ?o }")
                logger.info(f"Uploaded data: {results}")
            database.drop()
            logger.info(f"Shut down of database with name: {args.db_name}")
        return 0

    logger.info("App finished with exit code 0")
    return 0


def main(argv: typing.List[str], logger=None, environment=None) -> int:
    if logger is None:
        logger = logs.setup_logger()
    if environment is None:
        environment = common.Environment.from_env(os.environ)
    parser = argparse.ArgumentParser(
        description="This is a command line tool for executing queries on the Stardog database",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--create_db",
        action="store_true",
        help="specifies if database should be created",
    )
    parser.add_argument(
        "--query_path",
        type=str,
        help="specifies path to the file with query to execute",
    )
    parser.add_argument(
        "--ttl_path", type=str, help="specifies path to the file in the RDF format "
                                     "that will be uploaded to the database"
    )
    parser.add_argument(
        "db_name", type=str, help="specifies database name"
    )
    parser.epilog = get_help_epilog()
    return run_app(parser.parse_args(argv[1:]), argv, logger, environment)


if __name__ == "__main__":
    if sys.version_info[:2] < (3, 8):
        sys.exit(
            "Python {}.{}.{} is not supported. You should run app with Python 3.8 or later".format(
                *sys.version_info[:3]
            )
        )
    sys.exit(main(sys.argv))
