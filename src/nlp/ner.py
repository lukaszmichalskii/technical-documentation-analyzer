from src.nlp.google_kgs import google_search


def get_obj_properties(tup_ls):
    init_obj_tup_ls = []

    for tup in tup_ls:
        try:
            text, node_label_ls, url = google_search(tup[2], limit=1)
            new_tup = (tup[0], tup[1], tup[2], text[0], node_label_ls[0], url[0])
        except:
            new_tup = (tup[0], tup[1], tup[2], [], [], [])

        init_obj_tup_ls.append(new_tup)

    return init_obj_tup_ls
