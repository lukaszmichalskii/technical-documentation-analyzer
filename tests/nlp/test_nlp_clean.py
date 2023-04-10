import unittest

from src.nlp.nlp_clean import remove_stop_words_and_punct, remove_special_characters


class TestNLPClean(unittest.TestCase):
    def test_remove_special_characters(self):
        text = '''Camera recognition
is a component of\ncontrol pipeline of\tSEE part of autonomous\nsystem.'''
        expected = "Camera recognition is a component of control pipeline of SEE part of autonomous system."
        self.assertEqual(expected, remove_special_characters(text))

    def test_remove_stop_words_and_punct(self):
        text = "Camera recognition is a component of control pipeline of SEE part of autonomous system."
        expected = "Camera recognition component control pipeline autonomous system"
        self.assertEqual(expected, remove_stop_words_and_punct(text))

    def test_remove_duplicates(self):
        pass

    def test_remove_dates(self):
        pass
