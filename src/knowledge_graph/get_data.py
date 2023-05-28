import os

from src.knowledge_graph.make_rdf_triples import convert_to_rdf, make_turtle_syntax, make_graph
from src.nlp.triples import SVO, SPO

full_path = os.path.join(os.path.dirname(os.getcwd()), "results\information")


def get_results(path):
    """
        Get files with '.txt' extension form "results/information directory
        Args:
            path: full path to the corresponding directory
        Returns:
            turtle_file: turtle file of a graph for each information
    """

    svo = []
    spo = []
    for directory, subdirectory, files in os.walk(path):
        for file in files:
            file_path = os.path.join(directory, file)
            if file.endswith("_svo.txt"):
                svo = convert_txt_to_svo(file_path)
            elif file.endswith("_spo.txt"):
                spo = convert_txt_to_spo(file_path)

        if svo != [] or spo != []:
            triples = svo + spo
            svo = []
            spo = []

            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            file_name = file_name.split("_")[0]
            make_graph(make_turtle_syntax(convert_to_rdf(triples)), file_name)


def convert_txt_to_svo(file_path):
    """
        Converts a '.txt' file to svo triples
        Args:
            file_path: full path to the corresponding file
        Returns:
            svo_list: list of svo triples
    """

    file = open(file_path, "r")
    svo_list = []
    for line in file:
        line = line.strip()
        if line:
            elem_svo = line.split(';')
            svo = SVO(subj=elem_svo[0].strip(),
                      verb=elem_svo[1].strip(),
                      obj=elem_svo[2].strip(),
                      subj_ner=elem_svo[3].strip(),
                      obj_ner=elem_svo[4].strip())
            svo_list.append(svo)

    return svo_list


def convert_txt_to_spo(file_path):
    """
        Converts a '.txt' file to spo triples
        Args:
            file_path: full path to the corresponding file
        Returns:
            spo_list: list of spo triples
    """

    file = open(file_path, "r")
    spo_list = []
    for line in file:
        line = line.strip()
        if line:
            elem_spo = line.split(';')
            spo = SPO(subj=elem_spo[0].strip(),
                      pred=elem_spo[1].strip(),
                      obj=elem_spo[2].strip(),
                      subj_attrs=elem_spo[3].strip(),
                      obj_attrs=elem_spo[4].strip(),
                      subj_ner=elem_svo[5].strip(),
                      obj_ner=elem_svo[6].strip())
            spo_list.append(spo)

    return spo_list


get_results(full_path)