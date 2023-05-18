from __future__ import annotations

import dataclasses
from typing import List


@dataclasses.dataclass
class SVO:
    """struct for storing SVO triples"""

    subj: str = ""
    verb: str = ""
    obj: str = ""
    subj_ner: List[str] = dataclasses.field(default_factory=list)
    obj_ner: List[str] = dataclasses.field(default_factory=list)

    def invalid(self):
        if self.subj == "" or self.obj == "":
            return True
        return False


@dataclasses.dataclass
class SPO:
    """struct for storing SPO triples"""

    subj: str = ""
    subj_attrs: str | List[str] = ""
    pred: str = ""
    obj: str = ""
    obj_attrs: str | List[str] = ""


@dataclasses.dataclass
class WordAttr:
    """struct for storing relations between text parts"""

    word: str = ""
    attributes: List[str] = dataclasses.field(default_factory=lambda: [])

    def __eq__(self, other):
        return self.word == other.word and self.attributes == other.attributes
