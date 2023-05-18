from __future__ import annotations

import os.path
import pathlib
import typing


def files_in_dir(
    directory: pathlib.Path,
) -> typing.List[str | bytes | typing.Any] | None:
    files = []
    for root, dir, file in os.walk(directory):
        for f in file:
            files.append(os.path.join(root, f))
    return files
