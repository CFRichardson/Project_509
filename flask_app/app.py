from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
import support
import os
import io
import json
import pandas as pd
import pickle
import sqlite3
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dopsifjdsSADFASDFR23847203987$@%#$!QEWDSoij'
socketio = SocketIO(app)
matplotlib.pyplot.switch_backend('Agg')


def predict_user_input(raw_text):

    tc = support.TokenCleaner(return_as_string=False)

    model_course, words_course = \
        support.load_model('model_nb.pkl', 'words_course.txt')

    model_star, words_star = \
        support.load_model('model_svm.pkl', 'words_star.txt')

    tokens = tc.CleanText(raw_text)

    # make a dictionary of words_course if any of the words_course are in the tokens list
    # then set the value to True else False
    X_course = {word: (word in tokens) for word in words_course}

    course = model_course.classify(X_course)

    X_star = {word: (word in tokens) for word in words_star}

    X_star_df = pd.DataFrame([X_star])

    star = model_star.predict(X_star_df)[0].round()
    return course, star, tokens


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")


@app.route('/explore')
def explore():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query(
        "SELECT id, course_name, star, text FROM reviews", conn).sample(1000)

    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)
    return render_template("explore.html", rows=data)


@socketio.on('request_word_usage_chart')
def request_word_usage_chart(word):
    save_path = support.create_usage_chart_for_word(word)
    print(save_path)
    emit('place_word_usage_chart', save_path)


@socketio.on('get_filtered_data')
def get_filtered_data(data):
    id = str(data['id'])
    course_name = str(data['course_name'])
    star = str(data['star'])
    text = str(data['text'])

    conn = sqlite3.connect('database.db')
    sql_statement = 'SELECT id, course_name, star, text FROM reviews'
    df = pd.read_sql_query(sql_statement, conn)

    # filter the data based on the user input
    if id != '':
        df = df[df['id'] == int(id)]

    if course_name != '':
        df = df[df['course_name'].str.contains(course_name)]

    if star != '':
        df = df[df['star'] == int(star)]

    if text != '':
        tokens = text.split(' ')
        # if tokens len is 1 then it is a single word
        for token in tokens:
            df = df[df['text'].str.contains(token, na=False)]

    # convert df.star to int
    # place '✭' for number of stars in df.star
    df['star'] = df['star'].astype(int)
    df.star = df.star.apply(lambda star: star * '✭')

    info = df.to_html(index=False)
    soup = BeautifulSoup(info, 'html.parser')
    output = str(soup.tbody)
    output = output.replace('\\n', '<br>')
    print('done')
    emit('place_filtered_data', output)


@socketio.on('get_prediction')
def get_prediction(data):
    course_pred, star_pred, tokens = \
        predict_user_input(data['raw_text'])

    output = {'course_pred': str(course_pred),
              'star_pred': str(star_pred),
              'raw_text': data['raw_text'],
              'tokens': str(tokens)}

    socketio.emit('receive_prediction', output)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80)


# pip install virtualenv
# virtualenv mvenv
# pip install -r requirements.txt

# pip freeze > requirements.txt
