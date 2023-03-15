from __future__ import annotations

import os.path
import pathlib
import types
import typing

from src.application.text_provider import TextProvider


class FileManager:
    def __init__(self, file_size_limit):
        self.file_size_limit = file_size_limit
        self.text_provider = TextProvider()

    @staticmethod
    def files_in_dir(
        directory: pathlib.Path,
    ) -> typing.List[str | bytes | typing.Any] | None:
        files = []
        for root, dir, file in os.walk(directory):
            for f in file:
                files.append(os.path.join(root, f))
        return files

    def decode_text(self, file: pathlib.Path) -> str | typing.Generator[str, None, None]:
        if os.path.getsize(file) < self.file_size_limit:
                return self.text_provider.get_file_content(file)
        return self.text_provider.get_file_chunk(file)

    def save_parsed_text(self, destination: pathlib.Path, parsed_text: str | typing.Generator[str, None, None]) -> None:
        with open(destination, 'w') as fd:
            if isinstance(parsed_text, types.GeneratorType):
                for text in parsed_text:
                    fd.write(text)
            else:
                fd.write(parsed_text)
