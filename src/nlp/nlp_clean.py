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


def remove_duplicates(tup, tup_pos):
    """
    Recognize 'object' (in SVO the O) position to avoid redundant memory allocation in graph assembly
    Args:
        tup: precomputed SVO list
        tup_pos: position to comparison
    Returns:
        Unique list of SVO triples
    """
    check_val = set()
    result = []

    for i in tup:
        if i[tup_pos] not in check_val:
            result.append(i)
            check_val.add(i[tup_pos])

    return result


def remove_literals(tup_ls):
    """
    Get rid of literals from SVO triple list in further RDF assembly
    Args:
        tup_ls: list of SVO triples
    Returns:
        List without literal objects (in SVO the O)
    """
    clean_tup_ls = []
    for entry in tup_ls:
        if not entry[2].isdigit():
            clean_tup_ls.append(entry)
    return clean_tup_ls
