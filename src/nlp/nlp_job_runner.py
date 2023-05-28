import pathlib
import time
from typing import Tuple, Set, List

import networkx as nx
import nltk.tokenize
import pandas as pd
from matplotlib import pyplot as plt
from nltk import CoreNLPParser

from src.application import logs
from src.application.common import NLP_PIPELINE_JOBS, PIPELINE
from src.nlp.compile import compile_nlp
from src.nlp.cross_coref import cross_coref
from src.nlp.information_extraction import (
    content_filtering,
    filter_sents,
    svo,
    spo,
    named_entity_recognition,
)
from src.nlp.pre_processing import remove_whitespace_characters, remove_unicode
from src.nlp.tfidf import tfidf
from src.nlp.triples import SVO, SPO


def dummy_save(svo_, spo_, file):
    edge = []
    subj = []
    obj = []
    for s in spo_:
        if s.obj_attrs:
            for a in s.obj_attrs:
                subj.append(s.subj)
                edge.append(s.pred)
                obj.append(" ".join([s.obj, a]))
        else:
            subj.append(s.subj)
            edge.append(s.pred)
            obj.append(s.obj)

    subj1 = [s.subj for s in svo_]
    edge1 = [s.verb for s in svo_]
    obj1 = [s.obj for s in svo_]

    kg_df = pd.DataFrame(
        {"subject": subj + subj1, "object": obj + obj1, "edge": edge1 + edge}
    )

    G = nx.from_pandas_edgelist(
        kg_df, "subject", "object", edge_attr=True, create_using=nx.MultiDiGraph()
    )
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True, node_color="skyblue", edge_cmap=plt.cm.Blues, pos=pos)
    nx.draw_networkx_edge_labels(G, pos=pos)
    plt.savefig(file)


class NLPJobRunner:
    def __init__(
        self,
        logger,
        tfidf_param: int = 5,
        pipeline=None,
        model="en_core_web_sm",
        compile_on: str = "CPU",
        operating_system: str = "linux",
    ):
        self.logger = logger
        self.pipeline = NLP_PIPELINE_JOBS if pipeline is None else pipeline
        url = (
            "http://localhost:9000/"
            if operating_system != "linux"
            else "http://0.0.0.0:9000"
        )
        self.pos_tagger = CoreNLPParser(url=url, tagtype="pos")
        try:
            self.pos_tagger.parse("Validation phase")
        except Exception:
            if PIPELINE.SPO in self.pipeline:
                self.pipeline.remove(PIPELINE.SPO)
                self.logger.warn(
                    "CoreNLP engine is not working, skipping SPO extraction step."
                )
        self.logger.info("Compiling NLP pipeline toolkit...")
        self.lang, self.ner = compile_nlp(model, self.pipeline, compile_on)
        self.logger.info(f"Toolkit loaded successfully: model {model}")

        # docs file text
        self.documentation = None

        # pipeline variables
        self.tfidf = list()
        self.human_knowledge = list()
        self.sentences = list()
        self.filtered_content = list()
        self.svo = set()
        self.spo = set()

        # parameters
        self.tfidf_top = tfidf_param

    def execute(
        self, text: str, save: pathlib.Path = None
    ) -> Tuple[List[Tuple[str, int]], Set[SPO], Set[SVO]]:
        self.documentation = text
        start = time.time()
        if PIPELINE.CLEAN in self.pipeline:
            self.documentation = remove_whitespace_characters(self.documentation)
            self.documentation = remove_unicode(self.documentation)
            self.logger.info(
                f"Text preprocessing execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn("Skipping text preprocessing job.")
        start = time.time()
        if PIPELINE.CROSS_COREF in self.pipeline:
            try:
                self.documentation = cross_coref(self.documentation, self.lang)
                self.logger.info(
                    f"Coreference resolution execution time: {time.time() - start:.2f}s"
                )
            except RuntimeError as e:
                self.logger.error(str(e))
                return list(), set(), set()
        else:
            self.logger.warn(
                "Skipping coreference resolution, linked entities might be corrupted."
            )
        start = time.time()
        if PIPELINE.TFIDF in self.pipeline:
            self.tfidf = tfidf(self.documentation)
            self.tfidf_top = (
                self.tfidf_top
                if self.tfidf_top < len(self.tfidf)
                else len(self.tfidf) - 1
            )
            self.logger.info(
                f"Term frequencies inverse document frequency analysis execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "Skipping term frequencies inverse document frequency analysis."
            )
        start = time.time()
        if PIPELINE.TOKENIZE in self.pipeline:
            self.sentences = nltk.tokenize.sent_tokenize(self.documentation)
            self.logger.info(
                f"Sentence tokenization execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.error(
                f"Invalid pipeline setup, {PIPELINE.TOKENIZE} not found, required for further execution."
            )
            self.pipeline = []
        start = time.time()
        if PIPELINE.TOPIC_MODELING in self.pipeline and self.human_knowledge:
            pattern = [subject for subject in self.human_knowledge]
            self.filtered_content = content_filtering(self.sentences, pattern)
            self.logger.info(
                f"Topic modelling execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "Skipping topic modelling based on human knowledge (user does not provided subject matter info)."
            )
        start = time.time()
        if PIPELINE.CONTENT_FILTERING in self.pipeline:
            top_occur = [
                content_word[0] for content_word in self.tfidf[: self.tfidf_top]
            ]
            content_filtered = content_filtering(self.sentences, top_occur)
            if len(self.filtered_content) > 0:
                self.filtered_content.extend(content_filtered)
            else:
                self.filtered_content = content_filtered
            self.logger.info(
                f"Content filtering execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "Content filtering based on document additional TFIDF or human knowledge data not invoked."
            )
        start = time.time()
        if PIPELINE.BATCH in self.pipeline:
            self.sentences = filter_sents(self.sentences)
            self.sentences.extend(
                [sent for sent in self.filtered_content if sent not in self.sentences]
            )
            self.logger.info(
                f"Batch data based on document structure analysis procedure execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn("Further processing will be performed on unfiltered data.")
        start = time.time()
        if PIPELINE.SVO in self.pipeline:
            self.svo = svo(self.sentences, self.lang, self.ner)
            self.logger.info(
                f"SVO triples extraction execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "SVO triples extraction not utilized in information extraction process."
            )
        start = time.time()
        if PIPELINE.SPO in self.pipeline:
            self.spo = spo(self.sentences, self.pos_tagger, self.ner)
            self.logger.info(
                f"SPO triples extraction execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "SPO triples extraction not utilized in information extraction process."
            )
        start = time.time()
        if PIPELINE.NER in self.pipeline:
            self.logger.warn(
                "Named entity recognition run on pre-trained model specified for autonomous cars industry. "
                "If documentation is not related to topic, results might be corrupted. "
                "Consider turning off NER job from Information Extraction pipeline."
            )
            named_entities = named_entity_recognition(self.documentation, self.ner)
            if named_entities:
                self.svo.update(named_entities)
            self.logger.info(
                f"Named Entities Recognition execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn("Named Entity Recognition analysis was not executed.")

        if save and (self.svo or self.spo):
            dummy_save(self.svo, self.spo, save)

        return self.tfidf, self.spo, self.svo

    def reset(self):
        # docs file text
        self.documentation = None

        # pipeline variables
        self.tfidf = list()
        self.human_knowledge = list()
        self.sentences = list()
        self.filtered_content = list()
        self.svo = set()
        self.spo = set()


if __name__ == "__main__":
    jr = NLPJobRunner(logs.setup_logger())
    text = """Path planner is a component of control pipeline of THINK part of autonomous system"""
    tf, spo_, svo_ = jr.execute(text)
    dummy_save(svo_, spo_, "graph.png")
    for s in spo_:
        print(s)
