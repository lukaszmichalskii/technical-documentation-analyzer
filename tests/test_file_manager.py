import os
import pathlib
import unittest

from src.application.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("resources")
        self.file_manager = FileManager()

    def test_extract_txt(self):
        txt_ = self.resources.joinpath("dir/text2.txt")
        expected = "Text 2 content"
        self.assertEqual(expected, next(self.file_manager.process_file(txt_)))

    def test_extract_pdf(self):
        pdf_ = self.resources.joinpath("dir/sample.pdf")
        expected = "A Simple PDF File This is a small demonstration .pdf file - just for use in the Virtual Mechanics tutorials. More text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Boring, zzzzz. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Even more. Continued on page 2 ...Simple PDF File 2 ...continued from page 1. Yet more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Oh, how boring typing this stuff. But not as boring as watching paint dry. And more text. And more text. And more text. And more text. Boring. More, a little more text. The end, and just as well."
        actual = ""
        while True:
            try:
                text = next(self.file_manager.process_file(pdf_))
                if not text:
                    break
                actual += text
            except StopIteration:
                break
        self.assertEqual(expected, actual)
