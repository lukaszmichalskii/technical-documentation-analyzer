import pathlib
import time
from typing import List, Tuple

import networkx as nx
import nltk.tokenize
import pandas as pd
from matplotlib import pyplot as plt
from nltk import CoreNLPParser

from nlp.compile import compile_nlp
from nlp.cross_coref import cross_coref
from nlp.information_extraction import content_filtering, filter_sents, svo, spo
from src.application.common import NLP_PIPELINE_JOBS, PIPELINE
from nlp.pre_processing import remove_special_characters, remove_unicode
from nlp.tfidf import tfidf
from nlp.triples import SVO, SPO


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
    def __init__(self, logger, pipeline=None, model="en_core_web_sm"):
        self.logger = logger
        self.pipeline = NLP_PIPELINE_JOBS if pipeline is None else pipeline
        self.pos_tagger = CoreNLPParser(url="http://0.0.0.0:9000", tagtype="pos")
        try:
            self.pos_tagger.parse("Validation phase")
        except Exception:
            if PIPELINE.SPO in self.pipeline:
                self.pipeline.remove(PIPELINE.SPO)
                self.logger.warn(
                    "CoreNLP engine is not working, skipping SPO extraction step."
                )
        self.logger.info("Compiling NLP pipeline toolkit...")
        self.lang, self.ner = compile_nlp(model, self.pipeline)
        self.logger.info(f"Toolkit loaded successfully: model {model}")

        # docs file text
        self.documentation = None

        # pipeline variables
        self.tfidf = list()
        self.human_knowledge = list()
        self.sentences = list()
        self.filtered_content = list()
        self.svo = list()
        self.spo = list()

        # parameters
        self.tfidf_top = 5

    def execute(
        self, text: str, save: pathlib.Path = None
    ) -> Tuple[List[SPO], List[SVO]]:
        self.documentation = text
        start = time.time()
        if PIPELINE.CLEAN in self.pipeline:
            self.documentation = remove_special_characters(self.documentation)
            self.documentation = remove_unicode(self.documentation)
            self.logger.info(
                f"Text preprocessing execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn("Skipping text preprocessing job.")
        start = time.time()
        if PIPELINE.CROSS_COREF in self.pipeline:
            self.documentation = cross_coref(self.documentation, self.lang)
            self.logger.info(
                f"Coreference resolution execution time: {time.time() - start:.2f}s"
            )
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
            self.logger.error(f"Invalid pipeline setup, {PIPELINE.TOKENIZE} not found.")
            return list(), list()
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
            for sent in self.sentences:
                svo_triples = svo(sent, self.lang)
                if len(svo_triples) > 0:
                    self.svo.extend(svo_triples)
            self.logger.info(
                f"SVO triples extraction execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "SVO triples extraction not utilized in information extraction process."
            )
        start = time.time()
        if PIPELINE.SPO in self.pipeline:
            for sent in self.sentences:
                spo_triple = spo(sent, self.pos_tagger)
                if spo_triple and spo_triple not in self.spo:
                    self.spo.append(spo_triple)
            self.logger.info(
                f"SPO triples extraction execution time: {time.time() - start:.2f}s"
            )
        else:
            self.logger.warn(
                "SPO triples extraction not utilized in information extraction process."
            )
        if PIPELINE.NPN in self.pipeline:
            self.logger.info(
                "Extracting additional information is not implemented yet."
            )
        # if PIPELINE.NER in self.pipeline:
        #     self.logger.info("Named entity recognition was run on pretrained model specified for autonomous cars."
        #                      "If documentation is not related with topic process will not have impact on results.")
        if save:
            dummy_save(self.svo, self.spo, save)

        return self.spo, self.svo


if __name__ == "__main__":
    jr = NLPJobRunner(None)
    text = """Camera recognition is a component of control pipeline of SEE part of autonomous system.
It is responsible for detecting objects in real time and creating field of cones for further use in path planner.
Camera recognition is a ROS2 node running on autonomous system main unit (NVIDIA Jetson AGX Xavier)."""
    spo_, svo_ = jr.execute(text)
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
    plt.show()
