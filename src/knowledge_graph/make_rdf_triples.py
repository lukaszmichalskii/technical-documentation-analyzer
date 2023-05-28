import os
import requests
from rdflib import Graph
from src.nlp.triples import SVO, SPO


def is_svo(triple):
    return isinstance(triple, SVO)


def is_spo(triple):
    return isinstance(triple, SPO)


def convert_to_rdf(triple_list):
    """
    Converts SVO and SPO triples into RDF triples as turtle syntax
    Args:
        triple_list: SVO triples
    Returns:
        rdf_triples: turtle syntax of RDF triples
    """

    rdf_triples = []
    link = "https://dbpedia.org/resource/"

    for triple in triple_list:
        subject = triple.subj.replace(" ", "_")
        object = triple.obj.replace(" ", "_")
        link_subject = link + subject.capitalize()
        link_object = link + object.capitalize()

        if is_svo(triple):
            subject_attrs = False
            object_attrs = False
            verb = triple.verb.replace(" ", "_")

            subject_ner = triple.subj_ner
            if type(subject_ner) is list:
                for sub in subject_ner:
                    sub.replace(" ", "_")
            else:
                subject_ner = subject_ner.replace(" ", "_")

            object_ner = triple.obj_ner
            if type(object_ner) is list:
                for ob in object_ner:
                    ob.replace(" ", "_")
            else:
                object_ner = object_ner.replace(" ", "_")
        else:
            verb = triple.pred.replace(" ", "_")

            subject_attrs = triple.subj_attrs
            object_attrs = triple.obj_attrs

            subject_ner = triple.subj_ner
            if type(subject_ner) is list:
                for sub in subject_ner:
                    sub.replace(" ", "_")
            else:
                subject_ner = subject_ner.replace(" ", "_")

            object_ner = triple.obj_ner
            if type(object_ner) is list:
                for ob in object_ner:
                    ob.replace(" ", "_")

        if verb:
            rdf_triples.append(f":{subject} :{verb} :{object} .")

        responseS = requests.get(link_subject, timeout=5)
        responseO = requests.get(link_object, timeout=5)

        if responseS.status_code == 200:
            rdf_triples.append(f":{subject} rdfs:seeAlso <{link_subject}> .")
        if responseO.status_code == 200:
            rdf_triples.append(f":{object} rdfs:seeAlso <{link_object}> .")

        if subject_ner:
            if type(subject_ner) is list:
                for item in subject_ner:
                    rdf_triples.append(f":{subject} rdf:type :{item} .")
            else:
                rdf_triples.append(f":{subject} rdf:type :{subject_ner} .")

        if object_ner:
            if type(object_ner) is list:
                for item in object_ner:
                    rdf_triples.append(f":{object} rdf:type :{item} .")
            else:
                rdf_triples.append(f":{object} rdf:type :{object_ner} .")

        if subject_attrs:
            if type(subject_attrs) is list:
                for item in subject_attrs:
                    rdf_triples.append(f":{subject} rdfs:comment \"{item}\" .")
            else:
                rdf_triples.append(f":{subject} rdfs:comment \"{subject_attrs}\" .")

        if object_attrs:
            if type(object_attrs) is list:
                for item in object_attrs:
                    rdf_triples.append(f":{object} rdfs:comment \"{item}\" .")
            else:
                rdf_triples.append(f":{object} rdfs:comment \"{object_attrs}\" .")

    return rdf_triples


def make_turtle_syntax(rdf_triples):
    """
    Makes turtle file with rdf triples and prefixes
    Args:
        rdf_triples: rdf triples in turtle syntax
    Returns:
        turtle_syntax: turtle file of a graph
    """

    prefix = "http://api.stardog.com/"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xsd = "http://www.w3.org/2001/XMLSchema#"
    rdfs = "http://www.w3.org/2000/01/rdf-schema#"
    turtle_syntax = f"PREFIX : <{prefix}>\nPREFIX rdf: <{rdf}>\nPREFIX xsd: <{xsd}>\nPREFIX rdfs: <{rdfs}>\n"
    for triple in rdf_triples:
        turtle_syntax += triple + "\n"

    return turtle_syntax


def make_graph(turtle, name):
    """
    Serializes graph and creates file with knowledge graph as turtle syntax
    Args:
        turtle: turtle syntax before serialization
        name: name of an output file
    """

    graph_directory = os.path.join(os.path.dirname(os.getcwd()), "src\\results\\graph")
    if not os.path.exists(graph_directory):
        os.makedirs(graph_directory)

    directory_path = os.path.join(graph_directory, name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    name += ".ttl"
    file_path = os.path.join(directory_path, name)

    graph = Graph()
    graph.parse(data=turtle, format='turtle')
    graph.serialize(file_path, format='turtle')
