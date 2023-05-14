from __future__ import annotations

import pathlib
from typing import List

from nlp.svo import SVO


def read_resource(file: str | pathlib.Path) -> List[str]:
    with open(file) as fd:
        content = fd.read().split()
    return content


def svo_triples(svo_ls: List[str]) -> List[SVO]:
    triples = []
    for svo in svo_ls:
        svo_obj = SVO()
        svo_obj.subj = svo.split()[0]
        svo_obj.verb = svo.split()[1]
        svo_obj.obj = " ".join(svo.split()[2:])
        triples.append(svo_obj)
    return triples
