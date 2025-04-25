from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
import string
import nltk

def preprocess_text(text):
    text = text.lower()
    tokens = wordpunct_tokenize(text)  # Alternativa segura ao word_tokenize
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = [t for t in tokens if t not in stopwords.words('portuguese')]
    return tokens
