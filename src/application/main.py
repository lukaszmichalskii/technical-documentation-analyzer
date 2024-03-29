from __future__ import annotations

import argparse
import logging
import os.path
import pathlib
import shutil
import sys
import traceback
import typing

import stardog
from rdflib import Graph

from src.config.config import Config
from src.database.stardog_connection import StardogConnection
from src.knowledge_graph.make_rdf_triples import convert_to_rdf, make_turtle_syntax
from src.nlp.nlp_job_runner import NLPJobRunner
from src.application import common, decompression, logs
from src.application.common import (
    STEPS_CHOICES,
    STEPS,
    STANDARD_STEPS,
    NLP_PIPELINE_JOBS,
    SKIP_DECODING,
    RESULTS_FORMAT,
    PLUGIN_DEFAULT_PATH,
    PIPELINE_CHOICES,
    GRAPH_FORMAT,
)
from src.application.decompression import DecompressionError, NotSupportedArchiveFormat
from src.application.plugin_executor import execute_plugin
from src.application.file_manager import files_in_dir


def get_help_epilog():
    return """
Exit codes:
    0 - successful execution
    1 - known error connected with application requirements.
    3 - plugin failed to decode provided files.
    4 - no information was extracted during analysis, check your NLP pipeline setup.
    any other code indicated unrecoverable error - output might be invalid
    
Environment variables:
    IN_MEMORY_FILE_SIZE : Maximum file size that can be loaded into program memory in bytes.
                          If file size is greater than resource limit then content is broken down into smaller pieces.
                          Default: 1MB
    MODEL               : Language model used for NLP pipeline. For better accuracy 'en_core_web_lg'.
                          For performance 'en_core_web_sm'
                          Default: en_core_web_lg
    USE_CUDA            : If set to 1 system utilize CUDA platform during execution, otherwise CPU cores 
                          will handle calculations. Requires CUDA configuration, gives much better performance even on
                          large language models.
                          Default: 0
    STARDOG_ENDPOINT    : Stardog database endpoint URL
    STARDOG_USERNAME    : Stardog database username
    STARDOG_PASSWORD    : Stardog database password
                          
Examples:
    Autodetect what to do
    python skg_app.py --techdoc_path input_path --output results_dir --db_name database_name
    Decompress only files
    python skg_app.py --techdoc_path example.zip --output results_dir --only decompress
    Information extraction only, abandon graph serialization
    python skg_app.py --techdoc_path example.zip --only decompress decode information_extraction
    TF-IDF analysis only 
    python skg_app.py --techdoc_path docs.pdf --pipeline term_frequencies_inverse_document_frequency
    Provide custom text processing plugin
    python skg_app.py --techdoc_path input_path --plugin custom_plugin.py
    
More info: https://github.com/lukaszmichalskii/Samsung-KPZ/blob/master/MANUAL.md"""


def extracted_path(results_dir: pathlib.Path) -> pathlib.Path:
    extracted = results_dir.joinpath("extracted")
    if not extracted.exists():
        extracted.mkdir()
    return extracted


def decoded_path(results_dir: pathlib.Path) -> pathlib.Path:
    decoded = results_dir.joinpath("decoded")
    if not decoded.exists():
        decoded.mkdir()
    return decoded


def nlp_path(results_dir: pathlib.Path, subdir: str | pathlib.Path) -> pathlib.Path:
    info = results_dir.joinpath("information").joinpath(subdir)
    if not info.exists():
        os.makedirs(info)
    return info


def graph_path(results_dir: pathlib.Path, subdir: str | pathlib.Path) -> pathlib.Path:
    graph = results_dir.joinpath("graph").joinpath(subdir)
    if not graph.exists():
        os.makedirs(graph)
    return graph


def make_graph_step(svo, spo):
    triples = list()
    triples.extend(svo)
    triples.extend(spo)
    rdf_triples = convert_to_rdf(triples)
    turtle = make_turtle_syntax(rdf_triples)
    graph = Graph()
    graph.parse(data=turtle, format="turtle")
    return graph


def run_app(
    args: argparse.Namespace,
    argv: typing.List[str],
    logger: logging.Logger,
    environment: common.Environment,
) -> int:
    def decompress_step() -> None:
        extracted = extracted_path(output)
        logger.info(
            f"Decompressing files from {str(techdoc_path)} to {str(extracted)}..."
        )
        decompression.decompress(techdoc_path, extracted)

    def copy_step() -> None:
        logger.info(f"Nothing to be decompressed.")
        if techdoc_path.is_dir():
            decompression.copydir(techdoc_path, extracted_path(output))
        else:
            shutil.copy2(techdoc_path, extracted_path(output))

    def decode_step() -> None:
        for file in files_in_dir(output):
            try:
                file = pathlib.Path(file)
                if file.suffix in SKIP_DECODING:
                    shutil.copyfile(file, decoded_path(output).joinpath(file.name))
                    continue
                logger.info(f"Decoding {file.name}...")
                execute_plugin(
                    plugin_path,
                    file,
                    decoded_path(output).joinpath(file.stem + RESULTS_FORMAT),
                )
                logger.info(f"{file} file has been parsed successfully.")
            except Exception:
                logger.warning(
                    f"Unable to decode, skipping {file.name} file. Details: {traceback.format_exc()}"
                )
                continue

    def information_extraction_step():
        nlp_analizer = NLPJobRunner(
            logger,
            pipeline=args.pipeline,
            model=environment.spacy_model,
            tfidf_param=args.tfidf,
            compile_on=environment.processing_unit,
            operating_system=environment.os,
        )
        for file in files_in_dir(decoded_path(output)):
            with open(file, encoding="utf-8") as fd:
                text = fd.read()
            filename = pathlib.Path(file)
            nlp_dir = nlp_path(output, subdir=filename.stem)
            logger.info(
                f"NLP module started. Processing {filename.name} documentation."
            )
            tfidf, spo, svo = nlp_analizer.execute(
                text,
                save=nlp_dir.joinpath(f"{filename.stem}.png")
                if args.visualize
                else None,
            )
            if not tfidf and not spo and not svo:
                logger.error("No information was extracted.")
                logger.info("App finished with exit code 4")
                return sys.exit(4)
            if tfidf:
                with open(nlp_dir.joinpath(f"{filename.stem}_tfidf.txt"), "w") as fd:
                    for data in tfidf:
                        fd.write(f"{data[0]}: {data[1]}\n")
            if spo:
                with open(nlp_dir.joinpath(f"{filename.stem}_spo.txt"), "w") as fd:
                    for triple in spo:
                        fd.write(
                            f"{triple.subj};{triple.pred};{triple.obj};{triple.subj_attrs};{triple.obj_attrs};{triple.subj_ner};{triple.obj_ner}\n"
                        )
            if svo:
                with open(nlp_dir.joinpath(f"{filename.stem}_svo.txt"), "w") as fd:
                    for triple in svo:
                        fd.write(
                            f"{triple.subj};{triple.verb};{triple.obj};{triple.subj_ner};{triple.obj_ner}\n"
                        )
            if STEPS.MAKE_GRAPH in args.only:
                logger.info("Preparing RDF triples...")
                try:
                    graph_dir = graph_path(output, subdir=filename.stem)
                    graph = make_graph_step(svo, spo)
                    graph.serialize(
                        graph_dir.joinpath(f"{filename.stem}{GRAPH_FORMAT}"),
                        format="turtle",
                    )
                except Exception as e:
                    logger.error(
                        "Failed to generate RDF graph representation. Details: {}".format(
                            str(e)
                        )
                    )
            nlp_analizer.reset()

    def upload_to_database() -> None:
        with StardogConnection(Config(), args.db_name) as conn:
            conn.begin()
            for file in files_in_dir(output.joinpath("graph")):
                try:
                    file = pathlib.Path(file)
                    logger.info(f"Uploading {file.name} to {args.db_name} database...")
                    conn.add(stardog.content.File(str(file)))
                    logger.info(f"{file.name} file has been uploaded successfully.")
                except Exception:
                    logger.warning(
                        f"Unable to upload {file.name} file. Details: {traceback.format_exc()}"
                    )
                    continue
            conn.commit()

    if common.get_current_os() != "linux":
        logger.warning(
            f"You are using toolkit on {common.get_current_os()}. Some functionalities may not work correctly"
        )
    logger.info(
        f"pythonApp: {sys.executable} argv: {argv} {environment.to_info_string()}"
    )
    if os.path.exists(args.output) and os.listdir(args.output):
        logger.error(f"Output directory {args.output} is not empty")
        logger.info("App finished with exit code 1")
        return 1

    techdoc_path = pathlib.Path(args.techdoc_path)
    output = pathlib.Path(args.output)
    plugin_path = pathlib.Path(args.plugin)
    if not output.exists():
        output.mkdir()
    if STEPS.DECOMPRESS not in args.only:
        logger.error(f"Missing required step: 'decompress'.")
        logger.info("App finished with exit code 1")
        return 1
    if not args.db_name:
        logger.warning(f"Missing required arg: 'db_name'.")
    if STEPS.DECOMPRESS in args.only:
        try:
            if (
                techdoc_path.is_dir()
                or techdoc_path.suffix in common.SUPPORTED_DOCUMENTS
            ):
                copy_step()
            else:
                decompress_step()
        except (
            DecompressionError,
            NotSupportedArchiveFormat,
        ) as e:
            logger.error(str(e))
            logger.info("App finished with exit code 1")
            return 1
    if STEPS.DECODE in args.only:
        decode_step()
    if STEPS.INFORMATION_EXTRACTION in args.only:
        if len(files_in_dir(decoded_path(output))) == 0:
            logger.error("Plugin failed to decode provided files, nothing to analyze.")
            logger.info("App finished with exit code 3")
            return 3
        if args.visualize:
            logger.warning(
                "Deprecation: 'visualize' argument will be removed, use visualization utility in Stardog."
            )
        logger.info("Information extraction...")
        information_extraction_step()
    if STEPS.UPLOAD_GRAPH in args.only:
        if args.db_name:
            upload_to_database()
    logger.info("App finished with exit code 0")
    return 0


def main(argv: typing.List[str], logger=None, environment=None) -> int:
    if logger is None:
        logger = logs.setup_logger()
    if environment is None:
        environment = common.Environment.from_env(os.environ)
    parser = argparse.ArgumentParser(
        description="Technical Documentation Analyzer (TDA) - automatically create knowledge graph from technical documentation content",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--techdoc_path",
        type=str,
        required=True,
        help="path to the compressed documentation file/s (.zip and .tar.xz compressed only), directory with already decompressed files or single file (supported document formats: .pdf, .docx)",
        metavar="path",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        help="path to the text processing plugin",
        metavar="path",
        default=PLUGIN_DEFAULT_PATH,
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=STEPS_CHOICES,
        default=STANDARD_STEPS,
        help="""specifies actions which should be performed on input package:
    'decompress' - decompress files from archive pointed by --techdoc_path to the directory pointed by --output
    'decode'     - decode extracted files, cleanup text for NLP processing.
    'information_extraction' - natural language processing for information extraction.
    'make_graph' - create RDF based graph file.
    'upload_graph' - upload graph file to Stardog database pointed by --db_name.
    """,
    )
    parser.add_argument(
        "--pipeline",
        nargs="+",
        choices=PIPELINE_CHOICES,
        default=NLP_PIPELINE_JOBS,
        help="""specifies actions which should be performed on preprocessed text in NLP step, be default whole pipeline is executed:
    "clean" - text pre-processing
    "crosslingual_coreference" - AllenNLP CoReference resolution for entity linking
    "term_frequencies_inverse_document_frequency" - term frequencies inverse document frequency analysis
    "tokenize" - sentence tokenize
    "topic_modeling" - optional data given human knowledge about topic by --human-knowledge (user dependent).
    "content_filtering" - content filtering based on TFIDF step (and optional TOPIC_MODELING data)
    "batch" - obtain batch from document by filter out sentence with length not in defined threshold
    "subject_verb_object" - subject-verb-object triples extraction
    "subject_predicate_object" - subject-predicate-object triples extraction
    "named_entity_recognition" - named entity recognition, classification and description generation
    """,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="output_folder",
        default="results",
        help="specifies directory, where results should be saved. Has to be empty",
    )
    parser.add_argument(
        "--tfidf",
        type=int,
        default=5,
        help="specifies how many words to pick from TF-IDF results for topic modeling",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="save graph visualization from 'information_extraction' job",
    )
    parser.add_argument(
        "--db_name",
        help="name of the database to upload graph to",
    )
    parser.epilog = get_help_epilog()
    return run_app(parser.parse_args(argv[1:]), argv, logger, environment)
