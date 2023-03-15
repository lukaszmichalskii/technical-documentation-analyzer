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
from src.application.text_provider import NotSupportedDocumentFormat


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
    Autodetect what to do
    python skg_app.py --techdoc_path input_path --output results_dir
    Decompress only files
    python skg_app.py --techdoc_path example.zip --output results_dir --only decompress
    Decode only file
    python skg_app.py --techdoc_path example.pdf --output results_dir --only decode
    Decode only files
    python skg_app.py --techdoc_path examples/ --output results_dir --only decode
    
More info: <confluence manual url>"""


def extracted_path(results_dir: pathlib.Path) -> pathlib.Path:
    extracted = results_dir.joinpath("extracted")
    if not extracted.exists():
        extracted.mkdir()
    return extracted


def decoded_path(results_dir: pathlib.Path) -> pathlib.Path:
    decoded = results_dir.joinpath("decoded")
    if not decoded.exists():
        decoded.mkdir()
    return decoded


def run_app(
    args: argparse.Namespace,
    argv: typing.List[str],
    logger: logging.Logger,
    environment: common.Environment,
) -> int:
    def decompress_step() -> None:
        extracted = extracted_path(output)
        logger.info(
            f"Decompressing files from {str(techdoc_path)} to {str(extracted)}..."
        )
        decompression.decompress(
            techdoc_path, extracted
        )

    def copy_step() -> None:
        logger.info(
            f"Nothing to be decompressed."
        )
        if techdoc_path.is_dir():
            decompression.copydir(techdoc_path, output.joinpath())
        else:
            shutil.copy2(techdoc_path, output)

    def decode_step() -> None:
        file_manager = FileManager(file_size_limit=environment.in_memory_file_limit)
        for file in FileManager.files_in_dir(output):
            try:
                file = pathlib.Path(file)
                decoded_text = file_manager.decode_text(file)
                logger.info(f"{file} file has been parsed successfully.")
                file_manager.save_parsed_text(
                    decoded_path(output).joinpath(file.name.split('.')[0] + common.RESULTS_FORMAT), decoded_text)
            except NotSupportedDocumentFormat as e:
                logger.warning(f'Skipping file {file}. {str(e)}')
                continue

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

    techdoc_path = pathlib.Path(args.techdoc_path)
    output = pathlib.Path(args.output)
    if not output.exists():
        output.mkdir()
    if STEPS.DECOMPRESS in args.only:
        try:
            if techdoc_path.is_dir() or techdoc_path.suffix in common.SUPPORTED_DOCUMENTS:
                copy_step()
            else:
                decompress_step()
        except (DecompressionError, NotSupportedArchiveFormat, NotSupportedDocumentFormat) as e:
            logger.error(str(e))
            logger.info("App finished with exit code 1")
            return 1
    if STEPS.DECODE in args.only:
        decode_step()
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
        help="path to the compressed documentation file, directory with already decompressed files or single file.",
        metavar="path",
    )
    parser.add_argument(
        "--only",
        type=str,
        nargs="*",
        choices=STEPS_CHOICES,
        default=STANDARD_STEPS,
        help="""specifies actions which should be performed on input package:
    'decompress' - decompress files from archive pointed by --techdoc_path to the directory pointed by --output
    'decode'     - decode extracted files, cleanup text for NLP processing.
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
