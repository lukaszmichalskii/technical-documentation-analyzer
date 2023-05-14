from typing import List

import spacy
import crosslingual_coreference
from spacy import Language

from nlp.pipeline import PIPELINE


def compile_nlp(model: str, pipeline: List[str]) -> Language:
    lang = spacy.load(model)
    if PIPELINE.CROSS_COREF in pipeline:
        lang.add_pipe(
            "xx_coref",
            config={"chunk_size": 2500, "chunk_overlap": 2, "device": -1}
        )
    return lang
