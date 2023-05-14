from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class SVO:
    """struct for storing SVO triples
    """
    subj: str = ""
    verb: str = ""
    obj: str = ""
