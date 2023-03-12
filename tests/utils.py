from __future__ import annotations

import os
import pathlib
from typing import List, Any


def files_in_dir(directory: pathlib.Path) -> List[str | bytes | Any] | None:
    files = []
    for _, _, filenames in os.walk(directory):
        files.extend(filenames)
    if files:
        return files
    return None
