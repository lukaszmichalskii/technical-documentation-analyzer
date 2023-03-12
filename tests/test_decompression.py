import os
import pathlib
import tempfile
import unittest

from src.application.decompression import decompress, copyfileobj
from tests.utils import files_in_dir


class TestDecompression(unittest.TestCase):
    def setUp(self) -> None:
        self.archives = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("resources/archives")
        self.expected_dir = ["lorem-ipsum.pdf", "text1.txt", "sample.pdf", "text2.txt"]
        self.expected_archive = ["lorem-ipsum.pdf", "text1.txt", "text2.txt"]

    def test_extract_tar(self) -> None:
        tarfile_ = self.archives.joinpath("tarfile.tar.xz")
        with tempfile.TemporaryDirectory(dir=self.archives) as temp:
            decompress(tarfile_, pathlib.Path(temp))
            actual = files_in_dir(pathlib.Path(temp))
            self.assertEqual(self.expected_archive, actual)

    def test_extract_zip(self) -> None:
        zipfile_ = self.archives.joinpath("zipfile.zip")
        with tempfile.TemporaryDirectory(dir=self.archives) as temp:
            decompress(zipfile_, pathlib.Path(temp))
            actual = files_in_dir(pathlib.Path(temp))
            self.assertEqual(self.expected_archive, actual)

    def test_copyfileobj(self) -> None:
        files_ = self.archives.parent.joinpath("dir")
        with tempfile.TemporaryDirectory(dir=self.archives) as temp:
            copyfileobj(files_, pathlib.Path(temp))
            actual = files_in_dir(pathlib.Path(temp))
            self.assertEqual(self.expected_dir, actual)
