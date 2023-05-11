from spacy import tokens

from src.nlp.build import nlp
from src.nlp.nlp_clean import (
    remove_stop_words_and_punct,
    remove_special_characters,
    remove_duplicates,
    remove_literals,
)

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
VERBS = ["ROOT", "advcl"]
OBJECTS = ["dobj", "dative", "attr", "oprd", "pobj"]


def create_svo_lists(doc: tokens.doc.Doc, debug: bool = False):
    """
    Classification [subject, verb, object] from spacy doc
    Args:
        doc: spacy doc from text
        debug: debug flag
    Returns:
        Tuple containing lists of classified objects:
        (subject, verb, object)
    """
    subject_ls = []
    verb_ls = []
    object_ls = []

    for token in doc:
        if token.dep_ in SUBJECTS:
            subject_ls.append((token.lower_, token.idx))
        elif token.dep_ in VERBS:
            verb_ls.append((token.lemma_, token.idx))
        elif token.dep_ in OBJECTS:
            object_ls.append((token.lower_, token.idx))

    if debug:
        print("SUBJECTS: ", subject_ls)
        print("VERBS: ", verb_ls)
        print("OBJECTS: ", object_ls)

    return subject_ls, verb_ls, object_ls


def create_svo_triples(text, debug=False):
    """
    SVO triples extraction procedure.
    'Verb recognize' utility based on closest words algorithm
    Args:
        text: information to parse
        debug: debug flag
    Returns:
        SVO triples in tuple: (subject, verb (lemma), object)
    """

    clean_text = remove_special_characters(text)
    doc = nlp(clean_text)
    subject_ls, verb_ls, object_ls = create_svo_lists(doc, debug=debug)

    graph_tup_ls = []
    for subj in subject_ls:
        for obj in object_ls:
            dist_ls = []
            for v in verb_ls:
                dist_ls.append(abs(obj[1] - v[1]))

            index_min = min(range(len(dist_ls)), key=dist_ls.__getitem__)

            # Remove stop words from subjects and object. Note that this is done a bit
            # later down in the process to allow for proper sentence recognition.
            no_sw_subj = remove_stop_words_and_punct(subj[0])
            no_sw_obj = remove_stop_words_and_punct(obj[0])

            # Add entries to the graph if neither subject nor object is blank
            if no_sw_subj and no_sw_obj:
                tup = (no_sw_subj, verb_ls[index_min][0], no_sw_obj)
                graph_tup_ls.append(tup)

        # clean_tup_ls = remove_dates(graph_tup_ls)

    dedup_tup_ls = remove_duplicates(graph_tup_ls, 2)
    clean_tup_ls = remove_literals(dedup_tup_ls)
    return clean_tup_ls
