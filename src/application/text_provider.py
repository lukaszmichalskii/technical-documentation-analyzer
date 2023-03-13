from __future__ import annotations

import pathlib
import typing

from src.application.text_parse import (
    remove_escape_chars,
    read_file,
    PDFDecoder,
    DocxDecoder,
)


class NotSupportedDocumentFormat(Exception):
    pass


class TextProvider:
    """
    Class for handling single input - single output by reading textual content from files.
    """

    def __init__(self) -> None:
        self.supported_formats = [".docx", ".pdf", ".txt"]
        self.file_size_threshold = 1024 * 1024
        self.pdf_extractor = PDFDecoder()
        self.docx_extractor = DocxDecoder()

    def supported_format(self, extension) -> bool:
        return extension in self.supported_formats

    def get_text(self, filepath: pathlib.Path) -> typing.Generator[str, None, None]:
        """
        Read single .pdf, .docx, and standard .txt file content chunks
        Args:
            filepath: path to file
        Returns:
            decoded and cleaned text chunks from provided file.
        """
        if not self.supported_format(filepath.suffix):
            raise NotSupportedDocumentFormat
        if filepath.suffix == ".pdf":
            with open(filepath, "rb") as pdf_:
                while True:
                    try:
                        yield remove_escape_chars(next(self.pdf_extractor.read(pdf_)))
                    except StopIteration:
                        self.pdf_extractor.reset()
                        break
        elif filepath.suffix == ".txt":
            with open(filepath, "r") as fd:
                while True:
                    try:
                        yield remove_escape_chars(next(read_file(fd)))
                    except StopIteration:
                        break
        elif filepath.suffix == ".docx":
            with open(filepath, "rb") as docx_:
                while True:
                    try:
                        yield remove_escape_chars(next(self.docx_extractor.read(docx_)))
                    except StopIteration:
                        self.docx_extractor.reset()
                        break
