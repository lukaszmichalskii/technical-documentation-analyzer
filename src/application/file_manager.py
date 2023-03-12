from __future__ import annotations

import pathlib
import typing

from src.application.text_parse import remove_escape_chars, read_file, PDFDecoder, WordDecoder


class NotSupportedDocumentFormat(Exception):
    pass


class FileManager:
    def __init__(self):
        self.supported_formats = [".doc", ".docx", ".pdf", ".txt"]
        self.pdf_extractor = PDFDecoder()
        self.word_extractor = WordDecoder()

    def process_file(self, filepath: pathlib.Path) -> typing.Generator[str]:
        if filepath.suffix not in self.supported_formats:
            raise NotSupportedDocumentFormat
        if filepath.suffix == ".pdf":
            buffer_ = self.pdf_extractor.read(filepath)
            while True:
                try:
                    page = remove_escape_chars(next(buffer_))
                    yield page
                except StopIteration:
                    self.pdf_extractor.reset()
                    break
        elif filepath.suffix == ".txt":
            with open(filepath, "r") as fd:
                buffer_ = read_file(fd)
                while True:
                    try:
                        text = remove_escape_chars(next(buffer_))
                        yield text
                    except StopIteration:
                        break
        elif filepath.suffix == ".docx" or filepath.suffix == '.doc':
            buffer_ = self.word_extractor.read(filepath)
            while True:
                try:
                    text = remove_escape_chars(next(buffer_))
                    yield text
                except StopIteration:
                    self.word_extractor.reset()
                    break
