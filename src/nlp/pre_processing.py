import re


def remove_whitespace_characters(text: str) -> str:
    return re.sub(r"[\n\r\t]", " ", text)


def remove_unicode(text: str) -> str:
    return re.sub(
        r"(@\[A-Za-z0-9]+)|(\s+)|([^0-9A-Za-z\.\,\-\_\(\)\: \t])|(\w+:\/\/\S+)|^rt|http+?",
        " ",
        text,
    )
