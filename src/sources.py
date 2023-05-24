import os
import pathlib

SOURCES = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
NLP = SOURCES.joinpath("nlp")
APP = SOURCES.joinpath("application")
DATABASE = SOURCES.joinpath("database")
KNOWLEDGE_GRAPH = SOURCES.joinpath("knowledge_graph")
PLUGINS = SOURCES.joinpath("plugins")
