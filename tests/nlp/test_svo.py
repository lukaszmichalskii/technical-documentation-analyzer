import unittest

from src.nlp.build import nlp
from src.nlp.svo import create_svo_triples, create_svo_lists


class TestSVO(unittest.TestCase):
    def test_create_svo_triples(self):
        text = "A rare black squirrel has become a regular visitor to a suburban garden."
        expected = ('rare black squirrel', 'become', 'regular visitor')
        self.assertIn(expected, create_svo_triples(text))

    def test_create_svo_triples_large(self):
        text = "Given the real time images from two stereo ZED cameras, camera recognition detects landmarks and " \
               "creates field of cones that is later used by path planner module."
        expected = ('zed cameras', 'detect', 'landmarks')
        self.assertIn(expected, create_svo_triples(text))

    def test_create_svo_lists(self):
        text = "First version of cone detection module successfully detects cones from input images based on the " \
               "trained network."
        doc = nlp(text)
        expected = {
            'nsubj': [('first version', 0)],
            'verbs': [('detect', 52)],
            'obj': [('cone detection module', 17), ('cones', 60), ('input images', 71), ('the trained network', 93)]
        }

        nsubj, verbs, obj = create_svo_lists(doc)

        self.assertEqual(expected.get('nsubj'), nsubj)
        self.assertEqual(expected.get('verbs'), verbs)
        self.assertEqual(expected.get('obj'), obj)
