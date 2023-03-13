from __future__ import annotations

import logging
import pathlib
import typing

from src.application.text_parse import (
    remove_escape_chars,
    read_file,
    PDFDecoder,
    DocxDecoder,
)


LOGGER = logging.getLogger("SKG")


class NotSupportedDocumentFormat(Exception):
    pass


class TextProvider:
    """
    Class for handling single input - single output by reading textual content from files.
    """

    def __init__(self) -> None:
        self.supported_formats = [".docx", ".pdf", ".txt"]
        self.pdf_extractor = PDFDecoder()
        self.docx_extractor = DocxDecoder()

    def supported_format(self, extension) -> bool:
        return extension in self.supported_formats

    def get_file_content(self, filepath: pathlib.Path) -> str:
        """
        Read whole single .pdf, .docx, and standard .txt file to program memory
        Args:
            filepath: path to file
        Returns:
            decoded and cleaned text from provided file.
        """
        if filepath.suffix == ".pdf":
            with open(filepath, "rb") as pdf_:
                return self._read_all(pdf_, self.pdf_extractor.read_all)
        elif filepath.suffix == ".txt":
            with open(filepath, "r") as txt_:
                return remove_escape_chars(txt_.read())
        elif filepath.suffix == ".docx":
            with open(filepath, "rb") as docx_:
                return self._read_all(docx_, self.docx_extractor.read_all)

    def _read_all(
        self, fd, buffer_read_fn: typing.Callable[[typing.IO[str | bytes]], str]
    ) -> str:
        """
        Read from buffer stream str or bytes and clean up decoded content
        Args:
            fd: file descriptor
            buffer_read_fn: function to read buffer stream
        Returns:
            text without escape characters
        """
        return remove_escape_chars(buffer_read_fn(fd))

    def get_file_chunk(
        self, filepath: pathlib.Path
    ) -> typing.Generator[str, None, None]:
        """
        Read single .pdf, .docx, and standard .txt file content chunks
        Args:
            filepath: path to file
        Returns:
            decoded and cleaned text chunks from provided file.
        """
        if not self.supported_format(filepath.suffix):
            LOGGER.error(f"Document {filepath.suffix} format is not supported.")
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
