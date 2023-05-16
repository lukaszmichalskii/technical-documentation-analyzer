"""Term Frequencies Inverse Document Frequency (TFIDF) analysis
"""
from typing import List, Tuple
from nltk.tokenize import word_tokenize
from nlp import utils


SPECIAL_CHARS = utils.read_resource("nlp/resources/special_chars.txt")
FUNCTION_WORDS = utils.read_resource("nlp/resources/function_words.txt")


def tfidf(text: str) -> List[Tuple[str, int]]:
    tf = dict()
    for word in word_tokenize(text):
        word_ = word.lower()
        if word_ in FUNCTION_WORDS or word_ in SPECIAL_CHARS:
            continue
        if word_ not in tf.keys():
            tf[word_] = 1
        else:
            tf[word_] += 1

    tfidf_data = [(key, tf[key]) for key in tf.keys()]
    return sorted(tfidf_data, key=lambda info: info[1], reverse=True)
