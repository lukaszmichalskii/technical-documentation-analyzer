from typing import List, Tuple

import spacy
import crosslingual_coreference
from spacy import Language

from src.sources import NLP
from src.application.common import PIPELINE


def compile_nlp(model: str, pipeline: List[str]) -> Tuple[Language, Language]:
    lang = spacy.load(model)
    ner = None
    if PIPELINE.CROSS_COREF in pipeline:
        lang.add_pipe(
            "xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": -1}
        )
    if PIPELINE.NER in pipeline:
        ner = spacy.load(NLP.joinpath("models/ner"))
    return lang, ner
