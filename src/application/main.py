import argparse
import logging
import os.path
import pathlib
import shutil
import sys
import typing

from src.application import common, decompression, logs
from src.application.common import STEPS_CHOICES, STEPS, STANDARD_STEPS
from src.application.decompression import DecompressionError, NotSupportedArchiveFormat
from src.application.file_manager import FileManager


def get_help_epilog():
    return """
Exit codes:
    0 - successful execution
    any other code indicated unrecoverable error - output might be invalid
    
Environment variables:
    IN_MEMORY_FILE_SIZE : Maximum file size that can be loaded into program memory in bytes.
                          If file size is greater than resource limit then content is broken down into smaller pieces.
                          Default: 1MB
Examples:
    Decompress only files
    python skg_app.py --techdoc_path example.zip --output results_dir --only decompress
    Decode only files
    python skg_app.py --techdoc_path example.tar.xz --output results_dir --only decode
    
More info: <confluence manual url>"""


def run_app(
    args: argparse.Namespace,
    argv: typing.List[str],
    logger: logging.Logger,
    environment: common.Environment,
) -> int:
    if common.get_current_os() != "linux":
        logger.warning(
            f"You are using toolkit on {common.get_current_os()}. Some functionalities may not work correctly"
        )
    logger.info(
        f"pythonApp: {sys.executable} argv: {argv} {environment.to_info_string()}"
    )
    if os.path.exists(args.output) and os.listdir(args.output):
        logger.error(f"Output directory {args.output} is not empty")
        logger.info("App finished with exit code 1")
        return 1
    if STEPS.DECOMPRESS in args.only:
        try:
            if pathlib.Path(args.techdoc_path).is_dir():
                logger.info(
                    f"Copying files from {args.techdoc_path} to {args.output}..."
                )
                decompression.copydir(
                    pathlib.Path(args.techdoc_path), pathlib.Path(args.output)
                )
            else:
                if pathlib.Path(args.techdoc_path).suffix in [".docx", ".pdf", ".txt"]:
                    logger.info(
                        f"Nothing to be decompressed, copying file {pathlib.Path(args.techdoc_path).name} to {args.output}"
                    )
                    shutil.copy2(args.techdoc_path, args.output)
                else:
                    logger.info(
                        f"Decompressing files from {args.techdoc_path} to {args.output}..."
                    )
                    decompression.decompress(
                        pathlib.Path(args.techdoc_path), pathlib.Path(args.output)
                    )
        except (DecompressionError, NotSupportedArchiveFormat) as e:
            logger.error(str(e))
            logger.info("App finished with exit code 1")
            return 1
    if STEPS.DECODE in args.only:
        file_manager = FileManager(file_size_limit=environment.in_memory_file_limit)
        for file in FileManager.files_in_dir(args.output):
            logger.info(f"Reading file {file}...")
            file_manager.get_text(pathlib.Path(args.output).joinpath(file))
    logger.info("App finished with exit code 0")
    return 0


def main(argv: typing.List[str], logger=None, environment=None) -> int:
    if logger is None:
        logger = logs.setup_logger()
    if environment is None:
        environment = common.Environment.from_env(os.environ)
    parser = argparse.ArgumentParser(
        description="Automatic Semantic Knowledge Graph (ASKG) - automatically update knowledge graph from technical documentation content",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--techdoc_path",
        type=str,
        required=True,
        help="path to the compressed documentation file or directory with already decompressed files.",
        metavar="path",
    )
    parser.add_argument(
        "--only",
        type=str,
        nargs="*",
        choices=STEPS_CHOICES,
        default=STANDARD_STEPS,
        help="""specifies actions which should be performed on input package:
    'decompres' - decompress files from archive pointed by --techdoc_path to the directory pointed by --output
    'decode'    - decode extracted files
    """,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="output_folder",
        default="results",
        help="specifies directory, where results should be saved. Has to be empty",
    )
    parser.epilog = get_help_epilog()
    return run_app(parser.parse_args(argv[1:]), argv, logger, environment)
