<br />
<p align="center">
  <a href="https://github.com/lukaszmichalskii/Samsung-KPZ">
    <img src="docs/logo.png" alt="Logo" width="200" height="200">
  </a>
  <h3 align="center">System Manual</h3>
</p>


<!-- TABLE OF CONTENTS -->
## Table of Contents
- [More About TDA](#more-about-tda)
  - [Technical Documentation Analyzer](#technical-documentation-analyzer)
  - [Deep Convolutional Neural Network](#deep-convolutional-neural-network)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Get the TDA source](#get-the-tda-source)
  - [Install Dependencies](#install-dependencies)
    - [Setup CoreNLP dependency](#setup-corenlp-dependency)
    - [NER model configuration](#ner-model-configuration)
- [Getting Started](#getting-started)
  - [Adjust running options](#adjust-running-options)
- [Copyright](#license)


## More About TDA
Technical Documentation Analyzer is an application that provides a standalone tool used
for creating knowledge-graph based on content of technical documentation.

### Technical Documentation Analyzer
Large IT projects are based on the process of translating the system description into specific modeling
languages, starting from the description of the requirements model in a natural language, through the
description of the architecture model, to the description of the system in the programming language.
The aim of the project is to automatically create a description of the system using the OWL/RDF
language based on the available technical documentation, using NLP technologies offering Named
Entities Recognition and Relations Detection mechanisms. The result of the project will be an ontology
for describing software solutions from a functional and non-functional perspective, and an automatic
mechanism for creating a Semantic Knowledge Graph based on it, describing the system based on the
knowledge contained in the technical documentation.


### Deep Convolutional Neural Network

System was designed to handle technical documentation content related with autonomous car's industry 
therefore own Named Entities Recognition CNN was developed. Model required compatibility with [spacy](https://spacy.io/) library that is why we
used spaCy as training interface. Training procedure was made on the dataset related to Formula Student series, and
documentations publicly available on the Internet, annotated using [NER Annotator for SpaCy](https://github.com/tecoholic/ner-annotator) tool.

NER model are available for download here: [ner_latest.zip](https://drive.google.com/file/d/1hWuZuLUB3ZQTjpHtGNaGeznxM-X4fWJ4/view?usp=sharing)


## Installation

Below manual is Linux dependent, running on Windows OS is possible but not recommended.

### Prerequisites
If you are installing from source, you will need:
- Python 3.8 or later, discarding 3.11, 3.12

Optional:
- Java 17 for more information extraction, and 4.5.4 release of CoreNLPServer available
here: [CoreNLP Server](https://stanfordnlp.github.io/CoreNLP/index.html)

If you want to compile with CUDA support, install the following (note that CUDA is not supported on macOS)
- [NVIDIA CUDA](https://developer.nvidia.com/cuda-downloads) 11.0 or above according to Tensorflow and PyTorch support
- [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) v7 or above
- [Compiler](https://gist.github.com/ax3l/9489132) compatible with CUDA

Note: You could refer to the [cuDNN Support Matrix](https://docs.nvidia.com/deeplearning/cudnn/pdf/cuDNN-Support-Matrix.pdf) for cuDNN versions with the various supported CUDA, CUDA driver and NVIDIA hardware

If you want to disable CUDA support, export the environment variable `USE_CUDA=0`.
Other potentially useful environment variables may be found in `main.py`.

### Get the TDA source
```bash
git clone https://github.com/lukaszmichalskii/Samsung-KPZ.git
cd Samsung-KPZ
# **** OPTIONAL: virtual environment for Python setup ****
python3 -m virtualenv venv
source venv/bin/activate
# **** END OPTIONAL ****
```

### Install Dependencies
```bash
python3 -m pip install -r build_requirements.txt
# Default model for better performance use 'en_core_web_sm' (worse accuracy).
python3 -m spacy download en_core_web_lg
```

#### Setup CoreNLP dependency
Navigate to downloaded CoreNLPServer archive and extract packages.
```bash
unzip <archive_name.zip>  # extract archive
```
Navigate to directory with extracted packages, and run below command:
```bash
# Run the server using all jars in the current directory (e.g., the CoreNLP home directory)
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
```

> _Aside:_  Server should listen on port 9000:
> ```plaintext
> [main] INFO CoreNLP - --- StanfordCoreNLPServer#main() called ---
> [main] INFO CoreNLP - Server default properties:
> 			(Note: unspecified annotator properties are English defaults)
> 			inputFormat = text
> 			outputFormat = json
> 			prettyPrint = false
> [main] INFO CoreNLP - Threads: 24
> [main] INFO CoreNLP - Starting server...
> [main] INFO CoreNLP - StanfordCoreNLPServer listening at /[0:0:0:0:0:0:0:0]:9000
> ```


#### NER model configuration
Named Entities Recognition use pre-trained model available here: [ner_latest.zip](https://drive.google.com/file/d/1hWuZuLUB3ZQTjpHtGNaGeznxM-X4fWJ4/view?usp=sharing)
NER is topic related and above CNN detect information for autonomous car's industry. To load your own model
connected with documentation follow steps below and replace mentioned model.

Navigate to `src/nlp/models` directory and create `ner` directory, then place all extracted files into that dir:
```bash
# navigate to models dir (from project root) and create ner
cd src/nlp/models && mkdir ner
# move all files from extracted model directory to ner directory
mv <extracted_model_absolute_path> ner
```
If all steps was done correctly and paths are not messed up, system on start will compile
and add NER model to information extraction pipeline.





## Getting Started

> _Aside:_ Some packages and models might be missing, system will automatically resolve missing dependencies 
and configure environment on first run.


Technical Documentation Analyzer (TDA) by default is run using standard pipeline configuration.

```bash
python3 src/skg_app.py --techdoc_path <path_to_documentation>
```

Execution could be configured using `--only` argument, this allows to specify which jobs to run. The below command will run only decompress,
decode and information_extraction steps.

```bash
python3 src/skg_app.py --techdoc_path <path_to_documentation> --only decompress decode information_extraction
```

By default, results are stored in `results` directory created in current working directory. To specify where
to store intermediate results from each module execution use `--output` argument. If destination does not 
exist system will automatically create provided directory tree.

```bash
python3 src/skg_app.py --techdoc_path <path_to_documentation> --output <path_to_output>
```

To serialize results to StarDog database provide database name with `--db_name` argument. 

```bash
python3 src/skg_app.py --techdoc_path <path_to_documentation> --db_name <database_name>
```

#### Text processing plugin

By default, application uses `src/plugins/default_plugin.py` as text processing plugin. Custom plugin can be used with --path argument.

```bash
python3 src/skg_app.py --techdoc_path <path_to_documentation> --plugin <path_to_plugin>
```

### Adjust running options

Arguments for adjusting running options:

| Argument         | Description                                                                                                                                                                        | Default                                                              |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `--techdoc_path` | Path to the compressed documentation file/s (.zip and .tar.xz compressed only), directory with already decompressed files or single file (supported document formats: .pdf, .docx) | None                                                                 |
| `--plugin`       | Path to the text parsing plugin                                                                                                                                                    | src/plugins/default_plugin.py                                        |
| `--only`         | Specifies actions which should be performed on input package                                                                                                                       | None                                                                 |
| `--pipeline`     | Specifies actions which should be performed on preprocessed text in NLP step                                                                                                       | clean cross_coref tfidf tokenize content_filtering batch svo spo ner |
| `--output`       | Specifies directory, where results should be saved. Has to be empty                                                                                                                | results                                                              |
| `--tfidf`        | Specifies how many words to pick from TF-IDF results for topic modeling                                                                                                            | 5                                                                    |
| `--db_name`      | Name of the database to upload graph to                                                                                                                                            | None                                                                 |


Other options can be set via environment variables:

| Variable            | Description                                                                                                                                                                                       | Default        |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|
| MODEL               | Language model used for Natural Langauge Processing tasks                                                                                                                                         | en_core_web_lg |
| USE_CUDA            | If set to 1 system utilize CUDA platform during execution, otherwise CPU cores will handle calculations. Requires CUDA configuration, gives much better performance even on large language models | 0              |
| IN_MEMORY_FILE_SIZE | Maximum file size that can be loaded into program memory in bytes. If file size is greater than resource limit then content is broken down into smaller pieces                                    | 1MB            |
| STARDOG_ENDPOINT    | Stardog database endpoint URL                                                                                                                                                                     | None           |
| STARDOG_USERNAME    | Stardog database username                                                                                                                                                                         | None           |
| STARDOG_PASSWORD    | Stardog database password                                                                                                                                                                         | None           |
 

## Copyright
Technical Documentation Analyzer (TDA) has a GNU license, as found in the [LICENSE](https://github.com/lukaszmichalskii/Samsung-KPZ/blob/master/LICENSE) file.