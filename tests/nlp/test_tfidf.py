import unittest

from src.nlp.tfidf import tfidf


class TestTFIDF(unittest.TestCase):
    def setUp(self) -> None:
        self.corpus = """
        Test text to count word occurrences. Test text corpus text word.
        """

    def test_tfidf(self):
        ranking = [
            ("text", 3),
            ("test", 2),
            ("word", 2),
            ("count", 1),
            ("occurrences", 1),
            ("corpus", 1),
        ]
        empty = ""
        case_non_sensitive = "Text detected as same word as text"
        self.assertEqual([], tfidf(empty))
        self.assertEqual(("text", 2), tfidf(case_non_sensitive)[0])
        self.assertEqual(ranking, tfidf(self.corpus))
