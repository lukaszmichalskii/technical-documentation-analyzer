import os
import pathlib
import unittest

from src.application.text_provider import TextProvider, NotSupportedDocumentFormat


def release_buffer(buffer) -> str:
    content = ""
    for bytes_ in buffer:
        content += bytes_
    return content


class TestTextProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = pathlib.Path(
            os.path.dirname(os.path.abspath(__file__))
        ).joinpath("resources")
        self.text_provider = TextProvider()

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
        actual = release_buffer(self.text_provider.get_file_chunk(pdf_))
        self.assertEqual(expected, actual)
        self.assertEqual(-1, self.text_provider.pdf_extractor.head)

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
            "vitae justo facilisis, non condimentum ante sagittis.Morbi viverra semper lorem nec molestie.Maecenas "
            "tincidunt est efficitur ligula euismod, sit amet ornare est vulputate.In non mauris justo. Duis vehicula "
            "mi vel mi pretium, a viverra erat efficitur. Cras aliquam est ac eros varius, id iaculis dui auctor. "
            "Duis pretium neque ligula, et pulvinar mi placerat et. Nulla nec nunc sit amet nunc posuere vestibulum. "
            "Ut id neque eget tortor mattis tristique. Donec ante est, blandit sit amet tristique vel, "
            "lacinia pulvinar arcu. Pellentesque scelerisque fermentum erat, id posuere justo pulvinar ut. Cras id "
            "eros sed enim aliquam lobortis. Sed lobortis nisl ut eros efficitur tincidunt. Cras justo mi, "
            "porttitor quis mattis vel, ultricies ut purus. Ut facilisis et lacus eu cursus.In eleifend velit vitae "
            "libero sollicitudin euismod. Fusce vitae vestibulum velit. Pellentesque vulputate lectus quis "
            "pellentesque commodo. Aliquam erat volutpat. Vestibulum in egestas velit. Pellentesque fermentum nisl "
            "vitae fringilla venenatis. Etiam id mauris vitae orci maximus ultricies.Cras fringilla ipsum magna, "
            "in fringilla dui commodo a.Etiam vehicula luctus fermentum. In vel metus congue, pulvinar lectus vel, "
            "fermentum dui. Maecenas ante orci, egestas ut aliquet sit amet, sagittis a magna. Aliquam ante quam, "
            "pellentesque ut dignissim quis, laoreet eget est. Aliquam erat volutpat. Class aptent taciti sociosqu ad "
            "litora torquent per conubia nostra, per inceptos himenaeos. Ut ullamcorper justo sapien, "
            "in cursus libero viverra eget. Vivamus auctor imperdiet urna, at pulvinar leo posuere laoreet. "
            "Suspendisse neque nisl, fringilla at iaculis scelerisque, ornare vel dolor. Ut et pulvinar nunc. "
            "Pellentesque fringilla mollis efficitur. Nullam venenatis commodo imperdiet. Morbi velit neque, "
            "semper quis lorem quis, efficitur dignissim ipsum. Ut ac lorem sed turpis imperdiet eleifend sit amet id "
            "sapien.Lorem ipsum dolor sit amet, consectetur adipiscing elit.Nunc ac faucibus odio. Vestibulum neque "
            "massa, scelerisque sit amet ligula eu, congue molestie mi. Praesent ut varius sem. Nullam at porttitor "
            "arcu, nec lacinia nisi. Ut ac dolor vitae odio interdum condimentum. Vivamus dapibus sodales ex, "
            "vitae malesuada ipsum cursus convallis. Maecenas sed egestas nulla, ac condimentum orci. Mauris diam "
            "felis, vulputate ac suscipit et, iaculis non est. Curabitur semper arcu ac ligula semper, nec luctus "
            "nisl blandit. Integer lacinia ante ac libero lobortis imperdiet. Nullam mollis convallis ipsum, "
            "ac accumsan nunc vehicula vitae. Nulla eget justo in felis tristique fringilla. Morbi sit amet tortor "
            "quis risus auctor condimentum. Morbi in ullamcorper elit. Nulla iaculis tellus sit amet mauris tempus "
            "fringilla.Maecenas mauris lectus, lobortis et purus mattis, blandit dictum tellus.Maecenas non lorem "
            "quis tellus placerat varius. Nulla facilisi. Aenean congue fringilla justo ut aliquam. Mauris id ex "
            "erat. Nunc vulputate neque vitae justo facilisis, non condimentum ante sagittis. Morbi viverra semper "
            "lorem nec molestie. Maecenas tincidunt est efficitur ligula euismod, sit amet ornare est vulputate.In "
            "non mauris justo. Duis vehicula mi vel mi pretium, a viverra erat efficitur. Cras aliquam est ac eros "
            "varius, id iaculis dui auctor. Duis pretium neque ligula, et pulvinar mi placerat et. Nulla nec nunc sit "
            "amet nunc posuere vestibulum. Ut id neque eget tortor mattis tristique. Donec ante est, blandit sit amet "
            "tristique vel, lacinia pulvinar arcu. Pellentesque scelerisque fermentum erat, id posuere justo pulvinar "
            "ut. Cras id eros sed enim aliquam lobortis. Sed lobortis nisl ut eros efficitur tincidunt. Cras justo "
            "mi, porttitor quis mattis vel, ultricies ut purus. Ut facilisis et lacus eu cursus.In eleifend velit "
            "vitae libero sollicitudin euismod.Fusce vitae vestibulum velit. Pellentesque vulputate lectus quis "
            "pellentesque commodo. Aliquam erat volutpat. Vestibulum in egestas velit. Pellentesque fermentum nisl "
            "vitae fringilla venenatis. Etiam id mauris vitae orci maximus ultricies. Cras fringilla ipsum magna, "
            "in fringilla dui commodo a.Etiam vehicula luctus fermentum. In vel metus congue, pulvinar lectus vel, "
            "fermentum dui. Maecenas ante orci, egestas ut aliquet sit amet, sagittis a magna. Aliquam ante quam, "
            "pellentesque ut dignissim quis, laoreet eget est. Aliquam erat volutpat. Class aptent taciti sociosqu ad "
            "litora torquent per conubia nostra, per inceptos himenaeos. Ut ullamcorper justo sapien, "
            "in cursus libero viverra eget. Vivamus auctor imperdiet urna, at pulvinar leo posuere laoreet. "
            "Suspendisse neque nisl, fringilla at iaculis scelerisque, ornare vel dolor. Ut et pulvinar nunc. "
            "Pellentesque fringilla mollis efficitur. Nullam venenatis commodo imperdiet. Morbi velit neque, "
            "semper quis lorem quis, efficitur dignissim ipsum. Ut ac lorem sed turpis imperdiet eleifend sit amet id "
            "sapien.Maecenas mauris lectus, lobortis et purus mattis, blandit dictum tellus.Maecenas non lorem quis "
            "tellus placerat varius. Nulla facilisi. Aenean congue fringilla justo ut aliquam. Mauris id ex erat. "
            "Nunc vulputate neque vitae justo facilisis, non condimentum ante sagittis. Morbi viverra semper lorem "
            "nec molestie. Maecenas tincidunt est efficitur ligula euismod, sit amet ornare est vulputate.In non "
            "mauris justo. Duis vehicula mi vel mi pretium, a viverra erat efficitur. Cras aliquam est ac eros "
            "varius, id iaculis dui auctor. Duis pretium neque ligula, et pulvinar mi placerat et. Nulla nec nunc sit "
            "amet nunc posuere vestibulum. Ut id neque eget tortor mattis tristique. Donec ante est, blandit sit amet "
            "tristique vel, lacinia pulvinar arcu. Pellentesque scelerisque fermentum erat, id posuere justo pulvinar "
            "ut. Cras id eros sed enim aliquam lobortis. Sed lobortis nisl ut eros efficitur tincidunt. Cras justo "
            "mi, porttitor quis mattis vel, ultricies ut purus. Ut facilisis et lacus eu cursus.In eleifend velit "
            "vitae libero sollicitudin euismod.Fusce vitae vestibulum velit. Pellentesque vulputate lectus quis "
            "pellentesque commodo. Aliquam erat volutpat. Vestibulum in egestas velit. Pellentesque fermentum nisl "
            "vitae fringilla venenatis. Etiam id mauris vitae orci maximus ultricies. Cras fringilla ipsum magna, "
            "in fringilla dui commodo a.Etiam vehicula luctus fermentum. In vel metus congue, pulvinar lectus vel, "
            "fermentum dui. Maecenas ante orci, egestas ut aliquet sit amet, sagittis a magna. Aliquam ante quam, "
            "pellentesque ut dignissim quis, laoreet eget est. Aliquam erat volutpat. Class aptent taciti sociosqu ad "
            "litora torquent per conubia nostra, per inceptos himenaeos. Ut ullamcorper justo sapien, "
            "in cursus libero viverra eget. Vivamus auctor imperdiet urna, at pulvinar leo posuere laoreet. "
            "Suspendisse neque nisl, fringilla at iaculis scelerisque, ornare vel dolor. Ut et pulvinar nunc. "
            "Pellentesque fringilla mollis efficitur. Nullam venenatis commodo imperdiet. Morbi velit neque, "
            "semper quis lorem quis, efficitur dignissim ipsum. Ut ac lorem sed turpis imperdiet eleifend sit amet id "
            "sapien."
        )
        actual = release_buffer(self.text_provider.get_file_chunk(word_))
        self.assertEqual(expected, actual)
        self.assertEqual(-1, self.text_provider.docx_extractor.head)

    def test_decode_text_doc_not_supported_format_exception(self):
        dummy_file = pathlib.Path("test.doc")
        self.assertRaises(
            NotSupportedDocumentFormat,
            lambda: list(self.text_provider.get_file_chunk(dummy_file)),
        )

    def test_decode_text_txt_not_supported_format_exception(self) -> None:
        txt_ = self.resources.joinpath("dir/text2.txt")
        self.assertRaises(
            NotSupportedDocumentFormat,
            lambda: list(self.text_provider.get_file_chunk(txt_)),
        )
