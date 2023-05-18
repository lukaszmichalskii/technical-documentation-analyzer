from rdflib import Graph
from src.nlp.triples import SVO

example = [SVO(subj='Simultaneous localization', verb='create', obj='map', subj_ner=['jak', 'wół'], obj_ner=[]),
           SVO(subj='system', verb='', obj='Simultaneous localization', subj_ner=[], obj_ner=[]),
           SVO(subj='system', verb='represent', obj='map object', subj_ner=[], obj_ner=[]),
           SVO(subj='Landmark', verb='represent', obj='various things', subj_ner=[], obj_ner=[]),
           SVO(subj='SLAM', verb='give', obj='good results', subj_ner=[], obj_ner=['jak']),
           SVO(subj='approach', verb='have', obj='big advantage', subj_ner=[], obj_ner=[]),
           SVO(subj='particles', verb='share', obj='same history', subj_ner=[], obj_ner=[]),
           SVO(subj='particle', verb='create', obj='new path', subj_ner=[], obj_ner=[])]


def convert_to_rdf(triple_list):
    """
    Converts SVO triples into RDF triples as turtle syntax
    Args:
        triple_list: SVO triples
    Returns:
        rdf_triples: turtle syntax of RDF triples
    """

    rdf_triples = []

    for triple in triple_list:
        subject = triple.subj.replace(" ", "_")
        verb = triple.verb.replace(" ", "_")
        object = triple.obj.replace(" ", "_")

        subject_ner = triple.subj_ner
        for sub in subject_ner:
            sub.replace(" ", "_")

        object_ner = triple.obj_ner
        for ob in object_ner:
            ob.replace(" ", "_")

        if verb:
            rdf_triples.append(f":{subject} :{verb} :{object} .")

        if subject_ner:
            for item in subject_ner:
                rdf_triples.append(f":{subject} rdf:type :{item} .")

        if object_ner:
            for item in object_ner:
                rdf_triples.append(f":{object} rdf:type :{item} .")

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


def make_graph(turtle):
    """
    Serializes graph and creates file with knowledge graph as turtle syntax
    Args:
        turtle: turtle syntax before serialization
    """
    graph = Graph()
    graph.parse(data=turtle, format='turtle')
    graph.serialize('KG.ttl', format='turtle')


if __name__ == "__main__":
    x = convert_to_rdf(example)
    t = make_turtle_syntax(x)
    make_graph(t)
