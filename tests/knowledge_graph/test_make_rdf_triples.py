from unittest import TestCase

from src.knowledge_graph.make_rdf_triples import convert_to_rdf
from src.nlp.triples import SVO, SPO


class Test(TestCase):
    def test_empty_verb_and_ner(self):
        test = [SVO(subj='Steve Jobs', verb='', obj='Apple', subj_ner=[], obj_ner=[])]
        rdf_triple = convert_to_rdf(test)
        self.assertEqual(rdf_triple, [])

    def test_empty_verb(self):
        test = [SVO(subj='Steve Jobs', verb='', obj='Apple', subj_ner=['Person'], obj_ner=['Company'])]
        expected = [':Steve_Jobs rdf:type :Person .', ':Apple rdf:type :Company .']
        rdf_triple = convert_to_rdf(test)
        self.assertEqual(rdf_triple, expected)

    def test_SVO_and_SPO(self):
        test = [SVO(subj='Steve Jobs', verb='own', obj='Apple', subj_ner=['Person'], obj_ner=['Company', 'Thing']),
                SPO(subj='Steve Jobs', pred='part of', obj='Apple', subj_attrs=['Person'], obj_attrs=['Company', 'Thing'])]
        expected = [':Steve_Jobs :own :Apple .', ':Steve_Jobs rdf:type :Person .', ':Apple rdf:type :Company .',
                    ':Apple rdf:type :Thing .', ':Steve_Jobs :part_of :Apple .', ':Steve_Jobs rdf:type :Person .',
                    ':Apple rdf:type :Company .', ':Apple rdf:type :Thing .']
        rdf_triple = convert_to_rdf(test)
        self.assertEqual(rdf_triple, expected)
