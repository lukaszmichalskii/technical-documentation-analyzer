import unittest

from src.nlp.information_extraction import (
    content_filtering,
    filter_sents,
    svo_extract,
    svo,
    svo_triples,
    named_entity_recognition,
)
from src.nlp.triples import SVO
from tests.nlp.utils import MODEL, NER


class TestInformationExtraction(unittest.TestCase):
    def test_content_filtering(self):
        sentences = [
            "Camera recognition is ROS2 node running on autonomous system main unit",
            "TensorRT library provided by NVIDIA",
            "Map used in path planner",
        ]
        filtered = content_filtering(sentences, ["TensorRT", "ROS2"])
        nothing_to_extract = content_filtering(sentences, [])
        self.assertEqual(
            [
                "Camera recognition is ROS2 node running on autonomous system main unit",
                "TensorRT library provided by NVIDIA",
            ],
            filtered,
        )
        self.assertEqual([], nothing_to_extract)

    def test_batch_overflow_sentences(self):
        sentences = [
            "Just two",
            "Then they are extracted from pc",
            "Clustering is done with cuda - clustering library",
            "For more information visit cuda-cluster git",
            "Result is array Ar, such that Ar[0] is the number of clusters, lets say n, Ar[i] for i between 1 and n, "
            "are number of points in each cluster, and rest of the points is just indexes of points that are part of "
            "clusters, organized with respect to each of n clusters",
        ]
        self.assertEqual(
            [
                "Then they are extracted from pc",
                "Clustering is done with cuda - clustering library",
                "For more information visit cuda-cluster git",
            ],
            filter_sents(sentences),
        )

    def test_svo_extract_noun_phrases(self):
        sentence = "System use TensorRT library provided by NVIDIA"
        self.assertEqual(
            SVO(subj="System", verb="use", obj="TensorRT library"),
            svo_extract(sentence, MODEL)[0],
        )

    def test_svo_extract_simple_expressions(self):
        sentence = "System use TensorRT"
        self.assertEqual(
            SVO(subj="System", verb="use", obj="TensorRT"),
            svo_extract(sentence, MODEL)[0],
        )

    def test_svo_filter_out_duplicates(self):
        sentences = [
            "System use TensorRT",
            "I use TensorRT",
            "System use TensorRT library provided by NVIDIA",
            "We use TensorRT library provided by NVIDIA",
        ]
        arr_ = svo(sentences, MODEL)
        self.assertEqual(
            {
                SVO(subj="System", verb="use", obj="TensorRT"),
                SVO(subj="System", verb="use", obj="TensorRT library"),
            },
            arr_,
        )

    def test_svo_filter_out_corrupted_triples(self):
        sentences = [
            "System use TensorRT",
            "I use ",
            "by NVIDIA",
            "We use TensorRT library provided by NVIDIA",
        ]
        arr_ = svo(sentences, MODEL)
        self.assertEqual(
            {
                SVO(subj="System", verb="use", obj="TensorRT"),
                SVO(subj="System", verb="use", obj="TensorRT library"),
            },
            arr_,
        )

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

    def test_ner_detect_algorithm(self):
        textSLAM = "AS use FastSLAM for localisation and mapping."
        textTriangulation = "Path planner utilize Delaunay triangulation"
        resultsSLAM = named_entity_recognition(textSLAM, NER)
        results_triangulation = named_entity_recognition(textTriangulation, NER)
        self.assertEqual(
            {
                SVO(
                    subj="System",
                    verb="use",
                    obj="FastSLAM",
                    subj_ner="SYSTEM",
                    obj_ner="ALGORITHM",
                )
            },
            resultsSLAM,
        )
        self.assertEqual(
            {
                SVO(
                    subj="System",
                    verb="use",
                    obj="Delaunay triangulation",
                    subj_ner="SYSTEM",
                    obj_ner="ALGORITHM",
                )
            },
            results_triangulation,
        )

    def test_ner_detect_libraries(self):
        text = "Module dependencies: TensorRT"
        results_libraries = named_entity_recognition(text, NER)
        self.assertEqual(
            {
                SVO(
                    subj="System",
                    verb="depend on",
                    obj="TensorRT",
                    subj_ner="SYSTEM",
                    obj_ner="LIBRARY",
                )
            },
            results_libraries,
        )

    def test_ner_detect_computing_platforms(self):
        textgpu = "Network is executed on GPU"
        textcpu = "Network is executed on CPU"
        results_gpu = named_entity_recognition(textgpu, NER)
        results_cpu = named_entity_recognition(textcpu, NER)
        self.assertEqual(
            {
                SVO(
                    subj="System",
                    verb="utilize",
                    obj="GPU",
                    subj_ner="SYSTEM",
                    obj_ner="PROCESSING_UNIT",
                )
            },
            results_gpu,
        )
        self.assertEqual(
            {
                SVO(
                    subj="System",
                    verb="utilize",
                    obj="CPU",
                    subj_ner="SYSTEM",
                    obj_ner="PROCESSING_UNIT",
                )
            },
            results_cpu,
        )
