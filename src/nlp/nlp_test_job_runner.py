from src.nlp.ner import get_obj_properties, add_layer, subj_equals_obj, create_word_vectors, check_for_string_labels
from src.nlp.svo import create_svo_triples

if __name__ == '__main__':
    text = '''Camera recognition is a component of control pipeline of SEE part of autonomous system. It is 
responsible for detecting objects in real time and creating field of cones for further use in path planner. 
Camera recognition is a ROS2 node running on autonomous system main unit'''

    # svo triples
    initial_tup_ls = create_svo_triples(text, debug=True)
    print(initial_tup_ls[0:3])
    print('-' * 50)

    # ner
    init_obj_tup_ls = get_obj_properties(initial_tup_ls)

    # graph assembly
    new_layer_ls = add_layer(init_obj_tup_ls)
    starter_edge_ls = init_obj_tup_ls + new_layer_ls
    edge_ls = subj_equals_obj(starter_edge_ls)

    # clean
    clean_edge_ls = check_for_string_labels(edge_ls)
    print(clean_edge_ls[0:3])
    print('-' * 50)

    clean_edge_ls = edge_ls # workaround for debugging
    print(edge_ls[0:3])
    print('-'*50)

    # word to vec
    edges_word_vec_ls = create_word_vectors(edge_ls)
    print(edges_word_vec_ls[0:3])
