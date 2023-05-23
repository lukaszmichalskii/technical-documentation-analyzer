import spacy

from src.sources import NLP

MODEL = spacy.load("en_core_web_sm")
try:
    NER = spacy.load(NLP.joinpath("models/ner"))
except IOError:
    NER = None
