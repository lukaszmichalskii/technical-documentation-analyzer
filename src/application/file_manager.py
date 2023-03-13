from __future__ import annotations

import os.path
import pathlib
import typing

from application.text_provider import TextProvider


def print_file_content(
    filename, text: str | typing.Generator[str, None, None], chunk: bool = False
):
    # helper function for debugging purposes
    if chunk:
        print("-" * 50)
        print(f"{filename}:")
        for t in text:
            print(t, sep="")
        print("-" * 50)
        return
    print("-" * 50)
    print(f"{filename}:")
    print(text)
    print("-" * 50)


class FileManager:
    def __init__(self, file_size_limit):
        self.file_size_limit = file_size_limit
        self.text_provider = TextProvider()

    @staticmethod
    def files_in_dir(
        directory: pathlib.Path,
    ) -> typing.List[str | bytes | typing.Any] | None:
        files = []
        for _, _, filenames in os.walk(directory):
            files.extend(filenames)
        return files

    def get_text(self, file: pathlib.Path):
        if os.path.getsize(file) < self.file_size_limit:
            text = self.text_provider.get_file_content(file)
            print_file_content(file.name, text)
            return
        text = self.text_provider.get_file_chunk(file)
        print_file_content(file.name, text, chunk=True)
