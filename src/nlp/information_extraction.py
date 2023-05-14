import re
from typing import List, Tuple

import nltk.tokenize
import spacy
from scipy.stats import norm
from spacy import Language
from spacy.tokens.doc import Doc

from nlp.svo import SVO
from nlp.utils import svo_triples


SUBJECT = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECT = ["dobj", "pobj"]
NOUN_PREP = ['NOUN', 'PROPN', 'PRON']
VERB = "VERB"
ADJ = "ADJ"


def content_filtering(sentences: List[str], patterns: List[str]):
    content_related = list()
    for sentence in sentences:
        for pattern in patterns:
            if re.search(pattern, sentence, re.IGNORECASE) is not None and sentence not in content_related:
                content_related.append(sentence)
    return content_related


def threshold(distribution: List[int]) -> Tuple[int, int]:
    mean, _ = norm.fit(distribution)
    return 2, int(mean+mean*2)


def filter_sents(sentences: List[str]):
    distribution = list()
    for sent in sentences:
        words = nltk.tokenize.word_tokenize(sent)
        distribution.append(len(words))

    # filter
    lower_bound, upper_bound = threshold(distribution)
    filtered_sents = list()
    for sent in sentences:
        if lower_bound < len(nltk.tokenize.word_tokenize(sent)) < upper_bound:
            filtered_sents.append(sent)
    return filtered_sents


def adj_noun(text: str, index: int, model: Language) -> str:
    doc = model(text)
    phrase = ""
    for token in doc:
        if token.i == index:
            for child in token.children:
                if child.pos_ == ADJ:
                    phrase += " " + child.text
            break
    return phrase


def svo(text: str, model: Language) -> List[SVO]:
    corpus = model(text)
    svo_ls = []
    for token in corpus:
        if token.pos_ == VERB:  # assume root node
            phrase = ""
            for sub_tok in token.lefts:
                if sub_tok.dep_ in SUBJECT and sub_tok.pos_ in NOUN_PREP:
                    adj = adj_noun(text, sub_tok.i, model)
                    phrase += adj + ' ' + sub_tok.text
                    phrase += ' ' + token.lemma_
                    # check for noun or pronoun direct objects
                    for sub_tok in token.rights:
                        if sub_tok.dep_ in OBJECT and sub_tok.pos_ in NOUN_PREP:
                            adj = adj_noun(text, sub_tok.i, model)
                            phrase += adj + ' ' + sub_tok.text
                            svo_ls.append(phrase.strip())

    return svo_triples(svo_ls)


