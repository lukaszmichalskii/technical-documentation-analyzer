from rdflib import Graph
from src.nlp.triples import SVO, SPO

example = [SVO(subj='System', verb='have', obj='cones', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='use', obj='YOLOv5', subj_ner='SYSTEM', obj_ner='ALGORITHM'),
           SVO(subj='System', verb='utilize', obj='GPU', subj_ner='SYSTEM', obj_ner='PROCESSING UNIT'),
           SVO(subj='System', verb='produce', obj='distance', subj_ner='', obj_ner=''),
           SVO(subj='copy', verb='flatten', obj='vector', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='make', obj='lot', subj_ner='', obj_ner=''),
           SVO(subj='List', verb='CUDA', obj='Toolkit', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='use', obj='Docker', subj_ner='SYSTEM', obj_ner='SOFTWARE'),
           SVO(subj='System', verb='perform', obj='merging', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='depend on', obj='PyTorch', subj_ner='SYSTEM', obj_ner='LIBRARY'),
           SVO(subj='System', verb='depend on', obj='PyCuda', subj_ner='SYSTEM', obj_ner='LIBRARY'),
           SVO(subj='System', verb='utilize', obj='gpu', subj_ner='SYSTEM', obj_ner='PROCESSING UNIT'),
           SVO(subj='System', verb='create', obj='File', subj_ner='', obj_ner=''),
           SVO(subj='inference', verb='prepare', obj='buffers', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='have', obj='list', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='divide', obj='lot', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='make', obj='changes', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='depend on', obj='CUDA Toolkit', subj_ner='SYSTEM', obj_ner='LIBRARY'),
           SVO(subj='System', verb='depend on', obj='TensorRT', subj_ner='SYSTEM', obj_ner='LIBRARY'),
           SVO(subj='System', verb='utilize', obj='NVIDIA Jetson Agx Xavier', subj_ner='SYSTEM',
               obj_ner='COMPUTING PLATFORM'),
           SVO(subj='System', verb='perform', obj='padding', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='utilize', obj='NVIDIA Jetson AGX Xavier', subj_ner='SYSTEM',
               obj_ner='COMPUTING PLATFORM'),
           SVO(subj='System', verb='use', obj='ZED SDK', subj_ner='SYSTEM', obj_ner='SOFTWARE'),
           SVO(subj='System', verb='have', obj='boxes', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='use', obj='ROS2', subj_ner='SYSTEM', obj_ner='SOFTWARE'),
           SVO(subj='image', verb='have', obj='new size', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='use', obj='ZED SDK s', subj_ner='SYSTEM', obj_ner='SOFTWARE'),
           SVO(subj='System', verb='make', obj='tests', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='utilize', obj='autonomous system main unit', subj_ner='SYSTEM',
               obj_ner='COMPUTING PLATFORM'),
           SVO(subj='objects', verb='map', obj='pixels', subj_ner='', obj_ner=''),
           SVO(subj='System', verb='depend on', obj='CuDNN', subj_ner='SYSTEM', obj_ner='LIBRARY'),
           SVO(subj='System', verb='use', obj='NVIDIA tensorrt', subj_ner='SYSTEM', obj_ner='SOFTWARE'),
           SVO(subj='System', verb='use', obj='Non Maximum Suppression', subj_ner='SYSTEM', obj_ner='ALGORITHM')]


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

    for triple in triple_list:
        subject = triple.subj.replace(" ", "_")
        object = triple.obj.replace(" ", "_")
        if is_svo(triple):
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

            subject_ner = triple.subj_attrs
            if type(subject_ner) is list:
                for sub in subject_ner:
                    sub.replace(" ", "_")
            else:
                subject_ner = subject_ner.replace(" ", "_")

            object_ner = triple.obj_attrs
            if type(object_ner) is list:
                for ob in object_ner:
                    ob.replace(" ", "_")
            else:
                object_ner = object_ner.replace(" ", "_")

        if verb:
            rdf_triples.append(f":{subject} :{verb} :{object} .")

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

    print(rdf_triples)
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

    print(turtle_syntax)

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

    print(graph)


if __name__ == "__main__":
    x = convert_to_rdf(example)
    t = make_turtle_syntax(x)
    make_graph(t)
