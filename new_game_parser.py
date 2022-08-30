import nltk
from nltk import PorterStemmer

nltk.download('words')

words = set(nltk.corpus.words.words())
stemmer = PorterStemmer()


def watch_words(dict, text):
    if text not in dict:
        dict[text] = 0
    dict[text] = dict[text] + 1



def cleanse_string(text):
    return " ".join(w for w in nltk.wordpunct_tokenize(text) \
                    if stemmer.stem(w).lower() in words or not w.isalpha())


print(cleanse_string("adsf asdokasdk hellos hi cows cow dog doggy franks eliminated killed kills killing triple"))
