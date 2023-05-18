import unittest

from src.nlp.pre_processing import remove_unicode


class TestPreprocessing(unittest.TestCase):
    def test_remove_whitespace_characters(self):
        corpus = "Some text with\nnew lines, spaces      and\t tabulators\r\n"
        self.assertEqual(
            "Some text with new lines, spaces and tabulators ", remove_unicode(corpus)
        )

    def test_remove_unicode(self):
        quotation = "ROS2’s SLAM node"
        link = "For more info check https://blank.page/"
        self.assertEqual("For more info check  ", remove_unicode(link))
        self.assertEqual("ROS2 s SLAM node", remove_unicode(quotation))
