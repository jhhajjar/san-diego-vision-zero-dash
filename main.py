import pandas as pd
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/articles")
def articles():
    df = pd.read_csv('data/articles.csv')
    df = df.sort_values(by='date_posted')
    return df.to_json(orient='records')
