import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import nltk
import unicodedata
import re
from nltk.corpus import stopwords

stopword_list = nltk.corpus.stopwords.words('english') + ['r', 'u', '2', 'ltgt']
stopword_list.remove('no')
stopword_list.remove('not')

import warnings
warnings.filterwarnings("ignore")


### Pull from Github
def get_langs(soup):
    '''Function to get a list of languages for a Github repo from a url'''
    lang_list = soup.find_all(class_='language-color')
    langs = []
    for lang in lang_list:
        if lang.text is not '':
            langs.append(lang['aria-label'])

    return langs

def get_lang_dict(langs):
    '''This takes a list of Languages + Percentages and returns those in a dictionary'''
    return {re.findall('[^\d]+',lang)[0][:-1]:float(re.findall('\d+\.?\d?',lang)[0]) for lang in langs}

def read_lang(url):
    '''function to get percentage of languages and read me text of a Github repo from a url'''
    response = requests.get(f'{url}')
    soup = BeautifulSoup(response.text)

    read_me = soup.find_all(class_='Box-body')

    langs = get_lang_dict(get_langs(soup))

    if len(read_me) == 0:
        return {'Languages':langs, 'readme':''}

    return {'languages':langs, 'readme':' '.join(read_me[0].text.split())}


### Clean text docs 

def basic_clean(article):
    article = ' '.join(article.split()).lower()
    article = unicodedata.normalize('NFKD',article).encode('ASCII','ignore').decode('utf-8', 'ignore')
    article = re.sub(r"[^a-z0-9'\s]", '', article)
    return article

def stem_words(article):
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in article.split()]
    return ' '.join(stems)

def drop_stop_words(article):
    words = article.split()
    filtered_words = [w for w in words if w not in stopword_list]
    return ' '.join(filtered_words)

def clean(article):
    article = basic_clean(article)
    article = stem_words(article)
    article = drop_stop_words(article)
    return article
