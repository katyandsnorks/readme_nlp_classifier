import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings("ignore")

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