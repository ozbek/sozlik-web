import re
import sqlite3

from flask import Flask, render_template, g, jsonify

from spell import candidates

app = Flask(__name__)

DATABASE = '/Users/atabek/Projects/Flask/sozlik.com/sozlik/sozlik.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template('index.html')


# /api/suggestion/<beginswith>
@app.route("/api/suggestion/<beginswith>")
def api_get_suggestion(beginswith):
    beginswith = normalize_query(beginswith)
    cur = get_db().cursor()
    cur.execute("select word from qqen where word like ? limit 10", (beginswith + '%',))
    result = cur.fetchall()
    if result:
        data = []
        for r in result:
            data.append(r["word"])
        return jsonify(suggestions=data)


# /translate/<search_word>
@app.route("/translate/<search_word>")
def get_translate(search_word):
    search_word = normalize_query(search_word)
    cur = get_db().cursor()
    cur.execute("select * from qqen where word = ?", (search_word,))
    result = cur.fetchone()
    if result:
        return render_template("translate.html", word=result["word"], translation=result["translation"])
    else:
        did_you_mean = candidates(search_word, get_all_words())
        return render_template("notfound.html", word=search_word, did_you_mean=did_you_mean)


def normalize_query(search_word):
    return re.sub('[^a-z\-]', '', search_word.lower())


def get_all_words():
    data = []
    cur = get_db().cursor()
    cur.execute("select word from qqen")
    result = cur.fetchall()
    if result:
        for r in result:
            data.append(r["word"])
    return data
