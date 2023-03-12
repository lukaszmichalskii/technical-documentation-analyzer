import os
import pathlib
import unittest

from src.application.text_parse import read_file, remove_escape_chars, PDFExtractor


class TestTextParse(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("resources")
        self.pdf_extractor = PDFExtractor()

    def test_read_file_chunk(self):
        file_ = self.resources.joinpath("dir/text1.txt")
        bytes_ = 16
        expected = "9000817973713744"
        with open(file_, "r") as f:
            content_ = read_file(f, chunk_size=bytes_)
            self.assertEqual(expected, next(content_))

    def test_remove_escape_chars(self):
        string_ = "    Text  \t to clean\n \t example.  "
        expected = "Text to clean example."
        self.assertEqual(expected, remove_escape_chars(string_))

    def test_extract_pdf(self):
        pdf_ = self.resources.joinpath("dir/sample.pdf")
        expected = """ A Simple PDF File 
 This is a small demonstration .pdf file - 
 just for use in the Virtual Mechanics tutorials. More text. And more 
 text. And more text. And more text. And more text. 
 And more text. And more text. And more text. And more text. And more 
 text. And more text. Boring, zzzzz. And more text. And more text. And 
 more text. And more text. And more text. And more text. And more text. 
 And more text. And more text. 
 And more text. And more text. And more text. And more text. And more 
 text. And more text. And more text. Even more. Continued on page 2 ..."""
        self.assertEqual(expected, next(self.pdf_extractor.extract_pdf(pdf_)))
