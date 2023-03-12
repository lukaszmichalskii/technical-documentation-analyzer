import os
import pathlib
import unittest

from src.application.text_parse import read_file, remove_escape_chars, PDFDecoder, WordDecoder


class TestTextParse(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("resources")
        self.pdf_extractor = PDFDecoder()
        self.word_extractor = WordDecoder()

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

    def test_read_pdf(self):
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
        self.assertEqual(expected, next(self.pdf_extractor.read(pdf_)))

    def test_read_docx_files(self):
        docx_ = self.resources.joinpath("test_500kB.docx")
        expected = "Vestibulum neque massa, scelerisque sit amet ligula eu, congue molestie mi. Praesent ut varius " \
                   "sem. Nullam at porttitor arcu, nec lacinia nisi. Ut ac dolor vitae odio interdum condimentum. " \
                   "Vivamus dapibus sodales ex, vitae malesuada ipsum cursus convallis. Maecenas sed egestas nulla, " \
                   "ac condimentum orci. Mauris diam felis, vulputate ac suscipit et, iaculis non est. Curabitur " \
                   "semper arcu ac ligula semper, nec luctus nisl blandit. Integer lacinia ante ac libero lobortis " \
                   "imperdiet. Nullam mollis convallis ipsum, ac accumsan nunc vehicula vitae. Nulla eget justo in " \
                   "felis tristique fringilla. Morbi sit amet tortor quis risus auctor condimentum. Morbi in " \
                   "ullamcorper elit. Nulla iaculis tellus sit amet mauris tempus fringilla."
        self.word_extractor.head = 3  # move head to center of document to read only one paragraph
        self.assertEqual(expected, next(self.word_extractor.read(docx_)))
