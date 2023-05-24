import logging
import os
import pathlib
import shutil
import tempfile
import unittest

import mock_logger
import utils
from src.application.common import Environment
from src.application.main import main


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 16 * 1024
        self.temp = tempfile.mkdtemp()
        self.archives = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("../resources/archives")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp)

    def main(self, args, env=None):
        cwd = os.getcwd()
        os.chdir(self.temp)
        try:
            logger = logging.getLogger("SKG")
            environment = Environment.from_env(
                {"IN_MEMORY_FILE_SIZE": 1000} if env is None else env
            )
            return main(["skg_app.py"] + args, logger, environment)
        except SystemExit as e:
            return e.code
        finally:
            os.chdir(cwd)

    def test_fail_on_broken_pipeline_setup(self):
        with mock_logger.MockLogger() as logger:
            self.assertEqual(
                1,
                self.main(["--techdoc_path", "test.pdf", "--only", "decode"]),
            )
            self.assertIn(
                (
                    "ERROR",
                    "Missing required step: 'decompress'.",
                ),
                logger.messages,
            )

    def test_abandon_execution_when_plugin_do_not_decode_at_all(self):
        file = self.archives.parent.joinpath("dir/sample.pdf")
        with mock_logger.MockLogger() as logger:
            self.assertEqual(
                3,
                self.main(["--techdoc_path", str(file), "--plugin", "plugin.txt"]),
            )
            self.assertIn(
                (
                    "ERROR",
                    "Plugin failed to decode provided files, nothing to analyze.",
                ),
                logger.messages,
            )

    def test_skip_file_if_plugin_fail_to_decode(self):
        directory = self.archives.parent.joinpath("dir")
        self.assertEqual(
            0,
            self.main(
                ["--techdoc_path", str(directory), "--only", "decompress", "decode"]
            ),
        )
        self.assertEqual(
            sorted(
                [
                    "lorem-ipsum.pdf",
                    "lorem-ipsum.txt",
                    "not_supported.csv",
                    "sample.pdf",
                    "sample.txt",
                    "text1.txt",
                    "text1.txt",
                    "text2.txt",
                    "text2.txt",
                ]
            ),
            sorted(utils.files_in_dir(pathlib.Path(self.temp).joinpath("results"))),
        )

    def test_decompress_zip_archive(self):
        zipfile_ = self.archives.joinpath("zipfile.zip")
        self.assertEqual(
            0,
            self.main(
                ["--techdoc_path", str(zipfile_), "--only", "decompress", "decode"]
            ),
        )
        self.assertEqual(
            sorted(
                [
                    "lorem-ipsum.pdf",
                    "lorem-ipsum.txt",
                    "text1.txt",
                    "text1.txt",
                    "text2.txt",
                    "text2.txt",
                ]
            ),
            sorted(utils.files_in_dir(pathlib.Path(self.temp).joinpath("results"))),
        )

    def test_decompress_tar_xz_archive(self):
        tarfile_ = self.archives.joinpath("tarfile.tar.xz")
        with mock_logger.MockLogger() as logger:
            self.assertEqual(
                0,
                self.main(
                    ["--techdoc_path", str(tarfile_), "--only", "decompress", "decode"]
                ),
            )
            self.assertEqual(
                sorted(
                    [
                        "lorem-ipsum.pdf",
                        "lorem-ipsum.txt",
                        "text1.txt",
                        "text1.txt",
                        "text2.txt",
                        "text2.txt",
                    ]
                ),
                sorted(utils.files_in_dir(pathlib.Path(self.temp).joinpath("results"))),
            )
            self.assertIn(
                (
                    "INFO",
                    "results/extracted/lorem-ipsum.pdf file has been parsed successfully.",
                ),
                logger.messages,
            )
            self.assertIn(
                ("INFO", "Decoding lorem-ipsum.pdf..."),
                logger.messages,
            )

    def test_decompress_not_supported_archive(self):
        archive_ = self.archives.joinpath("archive.7z")
        with mock_logger.MockLogger() as logger:
            self.assertEqual(1, self.main(["--techdoc_path", str(archive_)]))
            self.assertIn(("ERROR", ".7z archive not supported."), logger.messages)

    def test_just_copy_file(self):
        file = self.archives.parent.joinpath("dir/sample.pdf")
        with mock_logger.MockLogger() as logger:
            self.assertEqual(
                0,
                self.main(
                    ["--techdoc_path", str(file), "--only", "decompress", "decode"]
                ),
            )
            self.assertIn(
                (
                    "INFO",
                    "Nothing to be decompressed.",
                ),
                logger.messages,
            )
            self.assertIn(
                (
                    "INFO",
                    "results/extracted/sample.pdf file has been parsed successfully.",
                ),
                logger.messages,
            )
