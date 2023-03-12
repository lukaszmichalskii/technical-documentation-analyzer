from __future__ import annotations

import pathlib
import typing

from src.application.text_parse import remove_escape_chars, read_file, PDFExtractor


class NotSupportedDocumentFormat(Exception):
    pass


class FileManager:
    def __init__(self):
        self.supported_formats = [".doc", ".docx", ".pdf", ".txt"]
        self.pdf_extractor = PDFExtractor()

    def process_file(self, filepath: pathlib.Path) -> typing.Generator[str]:
        if filepath.suffix not in self.supported_formats:
            raise NotSupportedDocumentFormat
        if filepath.suffix == ".pdf":
            buffer_ = self.pdf_extractor.extract_pdf(filepath)
            while True:
                try:
                    page = remove_escape_chars(next(buffer_))
                    yield page
                except StopIteration:
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
