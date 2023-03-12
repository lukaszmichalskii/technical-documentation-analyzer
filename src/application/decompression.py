from __future__ import annotations

import pathlib
import shutil
import tarfile
import zipfile


class DecompressionError(Exception):
    pass


class NotSupportedArchiveFormat(Exception):
    pass


def decompress(source: pathlib.Path, destination: pathlib.Path) -> None:
    """
    Args:
        source (pathlib.Path): file path to archive
        destination (pathlib.Path): file path to output to directory
    Returns:
        None
    Raises:
        DecompressionError: If archive is corrupted or interrupted
        NotSupportedArchiveFormat: If provided archive is compressed using unsupported format
    """
    if zipfile.is_zipfile(source):
        try:
            with zipfile.ZipFile(source) as zip_fd:
                return zip_fd.extractall(destination)
        except zipfile.BadZipFile:
            raise DecompressionError
    elif tarfile.is_tarfile(source):
        try:
            with tarfile.open(source) as tar_fd:
                return tar_fd.extractall(destination)
        except tarfile.TarError:
            raise DecompressionError
    raise NotSupportedArchiveFormat


def copyfileobj(source: pathlib.Path, destination: pathlib.Path) -> None:
    """
    Copy files from source directory to destination dir.
    If destination dir not exists then create whole tree.
    Args:
        source (pathlib.Path): file path to source directory
        destination (pathlib.Path): file path to output directory
    Returns:
        None
    """
    if source.is_dir():
        if not destination.exists():
            destination.mkdir()
        shutil.copytree(source, destination, dirs_exist_ok=True)
