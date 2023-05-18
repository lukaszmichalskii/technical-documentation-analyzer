from rdflib import Graph

example = [('camera recognition', 'be', 'component', 'In biology and ecology, abiotic components or abiotic factors are non-living chemical and physical parts of the environment that affect living organisms and the functioning of ecosystems. ', ['Thing', 'Person'], 'https://en.wikipedia.org/wiki/Abiotic_component'),
           ('camera', 'use', 'component', 'In biology and ecology, abiotic components or abiotic factors are non-living chemical and physical parts of the environment that affect living organisms and the functioning of ecosystems. ', ['Thing'], 'https://en.wikipedia.org/wiki/Abiotic_component'),
           ('camera', 'be', 'device', 'In biology and ecology, abiotic components or abiotic factors are non-living chemical and physical parts of the environment that affect living organisms and the functioning of ecosystems. ', ['Device'], 'https://en.wikipedia.org/wiki/Abiotic_component'),
           ('component', 'be', 'something', 'In biology and ecology, abiotic components or abiotic factors are non-living chemical and physical parts of the environment that affect living organisms and the functioning of ecosystems. ', ['Thing', 'Device'], 'https://en.wikipedia.org/wiki/Abiotic_component')]


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
        subject = triple[0].replace(" ", "_")
        verb = triple[1].replace(" ", "_")
        object = triple[2].replace(" ", "_")

        description = triple[3]
        classes = triple[4]
        url = triple[5]

        rdf_triples.append(f":{subject} :{verb} :{object} .")

        if classes != "[]":
            for item in classes:
                rdf_triples.append(f":{object} rdf:type :{item} .")

        if description != "[]":
            rdf_triples.append(f":{object} rdfs:description \"{description}\" .")

        if url != "[]":
            rdf_triples.append(f":{object} rdfs:seeAlso \"{url}\" .")

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


x = convert_to_rdf(example)
t = make_turtle_syntax(x)
make_graph(t)

