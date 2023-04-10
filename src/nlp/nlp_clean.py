import re

from src.nlp.build import non_nc


def remove_special_characters(text: str) -> str:
    """
    Hack for IO read pre-cleaned text
    Args:
        text: pre-cleaned text from text-parse module
    Returns:
        Clean text
    """
    regex = re.compile(r'[\n\r\t]')
    clean_text = regex.sub(" ", text)
    return clean_text


def remove_stop_words_and_punct(text: str, print_text: bool = False) -> str:
    """
    Clean-up unnecessary expressions
    Args:
        text: information to clean
        print_text: debug output
    Returns:
        Cleaned text e.g.
         in  > Camera recognition is a component of control pipeline of SEE part of autonomous system.
         out > Camera recognition component control pipeline autonomous system
    """
    result_ls = []
    rsw_doc = non_nc(text)
    for token in rsw_doc:
        if print_text:
            print(token, token.is_stop)
            print('--------------')
        if not token.is_stop and not token.is_punct:
            result_ls.append(str(token))
    result_str = ' '.join(result_ls)
    return result_str
