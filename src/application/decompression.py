from __future__ import annotations

import os.path
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
                for zip_info in zip_fd.infolist():
                    if zip_info.is_dir():
                        continue
                    zip_info.filename = os.path.basename(zip_info.filename)
                    zip_fd.extract(zip_info, destination)
                return
        except zipfile.BadZipFile as e:
            raise DecompressionError(str(e))
    elif tarfile.is_tarfile(source):
        try:
            with tarfile.open(source) as tar_fd:
                for tar_info in tar_fd.getmembers():
                    if tar_info.isdir():
                        continue
                    tar_info.name = os.path.basename(tar_info.name)
                    tar_fd.extract(tar_info, destination)
                return
        except tarfile.TarError as e:
            raise DecompressionError(str(e))
    raise NotSupportedArchiveFormat(f"{source.suffix} archive not supported.")


def copydir(source: pathlib.Path, destination: pathlib.Path) -> None:
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
