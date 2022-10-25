# flask related modules
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# DS related modules
import pandas as pd

import pyLDAvis
import pyLDAvis.sklearn

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from spacy.lang.en.stop_words import STOP_WORDS as stopwords

stopwords.update(['ll', 've'])

df = pd.read_csv('TOPIC_Data.csv')

count_text_vectorizer = CountVectorizer(stop_words=stopwords, min_df=0.1, max_df=0.7)
count_text_vectors = count_text_vectorizer.fit_transform(df["cleaned_text"])

lda_para_model = LatentDirichletAllocation(n_components=6 , random_state=1)
W_lda_para_matrix = lda_para_model.fit_transform(count_text_vectors)
H_lda_para_matrix = lda_para_model.components_


lda_display = pyLDAvis.sklearn.prepare(lda_para_model, count_text_vectors, count_text_vectorizer, sort_topics=False);
pyLDAvis.prepared_data_to_html(lda_display)
