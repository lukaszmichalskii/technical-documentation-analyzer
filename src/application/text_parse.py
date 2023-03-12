from __future__ import annotations

import abc
import docx
import pathlib
import re
import typing
from abc import abstractmethod

import PyPDF2


def read_file(
    file_obj: typing.IO[str], chunk_size: int = 1024 * 32
) -> typing.Generator[str, None, None]:
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


class Decoder(abc.ABC):
    """
    Base class for files decoding
    """

    def __init__(self) -> None:
        self.head = -1

    @abstractmethod
    def read(self, file: pathlib.Path) -> typing.Generator[str, None, None]:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class PDFDecoder(Decoder):
    """
    Decoder class providing method for reading .pdf based content only.
    """

    def __init__(self) -> None:
        super().__init__()

    def read(self, pdf_file: pathlib.Path) -> typing.Generator[str, None, None]:
        """
        Decode and extract PDF file content page by page
        Args:
            pdf_file: path to PDF encoded file
        Returns:
            decoded page content
        """
        with open(pdf_file, "rb") as pdf_:
            pdf_reader = PyPDF2.PdfReader(pdf_)
            self.head += 1
            while self.head < len(pdf_reader.pages):
                yield pdf_reader.pages[self.head].extract_text()

    def reset(self) -> None:
        self.head = 0


class WordDecoder(Decoder):
    """
    Decoder class providing method for reading .docx based content only.
    By now class does not take into consideration images, tables and other MS Word structures.
    """

    def __init__(self) -> None:
        super().__init__()

    def read(self, word_file: pathlib.Path) -> typing.Generator[str, None, None]:
        """
        Decode and extract .docx file content paragraph by paragraph.
        .doc format not supported by now
        Args:
            word_file: path to .docx encoded file
        Returns:
            decoded paragraph content
        """
        docx_ = docx.Document(word_file)
        self.head += 1
        while self.head < len(docx_.paragraphs):
            yield docx_.paragraphs[self.head].text

    def reset(self) -> None:
        self.head = 0
