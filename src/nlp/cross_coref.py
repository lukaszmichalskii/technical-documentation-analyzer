from spacy import Language


def cross_coref(text: str, model: Language) -> str:
    """
    Apply AllenNLP CoReference resolution for entity linking
    Args:
        model: neural coreference resolution model
        text: pre-processed corpus
    Returns: resolved text
    """
    coref = model(text)
    return coref._.resolved_text
