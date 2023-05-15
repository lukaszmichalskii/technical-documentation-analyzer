"""Natural Language Processing execution pipeline
"""


def enum(**params):
    return type("Enum", (), params)


PIPELINE = enum(
    CLEAN="clean",  # text pre-processing
    CROSS_COREF="crosslingual_coreference",  # AllenNLP CoReference resolution for entity linking
    TFIDF="term_frequencies_inverse_document_frequency",  # term frequencies inverse document frequency analysis
    TOKENIZE="tokenize",  # sentence tokenize
    TOPIC_MODELING="topic_modeling",  # optional data given human knowledge about topic (user dependent)
    CONTENT_FILTERING="content_filtering",  # content filtering based on TFIDF step (and optional TOPIC_MODELING data)
    BATCH="batch",  # obtain batch from document by filter out sentence with length not in defined threshold
    SVO="subject_verb_object",  # subject-verb-object triples extraction
    SPO="subject_predicate_object",  # subject-predicate-object triples extraction
    NPN="noun_preposition_noun",  # noun-preposition-noun n-grams extraction
    NER="named_entity_recognition"  # named entity recognition, classification and description generation
)

# default pipeline steps
NLP_PIPELINE_JOBS = [
    PIPELINE.CLEAN,
    PIPELINE.CROSS_COREF,
    PIPELINE.TFIDF,
    PIPELINE.TOKENIZE,
    PIPELINE.CONTENT_FILTERING,
    PIPELINE.BATCH,
    PIPELINE.SVO,
    PIPELINE.SPO,
    PIPELINE.NPN,
    PIPELINE.NER,
]
