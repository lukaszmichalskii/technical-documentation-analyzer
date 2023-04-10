import os
import unittest

from src.nlp import google_kgs


class TestGoogleKnowledgeGraphSearch(unittest.TestCase):
    def test_google_api_params(self):
        expected = {"query": "test", "limit": 1, "indent": True, "key": "dummy_key"}

        self.assertEqual(
            expected,
            google_kgs.google_api_params(
                query="test", limit=1, indent=True, api_key="dummy_key"
            ),
        )

    def test_build_url(self):
        params = {"query": "test", "limit": 1, "indent": True, "key": "dummy_key"}
        expected = "https://kgsearch.googleapis.com/v1/entities:search?query=test&limit=1&indent=True&key=dummy_key"
        self.assertEqual(expected, google_kgs.build_url(params))

    def test_search(self):
        query = "cat"
        limit = 1
        api_key = os.environ.get("API_KEY")
        expected = (
            [
                "The cat is a domestic species of small carnivorous mammal. It is the only domesticated species "
                "in the family Felidae and is commonly referred to as the domestic cat or house cat to "
                "distinguish it from the wild members of the family. "
            ],
            [["Thing"]],
            ["https://en.wikipedia.org/wiki/Cat"],
        )
        try:
            actual = google_kgs.google_search(query, limit, ner=True)
            self.assertEqual(expected, actual)
        except google_kgs.GoogleSearchError:
            self.fail("GET request error response from API")
