from __future__ import annotations

import pathlib
import re
import typing

import PyPDF2


def read_file(file_obj: typing.IO, chunk_size: int = 1024 * 32) -> str | bytes:
    """
    Read file content to memory buffer
    Args:
        file_obj: file descriptor
        chunk_size: memory buffer size, default is 32KiB
    Returns:
         buffer filled with file_obj content
    """
    while True:
        text = file_obj.read(chunk_size)
        if not text:
            break
        yield text


def remove_escape_chars(string_: str) -> str:
    """
    Strip string with escape characters e.g. tabs, newlines, terminated chars
    Args:
        string_: text to clean up
    Returns:
        parsed text without escape characters
    """
    escape_chars = r"\s+"
    return re.sub(escape_chars, " ", string_).strip()


class PDFExtractor:
    def __init__(self):
        self.page_ptr = -1

    def extract_pdf(self, pdf_file: pathlib.Path) -> typing.Generator[str]:
        """
        Decode and extract PDF file content page by page
        Args:
            pdf_file: path to PDF encoded file
        Returns:
            decoded page content
        """
        with open(pdf_file, "rb") as pdf_:
            pdf_reader = PyPDF2.PdfReader(pdf_)
            self.page_ptr += 1
            while self.page_ptr < len(pdf_reader.pages):
                yield pdf_reader.pages[self.page_ptr].extract_text()

    def reset(self):
        self.page_ptr = 0
