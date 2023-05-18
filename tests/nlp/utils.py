import spacy
from nltk import CoreNLPParser

MODEL = spacy.load('en_core_web_sm')
TAGGER = CoreNLPParser(url="http://0.0.0.0:9000", tagtype="pos")


def tag(*tags):
    def decorator(obj):
        setattr(obj, 'tags', set(tags))
        return obj
    return decorator
