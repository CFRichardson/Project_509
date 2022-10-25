import re
import os
import time
import random
import requests
from datetime import datetime
import pandas as pd
import sqlite3
import emoji
from nltk.stem import PorterStemmer
from string import punctuation
from nltk.corpus import stopwords
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


def load_model(model_name, words_path):
    # model = pickle.load(open(model_name, 'rb'))
    with open(model_name, 'rb') as f:
        model = pickle.load(f)

    with open(words_path, 'r') as f:
        words = f.read().splitlines()

    return model, words


class TokenCleaner():
    def __init__(self, remove_stopwords=True, return_as_string=False):

        # Some punctuation variations
        self.punctuation = set(punctuation)  # speeds up comparison
        self.punct_set = self.punctuation - {"#"}
        self.punct_pattern = \
            re.compile("[" + re.escape("".join(self.punct_set)) + "]")
        self.stemmer = PorterStemmer()
        # Stopwords
        if remove_stopwords:
            self.sw = stopwords.words("english") + ['️', '', ' ']
        else:
            self.sw = ''

        # Two useful regex
        self.whitespace_pattern = re.compile(r"\s+")
        self.hashtag_pattern = re.compile(r"^#[0-9a-zA-Z]+")
        self.CleanText_return_format = return_as_string

    def CleanText(self, _text):
        # if _text is has nothing in it then return none
        if _text is None:
            return ''

        # decode bytes to string if necessary
        if isinstance(_text, str):
            self.text = _text
        else:
            # this is for the case of tweets which are saved as bytes
            self.text = _text.decode("utf-8")

        self.__add_space_before_and_after_emoji()
        self.__RemovePunctuation()
        self.__TokenizeText()
        self.__StemEachToken()
        self.__RemoveStopWords()

        if self.CleanText_return_format:
            return ' '.join(self.tokens)
        else:
            return self.tokens

    def __StemEachToken(self):
        """
        Perform Stemming on each token (i.e. working, worked, works are all converted to work)<
        """

        self.tokens = [self.stemmer.stem(token) for token in self.tokens]

    def __add_space_before_and_after_emoji(self):
        text_section = list()
        for i, char in enumerate(self.text):
            if emoji.is_emoji(char):
                text_section.append(' ' + self.text[i] + ' ')
            else:
                text_section.append(self.text[i])

            if (ZERO_WIDTH_JOINER := '\u200d') in text_section:
                text_section.remove(ZERO_WIDTH_JOINER)

        return ''.join(text_section)

    def __RemovePunctuation(self):
        """
        Loop through the original text and check each character,
        if the character is a punctuation, then it is removed.
        ---------------------------------------------------------
        input: original text
        output: text without punctuation
        """
        self.text = \
            "".join([ch for ch in self.text if ch not in self.punct_set])

        self.text = re.sub(self.punct_pattern, '', self.text)

    def __TokenizeText(self):
        """
        Tokenize by splitting the text by white space
        ---------------------------------------------------------
        input: text without punctuation
        output: A list of tokens
        """
        self.tokens = \
            [item for item in self.whitespace_pattern.split(self.text)]

    def __RemoveStopWords(self):
        """
        Tokenize by splitting the text by white space
        ---------------------------------------------------------
        input: text without punctuation
        output: A list of tokens with all token as lower case
        """
        self.tokens = [token.lower() for token in self.tokens]

        self.tokens = \
            [token for token in self.tokens if not token in self.sw]


def add_space_after_emoji(text):

    text_section = list()
    for i, char in enumerate(text):
        if emoji.is_emoji(char):
            text_section.append(' ' + text[i] + ' ')
        else:
            text_section.append(text[i])

        if (ZERO_WIDTH_JOINER := '\u200d') in text_section:
            text_section.remove(ZERO_WIDTH_JOINER)

    return ''.join(text_section)


def clean_string(text):
    if pd.isnull(text):
        return text

    remove_words = stopwords.words("english") + ['️', '', ' ']
    text = text.replace('|', ' ').replace('\n', ' ')

    text = re.sub(punct_pattern, '', text)
    text = add_space_after_emoji(text)
    text_tokens = text.split(' ')
    text = [word.lower() for word in text_tokens]
    text = [word for word in text if not word in remove_words]
    return text


def create_usage_chart_for_word(word):
    try:
        word = str(word).strip()
        tc = TokenCleaner(return_as_string=True)
        word_stem = tc.CleanText(word)

        sql_statement = """
        SELECT reviews.star, reviews.text, review_tokens.tokens FROM reviews
        join review_tokens on reviews.id = review_tokens.id
        """

        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query(sql_statement, conn)
        df['star'] = df['star'].astype(int)

        # get the rows where the word is in the tokens

        if not word_stem == '':
            df_sub = df[df['tokens'].str.contains(word_stem)]

        elif df_sub.empty:
            df_sub = df[df['text'].str.contains(word)]
        else:
            pass

        word_df = pd.DataFrame(df_sub['star'].value_counts()).reset_index()

        # divide word_df index by number of rows in df with same star
        for i in range(1, 6):
            df_star_org = df_sub[df_sub['star'] == i]
            word_df.loc[word_df['index'] == i, 'proportion'] = len(
                word_df) / len(df_star_org)

        sns.set_style('darkgrid')

        # add padding inside grid to top
        matplotlib.rcParams['axes.ymargin'] = 0.1

        # chart word_df
        fig, ax = plt.subplots(figsize=(8, 6), nrows=1, ncols=1)
        ax = sns.barplot(x='index', y='star', data=word_df)

        # title of the plot
        ax.set_title(f'Word Usage: {word}', fontsize=20)

        # set x asix label
        ax.set_xlabel('Star Rating', fontsize=20)

        # set y axis label
        ax.set_ylabel('Proportion of Reviews', fontsize=16)

        # place occurance percentage compare to overall for each star
        for p in ax.patches:
            width, height = p.get_width(), p.get_height()
            place_value = height / word_df['star'].sum()

            x, y = p.get_xy()
            ax.annotate(f'{place_value:.1%}', (x + width/2, y + height*1.02),
                        ha='center', fontsize=16, weight='bold')

        # export the plot as png file
        save_path = f'./static/images/word_star_usage/{word}.png'
        plt.savefig(save_path)

    except:
        pass

    return save_path
