#!/usr/bin/env python
import requests
import cloudinary.uploader
import nltk
import re
import os

from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

try:
    from Tkinter import IntVar, Tk
except ImportError:
    from tkinter import IntVar, Tk

IMG_PATH = 'example8.jpg'
CLOUD_NAME = 'dezwtgmni'
UPLOAD_PRESET = 'wesjjhxl'
IMAGE_SEARCH_URL = 'https://www.google.com/searchbyimage?image_url='

# faking a browser client
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept-Language' : 'en-US,en;q=0.5'}

IRRELEVANT_TOKENS = ["www", "http", "https", "com", "net", "org",
                     "biz", "info", "pro", "name", "edu", "gov",
                     "co", "uk", "us", "de", "at", "html",
                     "twitter", "youtube", "status", "pinterest", "ebay", "shpock", "imgur"]


class SearchEngine(object):
    def __init__(self):

        self.img_path = IMG_PATH

        self._cloud_name = CLOUD_NAME

        self._upload_preset = UPLOAD_PRESET

        self._image_search_url = IMAGE_SEARCH_URL

        self._options = {'cloud_name': CLOUD_NAME}

    def run(self, **kwargs):

        if('path' in kwargs):
            self.img_path = kwargs['path']

        progress = None
        if('top' in kwargs and 'progress' in kwargs):
            top = kwargs['top']
            root = top
            progress = kwargs['progress']

        print(self.img_path)

        # Run the main job here
        image = self.open_img()
        img_b = self._img_to_bytecode(image)
        if(progress):
            progress.set(10)
        img_url = self._upload_img(img_b)
        if(progress):
            progress.set(40)
        html_received = self._search_img(img_url)
        if(progress):
            progress.set(60)
        img_urls = self._parse_img_urls(html_received)
        self._redirect(html_received)
        nouns_ranked = self._pos_process(img_urls)
        if(progress):
            progress.set(80)
        mrr = self._parse_most_likely_label(html_received)
        labels = self._get_human_labels(nouns_ranked, mrr)
        if(progress):
            progress.set(100)

        print("Most likely Human Labels for " + self.img_path + " are : "
                                                                 "\n1." + labels[0] +
              "\n2." + labels[1] +
              "\n3." + labels[2] +
              "\n4." + labels[3] +
              "\n5." + labels[4])

        result = Result()
        result.fileName = os.path.basename(self.img_path)
        result.labels = labels

        return result

    def _pos_process(self, text):
        # Cleaning the text from unnecessary characters and expressions (regex)
        text_re = self._re_filter(text)
        # Tokenizing the text
        tokens = self._tokenize(text_re)
        # Converting all characters to lower case
        tokens_lc = self._to_lower_case(tokens)
        # Removing stopwords from language
        tokens_wo_sw = self._remove_stopwords(tokens_lc)
        # Removing predefined expressions from tokens
        tokens_clean = self._remove_irrelevant_tokens(tokens_wo_sw)
        # Lemmatize
        tokens_lemmatized = self._lemmatize_tokens(tokens_clean)
        # POS tag
        tokens_pt = self._pos_tag_tokens(tokens_lemmatized)
        # Getting nouns
        nouns = self._get_nouns(tokens_pt)
        return nouns

    def open_img(self):
        try:
            with open(self.img_path, "rb") as image:
                img = image.read()
                return img
        except IOError:
            print("Oops! Opening the " + self.img_path + "wasn't successfull.")
        # *******************************polish this part!
        return None

    def _img_to_bytecode(self, image):
        return bytearray(image)

    def _upload_img(self, bytecode):
        result = cloudinary.uploader.unsigned_upload(bytecode, self._upload_preset, **self._options)
        # parsing resulting string to get image_url
        img_url = result['secure_url']
        print("Image url received : " + img_url)
        return img_url

    def _search_img(self, img_url):
        request_url = self._image_search_url + img_url
        print("Requesting : " + request_url)
        result = requests.get(request_url, headers=HEADERS)
        return result

    def _redirect(self, html):
        soup = BeautifulSoup(html.text, 'lxml')
        #match = soup.find('input', class_='e2BEnf U7izfe')['value']
        #match = ''
        #match = soup.find('input', class_='ui-card-header')['href']
        #print('similar images url : ' + match)

    def _parse_most_likely_label(self, html):
        # parsing html with beautifulsoup
        soup = BeautifulSoup(html.text, 'lxml')
        # access a variable of that class like a dictionary
        match = soup.find('input', class_='gLFyf gsfi')['value']
        print("Most likely result :  " + match)
        return match

    # Parse the image urls from similar images
    def _parse_img_urls(self, html):
        # parsing html with beautifulsoup
        soup = BeautifulSoup(html.text, 'lxml')
        match = ''
        for img_tag in soup.find_all('img', class_='rISBZc M4dUYb'):
            if img_tag.get('title'):
                img_url = img_tag.get('title')
                print("found! : " + img_url)
                match += (img_url + "\n")
        return match

    def _re_filter(self, text):
        result = re.sub("[\W\d_]", " ", text)
        #print(result)
        return result

    def _tokenize(self, text):
        tk = WordPunctTokenizer()
        result = tk.tokenize(text)
        #print(result)
        return result

    def _to_lower_case(self, tokens):
        # asagidakinin kisaca yapilmis hali boyle birsey ama nedense calismiyor.
        # return [].append([w.lower() for w in text])
        result = []
        for w in tokens:
            result.append(w.lower())
        return result

    def _remove_stopwords(self, tokens):
        stopword = stopwords.words('english')
        result = [word for word in tokens if word not in stopword]
        print("Removing Stopwords...")
        #print(result)
        return result

    def _remove_irrelevant_tokens(self, tokens):
        result = [word for word in tokens if word not in IRRELEVANT_TOKENS]
        print("Removing irrelevant tokens...")
        for word in result:
            # POLISH THE CODE *************************************************************************************************************
            if len(word) < 2:
                result.remove(word)
        return result

    def _lemmatize_tokens(self, tokens):
        wordnet_lemmatizer = WordNetLemmatizer()
        print("Lemmatizing tokens...")
        result = [wordnet_lemmatizer.lemmatize(word) for word in tokens]
        return result

    def _pos_tag_tokens(self, tokens):
        print("POS Tagging...")
        result = nltk.pos_tag(tokens)
        return result

    def _get_nouns(self, dictionary):
        print("Getting Nouns...")
        result = [word for (word, pos) in dictionary if pos[0] == 'N']
        return result

    def _get_human_labels(self, words, most_relevant_word):
        # POLISH THE CODE *****************************************************************************************************************
        result = [w[0] for w in Counter(words).most_common(5)]

        if most_relevant_word not in result:
            result.insert(0, most_relevant_word)
        else:
            result.remove(most_relevant_word)
            result.insert(0, most_relevant_word)
        return result

class Result:
    fileName = ""
    labels = []


def main():
    # Call your main functions here including run()
    se = SearchEngine()
    se.run()


if __name__ == '__main__':
    main()
