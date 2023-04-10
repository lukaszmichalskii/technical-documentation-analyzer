import unittest

from src.nlp.nlp_clean import (
    remove_stop_words_and_punct,
    remove_special_characters,
    remove_duplicates,
    remove_literals,
)


class TestNLPClean(unittest.TestCase):
    def test_remove_special_characters(self):
        text = """Camera recognition
is a component of\ncontrol pipeline of\tSEE part of autonomous\nsystem."""
        expected = "Camera recognition is a component of control pipeline of SEE part of autonomous system."
        self.assertEqual(expected, remove_special_characters(text))

    def test_remove_stop_words_and_punct(self):
        text = "Camera recognition is a component of control pipeline of SEE part of autonomous system."
        expected = "Camera recognition component control pipeline autonomous system"
        self.assertEqual(expected, remove_stop_words_and_punct(text))

    def test_remove_duplicates(self):
        dup = [
            ("camera recognition", "be", "component"),
            ("camera recognition", "be", "control pipeline"),
            ("camera recognition", "be", "ros2 node"),
            ("camera recognition", "be", "component"),
            ("camera recognition", "be", "control pipeline"),
            ("camera recognition", "be", "autonomous system"),
            ("camera recognition", "be", "ros2 node"),
        ]

        expected = [
            ("camera recognition", "be", "component"),
            ("camera recognition", "be", "control pipeline"),
            ("camera recognition", "be", "ros2 node"),
            ("camera recognition", "be", "autonomous system"),
        ]

        self.assertEqual(expected, remove_duplicates(dup, tup_pos=2))

    def test_remove_literals(self):
        literals = [
            ("camera recognition", "be", "component"),
            ("camera recognition", "be", "control pipeline"),
            ("camera recognition", "be", "1990"),
            ("camera recognition", "be", "68"),
            ("camera recognition", "be", "autonomous system main unit"),
        ]

        expected = [
            ("camera recognition", "be", "component"),
            ("camera recognition", "be", "control pipeline"),
            ("camera recognition", "be", "autonomous system main unit"),
        ]

        self.assertEqual(expected, remove_literals(literals))
