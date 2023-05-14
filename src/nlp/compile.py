import spacy
import crosslingual_coreference

text = """
    Do not forget about Momofuku Ando!
    He created instant noodles in Osaka.
    At that location, Nissin was founded.
    Many students survived by eating these noodles, but they don't even know him."""

# use any model that has internal spacy embeddings
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(
    "xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": -1}
)

doc = nlp(text)

print(doc._.resolved_text)