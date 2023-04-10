import spacy

non_nc = spacy.load('en_core_web_lg')
nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('merge_noun_chunks')

# print(spacy.__version__)
# print(non_nc.pipe_names)
# print(nlp.pipe_names)
