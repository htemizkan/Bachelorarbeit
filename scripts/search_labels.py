#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import requests
import cloudinary.uploader
import nltk
import re
import os

from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from collections import Counter


try:
    from Tkinter import IntVar, Tk
except ImportError:
    from tkinter import IntVar, Tk

DEBUG = False
OBJECT_SIMILARITY = 0.3
IMG_PATH = 'instant_noodles_0.jpeg'
CLOUD_NAME = 'dezwtgmni'
UPLOAD_PRESET = 'wesjjhxl'
IMAGE_SEARCH_URL = 'https://www.google.com/searchbyimage?image_url='

# Choose 1 for parsing text information from image addresses and
# Choose 2 for parsing information from image urls
# First option is more accurate but also slower.
DEFAULT_SEARCH_TYPE = 2

# faking a browser client
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept-Language' : 'en-US,en;q=0.5'}

IRRELEVANT_TOKENS = ["www", "http", "https", "com", "net", "org",
                     "biz", "info", "pro", "name", "edu", "gov",
                     "co", "uk", "us", "de", "at", "html",
                     "twitter", "youtube", "status", "pinterest", "ebay", "shpock",
                     "imgur", "the", "en", "png", "x", "o",
                     "photo", "photos", "image", "images", "wood", "jpg",
                     "color", "product", "products", "tripadvisor", "wood", "color",
                     "paint", "hashtag", "tag", "label", "vintage", "shutterstock",
                     "shop", "category", "aliexpress", "search", "htm", "spar",
                     "detail", "details", "amazon", "stock", "blog", "facebook",
                     "flickr", "china", "mm", "cm", "item", "io", "collection",
                     "bio", "fr", "plastic", "reddit", "pk", "ml",
                     "foundation","instagram","post",
                     "issue", "|", "/", "-", "\\", "~",
                     "\\\"", "page", "shopping", "picture", "yahoo", "value",
                     "param"
                     ]


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

        # Run the main job here
        image = self.open_img()
        img_b = self._img_to_bytecode(image)
        if(progress):
            progress.set(10)
            #root.searchProgressbar.update_idletasks()
        img_url = self._upload_img(img_b)
        if(progress):
            progress.set(40)
            #root.searchProgressbar.update_idletasks()
        html_received = self._search_img(img_url)
        if(progress):
            progress.set(60)
            #root.searchProgressbar.update_idletasks()
        if DEFAULT_SEARCH_TYPE == 1:
            img_text = self._parse_img_text(html_received)
            nouns = self._pos_process_text(img_text)
        elif DEFAULT_SEARCH_TYPE == 2:
            img_urls = self._parse_img_urls(html_received)
            nouns = self._pos_process_urls(img_urls)
        else:
            print("Given search type is not valid!")
            return

        if(progress):
            progress.set(80)
            #root.searchProgressbar.update_idletasks()
        mrr = self._parse_most_likely_label(html_received)
        labels = self._get_human_labels(nouns, mrr)
        if(progress):
            progress.set(100)
            #root.searchProgressbar.update_idletasks()
        if len(labels) >= 5:
            print("Most likely Human Labels for " + self.img_path + " are : " +
                  "\n1." + labels[0] +
                  "\n2." + labels[1] +
                  "\n3." + labels[2] +
                  "\n4." + labels[3] +
                  "\n5." + labels[4])

        result = Result()
        result.fileName = os.path.basename(self.img_path)
        result.labels = labels

        return result

    def _pos_process_text(self, text):
        # Removing non-ascii characters
        text_utf8 = self._remove_non_ascii(text)
        # Tokenizing the text
        tokens = self._tokenize(text_utf8)
        # Converting all characters to lower case
        tokens_lc = self._to_lower_case(tokens)
        # Removing stopwords from language
        tokens_wo_sw = self._remove_stopwords(tokens_lc)
        # POS tag
        tokens_pt = self._pos_tag_tokens(tokens_wo_sw)
        # Getting nouns
        nouns = self._get_nouns(tokens_pt)
        # Lemmatize
        result = self._lemmatize_tokens(nouns)
        # Remove tokens shorter than 3 characters
        result = self._remove_shorter_tokens(result, 2)
        # Removing predefined set of expressions from tokens
        result = self._remove_irrelevant_tokens(result)
        # Remove non-english words
        result = self._remove_if_not_en(result)
        # Getting words more likely to be object
        result = [w for w in result \
             if self._is_object(w)]
        return result

    def _pos_process_urls(self, text):
        # Cleaning the text from unnecessary characters and expressions (regex)
        text_re = self._re_filter_url(text)
        # Tokenizing the text
        tokens = self._tokenize(text_re)
        # Converting all characters to lower case
        tokens_lc = self._to_lower_case(tokens)
        # Removing stopwords from language
        tokens_wo_sw = self._remove_stopwords(tokens_lc)
        # Removing predefined set of expressions from tokens
        tokens_clean = self._remove_irrelevant_tokens(tokens_wo_sw)
        # POS tag
        tokens_pt = self._pos_tag_tokens(tokens_clean)
        # Getting nouns
        nouns = self._get_nouns(tokens_pt)
        # Lemmatize
        nouns = self._lemmatize_tokens(nouns)
        # Remove tokens shorter than 3 characters
        nouns = self._remove_shorter_tokens(nouns, 2)
        # Remove non-english words
        result = self._remove_if_not_en(nouns)
        # Getting words more likely to be object
        result = [w for w in result \
                    if self._is_object(w)]
        return result

    def open_img(self):
        try:
            with open(self.img_path, "rb") as image:
                img = image.read()
                return img
        except IOError:
            print("Oops! Opening the " + self.img_path + " wasn't successfull.")
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

    def _parse_img_text(self, html):
        result = ''
        soup = BeautifulSoup(html.text, 'lxml')
        match = soup.find('a', class_='iu-card-header').get('href')
        request_url = "https://www.google.com" + match
        print('Requesting :' + request_url)
        si_html = requests.get(request_url, headers=HEADERS)
        soup = BeautifulSoup(si_html.text, 'lxml')

        for img_tag in soup.find_all('div', class_='mVDMnf nJGrxf'):
            if img_tag.text:
                if DEBUG:
                    print("found image text! : " + img_tag.text)
                result += (img_tag.text + "\n")
        return result

    def _parse_most_likely_label(self, html):
        # parsing html with beautifulsoup
        soup = BeautifulSoup(html.text, 'lxml')
        # access a variable of that class like a dictionary
        match = soup.find('input', class_='gLFyf gsfi')['value']
        if DEBUG:
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
                if DEBUG:
                    print("found! : " + img_url)
                match += (img_url + "\n")
        return match

    def _re_filter_url(self, text):
        result = re.sub("[\W\d_]", " ", text)
        if DEBUG:
            print('Result after cleaning url: '),
            print(result)
        return result

    def _remove_non_ascii(self, text):
        result = re.sub("[^\x00-\x7F]+", "", text)
        if DEBUG:
            print('Result after removing non-ASCII expressions: '),
            print(result)
        return result

    def _remove_non_unicode(self, text):
        result = re.sub("[^\x00-\x7F]+", "", text)
        if DEBUG:
            print('Result after removing non-unicode expressions: '),
            print(result)
        return result

    def _tokenize(self, text):
        tk = WordPunctTokenizer()
        result = tk.tokenize(text)
        if DEBUG:
            print("Result after tokenizing: "),
            print(result)
        return result

    def _to_lower_case(self, tokens):
        result = []
        for w in tokens:
            result.append(w.lower())
        return result

    def _remove_stopwords(self, tokens):
        stopword = stopwords.words('english')
        result = [word for word in tokens if word not in stopword]
        print("Removing Stopwords...")
        if DEBUG:
            print('Result after removing stopwords: '),
            print(result)
        return result

    def _remove_irrelevant_tokens(self, tokens):
        print("Removing irrelevant tokens...")
        result = [word for word in tokens if word not in IRRELEVANT_TOKENS]
        return result

    def _remove_shorter_tokens(self, tokens, max_length):
        result = []
        for word in tokens:
            if len(word) > max_length or word == '.' or word == '...':
                result.append(word)
        return result

    def _remove_if_not_en(self, tokens):
        words = set(nltk.corpus.words.words())
        result = [w for w in tokens \
                 if w.lower() in words or not w.isalpha()]
        if DEBUG:
            print('Result after non-english words removed: '),
            print(result)
        return result

    def _is_object(self, word):
        wn_lemmas = set(wordnet.all_lemma_names())
        lemmatizer = WordNetLemmatizer()
        word = lemmatizer.lemmatize(word)
        str_var = "".join(word + ".n.01")
        if word in wn_lemmas and str_var in [syn.name() for syn in wordnet.synsets(word)]:
            w = wordnet.synset(str_var)
            object = wordnet.synset("object.n.01")
            if object.wup_similarity(w) >= OBJECT_SIMILARITY:
                return True
            else:
                return False
        return False


    def _lemmatize_tokens(self, tokens):
        wordnet_lemmatizer = WordNetLemmatizer()
        print("Lemmatizing tokens...")
        result_unicode = [wordnet_lemmatizer.lemmatize(word, pos="n") for word in tokens]
        result = [x.encode('utf-8') for x in result_unicode]
        if DEBUG:
            print("Result after Lemmatizing: "),
            print(result)
        return result

    def _pos_tag_tokens(self, tokens):
        print("POS Tagging...")
        result = nltk.pos_tag(tokens)
        if DEBUG:
            print("POS tagging result: "),
            print(result)
        return result

    def _get_nouns(self, dictionary):
        print("Getting Nouns...")
        result = [word for (word, pos) in dictionary if pos[0] == 'N']
        return result

    def _get_human_labels(self, words, most_relevant_word):
        result = [w[0] for w in Counter(words).most_common(5)]
        if most_relevant_word not in result:
            if(result):
                result.pop()
                result.insert(0, most_relevant_word)
        else:
            result.remove(most_relevant_word)
            result.insert(0, most_relevant_word)
        return result

class Result:
    fileName = ""
    labels = []


def main():
    se = SearchEngine()
    se.run()


if __name__ == '__main__':
    main()
