import re
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text.lower())
    words = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    keywords = [w for w, _ in Counter(words).most_common(20)]
    return keywords
