from __future__ import annotations

import os
import pathlib
from typing import List, Any, Union, Optional


def files_in_dir(directory: pathlib.Path) -> Optional[List[Union[str, bytes, Any]]]:
    files = []
    for _, _, filenames in os.walk(directory):
        files.extend(filenames)
    if files:
        return files
    return None
