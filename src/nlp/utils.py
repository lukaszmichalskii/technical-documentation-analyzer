from __future__ import annotations

import pathlib
from typing import List


def read_resource(file: str | pathlib.Path) -> List[str]:
    with open(file) as fd:
        content = fd.read().split()
    return content
