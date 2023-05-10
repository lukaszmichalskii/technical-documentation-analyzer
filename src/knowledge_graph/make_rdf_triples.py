from rdflib import Graph
from pyvis.network import Network

example = [('camera recognition', 'be', 'component'), ('camera recognition', 'be', 'computer vision module'), ('camera recognition', 'responsible', 'autonomous system'), ('camera recognition', 'be', 'component'), ('camera recognition', 'be', 'control pipeline'), ('camera recognition', 'be', 'autonomous system'), ('camera recognition', 'be', 'objects'), ('camera recognition', 'be', 'real time'), ('camera recognition', 'be', 'field'), ('camera recognition', 'be', 'cones'), ('camera', 'use', 'camera recognition'), ('camera', 'be', 'device'), ('camera', 'be', 'digital')]


def convert_to_rdf(triple_list):
    rdf_triples = []

    for triple in triple_list:
        subject = triple[0].replace(" ", "_")
        verb = triple[1].replace(" ", "_")
        object = triple[2].replace(" ", "_")

        rdf_triples.append(f":{subject} :{verb} :{object} .")

    return rdf_triples


def make_turtle_syntax(rdf_triples):
    prefix = "http://example.org/test#"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    turtle_syntax = f"PREFIX : <{prefix}>\nPREFIX rdf: <{rdf}>\n"
    for triple in rdf_triples:
        turtle_syntax += triple + "\n"

    return turtle_syntax


def make_graph(turtle):
    graph = Graph()
    graph.parse(data=turtle, format='turtle')

    network = Network()
    nodes = []
    edges = []

    for sub, edg, obj in graph:

        # temporary solution to pyvis not reading integers correctly
        if str(sub).isdigit():
            sub = str(sub) + '.'
        if str(obj).isdigit():
            obj = str(obj) + '.'

        nodes.append(sub)
        nodes.append(obj)
        edges.append([sub, obj])
        print(sub, edg, obj)

    network.add_nodes(nodes)
    network.add_edges(edges)
    # notebook = False - needed in new pyvis versions to work properly
    network.show('basic.html', notebook=False)


x = convert_to_rdf(example)

t = make_turtle_syntax(x)

print(t)

make_graph(t)

