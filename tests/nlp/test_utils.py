import unittest

from src.nlp.triples import SVO
from tests.nlp.utils import MODEL
from src.nlp.utils import svo_triples


class TestUtils(unittest.TestCase):
    def test_svo_triple_in_person_calls_substitution(self):
        triple1 = "we create map"
        triple2 = "we create landmark map"
        triple3 = "they use FSOCO"

        resolved = svo_triples([triple1, triple2, triple3], MODEL)
        self.assertEqual(
            [
                SVO(subj="system", obj="create", verb="map"),
                SVO(subj="system", obj="landmark map", verb="create"),
                SVO(subj="system", obj="FSOCO", verb="use"),
            ].sort(),
            resolved.sort(),
        )

    def test_svo_triple_resolve_noun_phrases(self):
        triple_multi_obj = "FastSLAM create landmark map"
        triple_multi_subj = "Simultaneous localization create occupancy grid"
        resolved = svo_triples([triple_multi_obj, triple_multi_subj], MODEL)
        self.assertEqual(
            [
                SVO(subj="FastSLAM", obj="landmark map", verb="create"),
                SVO(
                    subj="Simultaneous localization",
                    obj="occupancy grid",
                    verb="create",
                ),
            ].sort(),
            resolved.sort(),
        )

    def test_svo_triple_remove_invalid_relations(self):
        corrupted = "one associate "
        correct = "FastSLAM create landmark map"
        results = svo_triples([corrupted, correct], MODEL)
        self.assertEqual(
            [SVO(subj="FastSLAM", obj="landmark map", verb="create")], results
        )
