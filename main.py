import os
from services.aws_service import read_file_s3
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)
CORS(app)

@app.route("/articles")
def articles():
    load_dotenv()
    # fetch df
    df = read_file_s3(os.getenv('S3_ARTICLES_FILENAME'))
    # filter out non relevant articles
    df = df[df['is_relevant'] == True]
    # sort by date
    df = df.sort_values(by='date_posted', ascending=False)
    return df.to_json(orient='records')
