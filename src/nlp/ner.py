import numpy as np

from src.nlp.build import nlp
from src.nlp.google_kgs import google_search
from src.nlp.svo import create_svo_triples


def get_obj_properties(tup_ls):
    init_obj_tup_ls = []

    for tup in tup_ls:
        try:
            text, node_label_ls, url = google_search(tup[2], limit=1)
            new_tup = (tup[0], tup[1], tup[2], text[0], node_label_ls[0], url[0])
        except Exception:
            new_tup = (tup[0], tup[1], tup[2], [], [], [])

        init_obj_tup_ls.append(new_tup)

    return init_obj_tup_ls


def add_layer(tup_ls):
    svo_tup_ls = []

    for tup in tup_ls:

        if tup[3]:
            svo_tup = create_svo_triples(tup[3])
            svo_tup_ls.extend(svo_tup)
        else:
            continue

    return get_obj_properties(svo_tup_ls)


def subj_equals_obj(tup_ls):
    new_tup_ls = []

    for tup in tup_ls:
        if tup[0] != tup[2]:
            new_tup_ls.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))

    return new_tup_ls


def check_for_string_labels(tup_ls):
    """
    This is for an edge case where the object does not get fully populated
    resulting in the node labels being assigned to string instead of list.
    This may not be strictly necessary and the lines using it are commented out
    below.
    Args:
        tup_ls: SVO triples list
    Returns:
        Fully populated SVO triples with NER
    """
    clean_tup_ls = []

    for el in tup_ls:
        if isinstance(el[2], list):
            clean_tup_ls.append(el)

    return clean_tup_ls


def create_word_vectors(tup_ls):
    """
    Create word to vec embeddings.
    For reliable work requires 'en_core_web_md' or 'en_core_web_lg' spacy langauge model
    Args:
        tup_ls: SVO triples list
    Returns:
        SVO triples enhanced with vectors embeddings
    """
    new_tup_ls = []

    for tup in tup_ls:
        if tup[3]:
            doc = nlp(tup[3])
            new_tup = (tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], doc.vector)
        else:
            new_tup = (
            tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], np.random.uniform(low=-1.0, high=1.0, size=(300,)))
        new_tup_ls.append(new_tup)

    return new_tup_ls
