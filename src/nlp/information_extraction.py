import re
from typing import List, Tuple, Optional

import nltk.tokenize
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from scipy.stats import norm
from spacy import Language

from nlp.tfidf import FUNCTION_WORDS
from nlp.triples import SVO, SPO
from nlp.triples import WordAttr
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


def spo(text: str, tagger: CoreNLPParser) -> Optional[SPO]:
    dependency_tree, = ParentedTree.convert(list(tagger.parse(nltk.tokenize.word_tokenize(text)))[0])
    subject = find_subj(dependency_tree)
    predicate = find_predicate(dependency_tree)
    objects = find_obj(dependency_tree)
    if (subject is not None) and (predicate is not None) and (objects is not None):
        triplet = SPO()
        triplet.subj = subject.word
        if subject.attributes:
            triplet.subj_attrs = subject.attributes
        triplet.pred = predicate.word
        triplet.obj = objects.word
        if objects.attributes:
            triplet.obj_attrs = objects.attributes
        if triplet.subj == triplet.obj:
            return None
        return triplet
    return None


def find_subj(dependency_tree: ParentedTree) -> Optional[WordAttr]:
    subject = []
    for tree in dependency_tree.subtrees(lambda x: x.label() == 'NP'):
        for sub_tree in tree.subtrees(lambda y: y.label().startswith('NN')):
            root = sub_tree[0]
            subj_info = WordAttr(word=root, attributes=get_attributes(sub_tree))
            if subj_info not in subject:
                subject.append(subj_info)
    return subject[0] if len(subject) != 0 else None


def find_predicate(dependency_tree: ParentedTree) -> Optional[WordAttr]:
    output, predicate = None, []
    for tree in dependency_tree.subtrees(lambda x: x.label() == 'VP'):
        for sub_tree in tree.subtrees(lambda y: y.label().startswith('VB')):
            root = sub_tree[0]
            output = WordAttr(word=root, attributes=get_attributes(sub_tree))
            if output is not None and output not in predicate:
                predicate.append(output)
    return predicate[-1] if len(predicate) != 0 else None


def find_obj(dependency_tree: ParentedTree) -> Optional[WordAttr]:
    objects, output, word = [], None, []
    for tree in dependency_tree.subtrees(lambda x: x.label() == 'VP'):
        for sub_tree in tree.subtrees(lambda y: y.label() in ['NP', 'PP', 'ADP']):
            if sub_tree.label() in ['NP', 'PP']:
                for sub_sub_tree in sub_tree.subtrees(lambda z: z.label().startswith('NN')):
                    word = sub_sub_tree
            else:
                for sub_sub_tree in sub_tree.subtrees(lambda z: z.label().startswith('JJ')):
                    word = sub_sub_tree
            if len(word) != 0:
                root = word[0]
                output = WordAttr(word=root, attributes=get_attributes(word))
            if output is not None and output not in objects:
                objects.append(output)
    return objects[0] if len(objects) != 0 else None


def get_attributes(word) -> List[str]:
    attrs = []
    # word's tree siblings
    if word.label().startswith('JJ'):
        for p in word.parent():
            if p.label() == 'RB':
                attrs.append(p[0])
    elif word.label().startswith('NN'):
        for p in word.parent():
            if p.label() in ['DT', 'PRP$', 'POS', 'JJ', 'CD', 'ADJP', 'QP', 'NP']:
                attrs.append(p[0])
    elif word.label().startswith('VB'):
        for p in word.parent():
            if p.label() == 'ADVP':
                attrs.append(p[0])
    # word's tree uncles
    if word.label().startswith('NN') or word.label().startswith('JJ'):
        for p in word.parent().parent():
            if p.label() == 'PP' and p != word.parent():
                attrs.append(' '.join(p.flatten()))
    elif word.label().startswith('VB'):
        for p in word.parent().parent():
            if p.label().startswith('VB') and p != word.parent():
                attrs.append(' '.join(p.flatten()))
    clean_attrs = []
    for attr in attrs:
        attr_ = attr.lower() if isinstance(attr, str) else attr.label().lower()
        if attr_ not in FUNCTION_WORDS:
            clean_attrs.append(attr_)
    return clean_attrs


