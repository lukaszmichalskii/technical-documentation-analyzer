from __future__ import annotations

import pathlib
from typing import List

from spacy import Language

from src.nlp.triples import SVO

""" workaround for in-person system references in documentation
e.g. we execute external tool -> system execute external tool
"""
PRONOUNS = ["i", "you", "he", "she", "it", "we", "they"]
RESOLVED = "System"


def read_resource(file: str | pathlib.Path) -> List[str]:
    with open(file) as fd:
        content = fd.read().split()
    return content


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
