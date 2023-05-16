from __future__ import annotations

import pathlib
from typing import List

from nlp.triples import SVO


PRONOUNS = ["i", "you", "he", "she", "it", "we", "they"]


def read_resource(file: str | pathlib.Path) -> List[str]:
    with open(file) as fd:
        content = fd.read().split()
    return content


def svo_triples(svo_ls: List[str]) -> List[SVO]:
    triples = []
    for svo in svo_ls:
        svo_obj = SVO()

        subj, verb, *obj = svo.split()
        svo_obj.subj = (
            subj if subj.lower() not in PRONOUNS else "system"
        )  # workaround for in-person system description
        svo_obj.verb = verb
        svo_obj.obj = " ".join(obj)
        triples.append(svo_obj)
    return triples
