from __future__ import annotations

import re
from typing import List, Tuple, Optional, Set

import nltk.tokenize
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from scipy.stats import norm
from spacy import Language

from src.nlp.tfidf import FUNCTION_WORDS
from src.nlp.triples import SVO, SPO
from src.nlp.triples import WordAttr

SUBJECT = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECT = ["dobj", "pobj"]
NOUN_PREP = ["NOUN", "PROPN", "PRON"]
VERB = "VERB"
ADJ = "ADJ"

"""workaround for in-person system references in documentation
e.g. we execute external tool -> system execute external tool
"""
PRONOUNS = ["i", "you", "he", "she", "it", "we", "they"]
RESOLVED = "System"


"""named entity linking
"""
LIBRARY = ["LIBRARY"]
ALGORITHM = ["ALGORITHM", "KALMAN FILTER", "YOLO", "SLAM"]
SENSOR = ["SENSOR"]
SOFTWARE = ["ROBOTIC OPERATING SYSTEM", "SOFTWARE"]
PROGRAMMING_LANGUAGE = ["PROGRAMMING LANGUAGE"]
EXECUTION_UNIT = ["COMPUTING PLATFORM", "PROCESSING UNIT"]


def content_filtering(sentences: List[str], patterns: List[str]):
    content_related = list()
    for sentence in sentences:
        for pattern in patterns:
            if (
                re.search(pattern, sentence, re.IGNORECASE) is not None
                and sentence not in content_related
            ):
                content_related.append(sentence)
    return content_related


def threshold(distribution: List[int]) -> Tuple[int, int]:
    mean, _ = norm.fit(distribution)
    return 2, int(mean + mean * 2)


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


def svo(text: List[str], model: Language) -> Set[SVO]:
    svo_ls = list()
    for sent in text:
        svo_ls.extend(svo_extract(sent, model))
    return set(svo_ls)


def svo_extract(text: str, model: Language) -> List[SVO]:
    corpus = model(text)
    svo_ls = []
    for token in corpus:
        if token.pos_ == VERB:  # assume root node
            phrase = ""
            for sub_tok in token.lefts:
                if sub_tok.dep_ in SUBJECT and sub_tok.pos_ in NOUN_PREP:
                    adj = adj_noun(text, sub_tok.i, model)
                    phrase += adj + " " + sub_tok.text
                    phrase += " " + token.lemma_
                    # check for noun or pronoun direct objects
                    for sub_tok in token.rights:
                        if sub_tok.dep_ in OBJECT and sub_tok.pos_ in NOUN_PREP:
                            adj = adj_noun(text, sub_tok.i, model)
                            phrase += adj + " " + sub_tok.text
                            svo_ls.append(phrase.strip())
    return svo_triples(svo_ls, model)


def svo_triples(svo_ls: List[str], model: Language) -> List[SVO]:
    triples = []
    for svo in svo_ls:
        svo_obj = SVO()
        if len(svo.split()) == 3:
            subj, verb, obj = svo.split()
            svo_obj.subj = RESOLVED if subj.lower() in PRONOUNS else subj
            svo_obj.verb = verb
            svo_obj.obj = RESOLVED if obj.lower() in PRONOUNS else obj
        else:
            dep_tree = model(svo)
            is_verb_detected = False
            for token in dep_tree:
                if token.pos_ == "VERB" or token.dep_ == "ROOT":
                    svo_obj.verb = token.text
                    is_verb_detected = True
                    continue
                if not is_verb_detected:
                    if not svo_obj.subj:
                        svo_obj.subj = (
                            token.text
                            if token.text.lower() not in PRONOUNS
                            else RESOLVED
                        )
                    else:
                        svo_obj.subj = " ".join([svo_obj.subj, token.text])
                else:
                    if not svo_obj.obj:
                        svo_obj.obj = (
                            token.text
                            if token.text.lower() not in PRONOUNS
                            else RESOLVED
                        )
                    else:
                        svo_obj.obj = " ".join([svo_obj.obj, token.text])
        if svo_obj.invalid():
            continue
        if svo_obj in triples:
            continue
        triples.append(svo_obj)
    return triples


def spo(text: List[str], tagger: CoreNLPParser) -> Set[SPO]:
    spo_ls = list()
    for sent in text:
        triplet = spo_extract(sent, tagger)
        if triplet and triplet not in spo_ls:
            spo_ls.append(triplet)
    return set(spo_ls)


def spo_extract(text: str, tagger: CoreNLPParser) -> Optional[SPO]:
    (dependency_tree,) = ParentedTree.convert(
        list(tagger.parse(nltk.tokenize.word_tokenize(text)))[0]
    )
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
    for tree in dependency_tree.subtrees(lambda x: x.label() == "NP"):
        for sub_tree in tree.subtrees(lambda y: y.label().startswith("NN")):
            root = sub_tree[0]
            subj_info = WordAttr(word=root, attributes=get_attributes(sub_tree))
            if subj_info not in subject:
                subject.append(subj_info)
    return subject[0] if len(subject) != 0 else None


def find_predicate(dependency_tree: ParentedTree) -> Optional[WordAttr]:
    output, predicate = None, []
    for tree in dependency_tree.subtrees(lambda x: x.label() == "VP"):
        for sub_tree in tree.subtrees(lambda y: y.label().startswith("VB")):
            root = sub_tree[0]
            output = WordAttr(word=root, attributes=get_attributes(sub_tree))
            if output is not None and output not in predicate:
                predicate.append(output)
    return predicate[-1] if len(predicate) != 0 else None


def find_obj(dependency_tree: ParentedTree) -> Optional[WordAttr]:
    objects, output, word = [], None, []
    for tree in dependency_tree.subtrees(lambda x: x.label() == "VP"):
        for sub_tree in tree.subtrees(lambda y: y.label() in ["NP", "PP", "ADP"]):
            if sub_tree.label() in ["NP", "PP"]:
                for sub_sub_tree in sub_tree.subtrees(
                    lambda z: z.label().startswith("NN")
                ):
                    word = sub_sub_tree
            else:
                for sub_sub_tree in sub_tree.subtrees(
                    lambda z: z.label().startswith("JJ")
                ):
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
    if word.label().startswith("JJ"):
        for p in word.parent():
            if p.label() == "RB":
                attrs.append(p[0])
    elif word.label().startswith("NN"):
        for p in word.parent():
            if p.label() in ["DT", "PRP$", "POS", "JJ", "CD", "ADJP", "QP", "NP"]:
                attrs.append(p[0])
    elif word.label().startswith("VB"):
        for p in word.parent():
            if p.label() == "ADVP":
                attrs.append(p[0])
    # word's tree uncles
    if word.label().startswith("NN") or word.label().startswith("JJ"):
        for p in word.parent().parent():
            if p.label() == "PP" and p != word.parent():
                attrs.append(" ".join(p.flatten()))
    elif word.label().startswith("VB"):
        for p in word.parent().parent():
            if p.label().startswith("VB") and p != word.parent():
                attrs.append(" ".join(p.flatten()))
    clean_attrs = []
    for attr in attrs:
        attr_ = attr.lower() if isinstance(attr, str) else attr.label().lower()
        if attr_ not in FUNCTION_WORDS:
            clean_attrs.append(attr_)
    return clean_attrs


def named_entity_recognition(text: str, model: Language) -> Set[SVO]:
    ner = model(text)
    svo_ls = list()
    for entity in ner.ents:
        if entity.label_ in ALGORITHM or entity.label_ in SOFTWARE:
            svo_ls.append(
                SVO(
                    subj=RESOLVED,
                    verb="use",
                    obj=entity.text,
                    subj_ner=RESOLVED.upper(),
                    obj_ner=entity.label_,
                )
            )
        elif entity.label_ in LIBRARY:
            svo_ls.append(
                SVO(
                    subj=RESOLVED,
                    verb="depend on",
                    obj=entity.text,
                    subj_ner=RESOLVED.upper(),
                    obj_ner=entity.label_,
                )
            )
        elif entity.label_ in EXECUTION_UNIT:
            svo_ls.append(
                SVO(
                    subj=RESOLVED,
                    verb="utilize",
                    obj=entity.text,
                    subj_ner=RESOLVED.upper(),
                    obj_ner=entity.label_,
                )
            )
    return set(svo_ls)
