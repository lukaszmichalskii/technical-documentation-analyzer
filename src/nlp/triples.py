from __future__ import annotations

import dataclasses
from typing import List


@dataclasses.dataclass
class SVO:
    """struct for storing SVO triples"""

    subj: str = ""
    verb: str = ""
    obj: str = ""
    subj_ner: str = ""
    obj_ner: str = ""

    def invalid(self):
        if self.subj == "" or self.obj == "":
            return True
        return False

    def __eq__(self, other: SVO):
        if (
            self.subj == other.subj
            and self.obj == other.obj
            and self.verb == other.verb
        ):
            return True
        return False

    def __lt__(self, other: SVO):
        return self.subj < other.subj

    def __hash__(self):
        return hash((self.subj, self.obj, self.verb))


@dataclasses.dataclass
class SPO:
    """struct for storing SPO triples"""

    subj: str = ""
    subj_attrs: str | List[str] = ""
    pred: str = ""
    obj: str = ""
    obj_attrs: str | List[str] = ""

    def __eq__(self, other: SPO):
        if (
            self.subj == other.subj
            and self.obj == other.obj
            and self.pred == other.pred
        ):
            return True
        return False

    def __lt__(self, other: SPO):
        return self.subj < other.subj

    def __hash__(self):
        return hash((self.subj, self.obj, self.pred))


@dataclasses.dataclass
class WordAttr:
    """struct for storing relations between text parts"""

    word: str = ""
    attributes: List[str] = dataclasses.field(default_factory=lambda: [])

    def __eq__(self, other):
        return self.word == other.word and self.attributes == other.attributes
