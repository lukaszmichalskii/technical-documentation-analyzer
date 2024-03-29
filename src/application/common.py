from platform import platform

from src.sources import PLUGINS


def enum(**params):
    return type("Enum", (), params)


########################################################################################################################
###################################### APPLICATION PIPELINE ############################################################
########################################################################################################################

STEPS = enum(
    DECOMPRESS="decompress",
    DECODE="decode",
    INFORMATION_EXTRACTION="information_extraction",
    MAKE_GRAPH="make_graph",
    UPLOAD_GRAPH="upload_graph",
)

STEPS_CHOICES = [
    STEPS.DECOMPRESS,
    STEPS.DECODE,
    STEPS.INFORMATION_EXTRACTION,
    STEPS.MAKE_GRAPH,
    STEPS.UPLOAD_GRAPH,
]
STANDARD_STEPS = [
    STEPS.DECOMPRESS,
    STEPS.DECODE,
    STEPS.INFORMATION_EXTRACTION,
    STEPS.MAKE_GRAPH,
    STEPS.UPLOAD_GRAPH,
]

SUPPORTED_ARCHIVES = {".zip", ".tar.xz", ".xz"}
SUPPORTED_DOCUMENTS = {".docx", ".pdf", ".txt"}
SKIP_DECODING = [".txt"]  # assume txt file contains standard charset
RESULTS_FORMAT = ".txt"
GRAPH_FORMAT = ".ttl"

PLUGIN_DEFAULT_PATH = PLUGINS.joinpath("default_plugin.py")

########################################################################################################################
############################### NATURAL LANGUAGE PROCESSING PIPELINE ###################################################
########################################################################################################################

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
    NER="named_entity_recognition",  # named entity recognition, classification and description generation
)

PIPELINE_CHOICES = [
    PIPELINE.CLEAN,
    PIPELINE.CROSS_COREF,
    PIPELINE.TFIDF,
    PIPELINE.TOKENIZE,
    PIPELINE.TOPIC_MODELING,
    PIPELINE.CONTENT_FILTERING,
    PIPELINE.BATCH,
    PIPELINE.SVO,
    PIPELINE.SPO,
    PIPELINE.NER,
]

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
    PIPELINE.NER,
]


########################################################################################################################
############################################ END PIPELINES #############################################################
########################################################################################################################


def get_current_os() -> str:
    if is_linux_os():
        return "linux"
    return "windows"


def is_linux_os() -> bool:
    return platform().find("Linux") != -1


def computation_platform(code: int) -> str:
    if code == 1:
        return "CUDA"
    return "CPU"


class Environment:
    """
    Class for storing user specific configuration overwritten using environmental variables
    """

    def __init__(self, env):
        self.in_memory_file_limit = int(env.get("IN_MEMORY_FILE_SIZE", 1024 * 1024))
        self.spacy_model = env.get("MODEL", "en_core_web_lg")
        self.processing_unit = computation_platform(int(env.get("USE_CUDA", 0)))
        self.os = get_current_os()

    @staticmethod
    def from_env(env):
        return Environment(env)

    def to_info_string(self):
        return (
            "os: {}, " + "in_memory_file_limit: {}, " + "model: {}, " + "running on: {}"
        ).format(
            self.os, self.in_memory_file_limit, self.spacy_model, self.processing_unit
        )
