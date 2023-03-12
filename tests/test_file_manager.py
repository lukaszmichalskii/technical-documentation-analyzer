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

    def test_extract_txt(self) -> None:
        txt_ = self.resources.joinpath("dir/text2.txt")
        expected = "Text 2 content"
        self.assertEqual(expected, next(self.file_manager.process_file(txt_)))

    def test_read_pdf(self) -> None:
        pdf_ = self.resources.joinpath("dir/sample.pdf")
        expected = (
            "A Simple PDF File This is a small demonstration .pdf file - just for use in the Virtual Mechanics "
            "tutorials. More text. And more text. And more text. And more text. And more text. And more text. "
            "And more text. And more text. And more text. And more text. And more text. Boring, zzzzz. And "
            "more text. And more text. And more text. And more text. And more text. And more text. And more "
            "text. And more text. And more text. And more text. And more text. And more text. And more text. "
            "And more text. And more text. And more text. Even more. Continued on page 2 ...Simple PDF File 2 "
            "...continued from page 1. Yet more text. And more text. And more text. And more text. And more "
            "text. And more text. And more text. And more text. Oh, how boring typing this stuff. But not as "
            "boring as watching paint dry. And more text. And more text. And more text. And more text. Boring. "
            "More, a little more text. The end, and just as well."
        )
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

    def test_read_docx(self) -> None:
        word_ = self.resources.joinpath("test_500kB.docx")
        expected = (
            "Lorem ipsumLorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ac faucibus odio.Vestibulum "
            "neque massa, scelerisque sit amet ligula eu, congue molestie mi. Praesent ut varius sem. Nullam at "
            "porttitor arcu, nec lacinia nisi. Ut ac dolor vitae odio interdum condimentum. Vivamus dapibus sodales "
            "ex, vitae malesuada ipsum cursus convallis. Maecenas sed egestas nulla, ac condimentum orci. Mauris diam "
            "felis, vulputate ac suscipit et, iaculis non est. Curabitur semper arcu ac ligula semper, nec luctus "
            "nisl blandit. Integer lacinia ante ac libero lobortis imperdiet. Nullam mollis convallis ipsum, "
            "ac accumsan nunc vehicula vitae. Nulla eget justo in felis tristique fringilla. Morbi sit amet tortor "
            "quis risus auctor condimentum. Morbi in ullamcorper elit. Nulla iaculis tellus sit amet mauris tempus "
            "fringilla.Maecenas mauris lectus, lobortis et purus mattis, blandit dictum tellus.Maecenas non lorem "
            "quis tellus placerat varius.Nulla facilisi.Aenean congue fringilla justo ut aliquam.Nunc vulputate neque "
            "vitae justo facilisis, non condimentum ante sagittis."
        )
        actual = ""
        chunk_counter = 0  # do not read 500kB text in-memory read only chunk of it
        while chunk_counter < 10:
            try:
                text = next(self.file_manager.process_file(word_))
                actual += text
                chunk_counter += 1
            except StopIteration:
                break
        self.assertEqual(expected, actual)
