import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import nltk
import unicodedata
import numpy as np
import langdetect
from nltk.corpus import stopwords

### if you are missing langdetect, install with pip install langdetect

headers={'user-agent':'Snorks'}

languages = ['Java','C++','Rust','Python','php','Ruby']


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


# ## Clean text docs

def basic_clean(article):
    'Cleans all Tab and Newline chars, and removes non-english + speical chars'
    article = ' '.join(article.split()).lower()
    article = unicodedata.normalize('NFKD',article).encode('ASCII','ignore').decode('utf-8', 'ignore')
    article = re.sub(r"[^a-z0-9\s]", '', article)
    return article

def remove_links(article):
    ''
    return re.sub(r'(https?:\/\/)(\s)?(www\.)?(\s?)(\w+\.)*([\w\-\s]+\/)*([\w-]+)\/?',' ',article)

def stem_words(article):
    'Uses simple Stemmer to stem each word'
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in article.split()]
    return ' '.join(stems)

def drop_stop_words(article, stop_words=[]):
    ''
    stopword_list = nltk.corpus.stopwords.words('english') + ['r', 'u', '2', 'ltgt','yes','yeah','ye'] + [lang.lower() for lang in languages] + stop_words
    words = article.split()
    filtered_words = [w for w in words if w not in stopword_list]
    return ' '.join(filtered_words)

def clean(article,bonus_stopwords=[],skip_lang_check = True):
    '''If Language != English, returns NaN, else lowers and cleans all data,
     then drops stop words and stems words.
     can add extra stop words by passing in a list like:  bonus_stopwords = []'''
    if skip_lang_check:
        article = basic_clean(article)
        article = drop_stop_words(article,bonus_stopwords)
        article = stem_words(article)
        article = drop_stop_words(article,bonus_stopwords)
        return article

    if langdetect.detect(article) != 'en':

        return np.NaN

    else:
        article = basic_clean(article)
        article = drop_stop_words(article,bonus_stopwords)
        article = stem_words(article)
        return article

def deep_clean(article,bonus_stopwords=[]):
    article = remove_links(article)
    article = clean(article,bonus_stopwords)
    article = re.sub(r'\d','',article)
    return article


# ## Get 10 Links from Github Search

def get_links(pagenum=1,language='Python'):
    ''' This returns 10 Links as a list from Github's Search '''


    if language.lower() == 'c++':
        response = requests.get(f'https://github.com/search?l=&p={pagenum}&q=stars%3A%3E200+location%3AUSA+language%3AC%2B%2B&ref=advsearch&type=Repositories&utf8=%E2%9C%93')
    else:
        response = requests.get(f'https://github.com/search?l=&p={pagenum}&q=stars%3A%3E200+location%3AUSA+language%3A{language}&ref=advsearch&type=Repositories&utf8=%E2%9C%93')


    soup = BeautifulSoup(response.text)

    link_list=[]
    for i in range(7,len(soup.find_all(class_='v-align-middle'))):
        if soup.find_all(class_='v-align-middle')[i].text[0]:
            link_list.append(soup.find_all(class_='v-align-middle')[i].text)

    return link_list



def get_all_links():

    ''' Returns a large number of github repo links as a dictionary'''

    languages = ['Java','C++','Rust','Python','php','Ruby']

    repo_lists = {}
    for lang in languages:
        repo_list = []
        for page in range(1,12):
            repo_list += prepare.get_links(pagenum=page,language=lang)
            time.sleep(3)
        repo_lists[lang] = repo_list

    return repo_lists
