import re
import nltk
import spacy
nltk.download("stopwords")
from nltk.corpus import stopwords
import numpy as np

def preprocess_text(text):

    # Load spaCy English model
    nlp = spacy.load("en_core_web_sm")

    # Remove all non-alphanumeric characters (keep letters/numbers)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = text.lower()

    # Convert to spaCy Doc
    doc = nlp(text)

    # Remove stop words and lemmatize
    stop_words = set(stopwords.words("english"))
    tokens = []
    for token in doc:
        if token.text not in stop_words and not token.is_punct:
            tokens.append(token.lemma_)

    return " ".join(tokens)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))