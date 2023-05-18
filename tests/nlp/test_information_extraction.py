import unittest

from src.nlp.triples import SVO, SPO
from tests.nlp.utils import MODEL, TAGGER, tag
from src.nlp.information_extraction import content_filtering, filter_sents, svo_extract, svo, spo


class TestInformationExtraction(unittest.TestCase):
    def test_content_filtering(self):
        sentences = [
            "Camera recognition is ROS2 node running on autonomous system main unit",
            "TensorRT library provided by NVIDIA",
            "Map used in path planner"
        ]
        filtered = content_filtering(sentences, ["TensorRT", "ROS2"])
        nothing_to_extract = content_filtering(sentences, [])
        self.assertEqual(
            [
                "Camera recognition is ROS2 node running on autonomous system main unit",
                "TensorRT library provided by NVIDIA"
            ],
            filtered
        )
        self.assertEqual([], nothing_to_extract)

    def test_batch_overflow_sentences(self):
        sentences = [
            "Just two",
            "Then they are extracted from pc",
            "Clustering is done with cuda - clustering library",
            "For more information visit cuda-cluster git",
            "Result is array Ar, such that Ar[0] is the number of clusters, lets say n, Ar[i] for i between 1 and n, are number of points in each cluster, and rest of the points is just indexes of points that are part of clusters, organized with respect to each of n clusters"
        ]
        self.assertEqual(
            [
                "Then they are extracted from pc",
                "Clustering is done with cuda - clustering library",
                "For more information visit cuda-cluster git",
            ],
            filter_sents(sentences)
        )

    def test_svo_extract_noun_phrases(self):
        sentence = "System use TensorRT library provided by NVIDIA"
        self.assertEqual(
            SVO(subj="System", verb="use", obj="TensorRT library"),
            svo_extract(sentence, MODEL)[0]
        )

    def test_svo_extract_simple_expressions(self):
        sentence = "System use TensorRT"
        self.assertEqual(
            SVO(subj="System", verb="use", obj="TensorRT"),
            svo_extract(sentence, MODEL)[0]
        )

    def test_svo_filter_out_duplicates(self):
        sentences = [
                "System use TensorRT",
                "I use TensorRT",
                "System use TensorRT library provided by NVIDIA",
                "We use TensorRT library provided by NVIDIA"
            ]
        arr_ = svo(sentences, MODEL)
        self.assertEqual(
            {SVO(subj="System", verb="use", obj="TensorRT"), SVO(subj="System", verb="use", obj="TensorRT library")},
            arr_
        )

    def test_svo_filter_out_corrupted_triples(self):
        sentences = [
            "System use TensorRT",
            "I use ",
            "by NVIDIA",
            "We use TensorRT library provided by NVIDIA"
        ]
        arr_ = svo(sentences, MODEL)
        self.assertEqual(
            {SVO(subj="System", verb="use", obj="TensorRT"), SVO(subj="System", verb="use", obj="TensorRT library")},
            arr_
        )
