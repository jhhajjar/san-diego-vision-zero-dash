from dotenv import load_dotenv
from services.aws_service import read_file_s3, upload_file_s3
from services.gemini_service import process_articles
from utils.logging import log
from typing import List
import requests
import json
import os
from bs4 import BeautifulSoup
from entity.Article import Article, SOURCE_TYPE
from datetime import datetime
import pandas as pd
from utils.constants import FOX5_HEADERS, NBC7_HEADERS
from argparse import ArgumentParser, Namespace


def fetch_fox5():
    """
    Fetches the list of traffic articles on the Fox 5 san diego page.

    Note: Fox 5 does server side rendering, so we make an api call for the html, then parse the html for data.
    """
    data = requests.get("https://fox5sandiego.com/traffic/", headers=FOX5_HEADERS)

    if data.status_code != 200:
        raise Exception(f"API request to Fox5 returned {data.status_code}.")

    html = BeautifulSoup(data.content, "html.parser")
    article_container = html.find("div", class_="article-list__content")
    if not article_container:
        raise Exception('Couldn\'t find the div with class "article-list__content".')

    article_objects = []
    articles = article_container.find_all("article")
    for article in articles:
        a_tag = article.find("a", class_="article-list__article-link")
        if not a_tag:
            raise Exception("No a tag found for this article")

        link = a_tag["href"]

        title = a_tag.text.strip()

        web_id = article["data-article-id"].strip()

        date_posted = article.find("time")
        date_format = "%Y-%m-%dT%H:%M:%S%z"
        if date_posted is not None:
            date_posted = datetime.strptime(date_posted["datetime"], date_format)

        article_object = Article(web_id, title, link, date_posted, "", SOURCE_TYPE.FOX5)
        article_objects.append(article_object)

    log(f"Fetched {len(article_objects)} articles from FOX5.")
    return article_objects


def fetch_nbc7():
    url = "https://www.nbcsandiego.com/wp-json/nbc/v1/template/term/1:13:461?page=1"
    data = requests.get(url, headers=NBC7_HEADERS)

    if data.status_code != 200:
        raise Exception(f"API request to NBC7 returned {data.status_code}.")

    object = json.loads(data.content)
    date_format = "%Y-%m-%dT%H:%M:%S%z"
    articles = []
    for item in object["template_items"]["items"]:
        title = item["title"].strip()
        summary_soup = BeautifulSoup(item["summary"].strip(), "html.parser")
        summary = summary_soup.text
        date_posted = datetime.strptime(item["date_time"], date_format)
        web_id = item["post_noid"]
        link = item["link"]

        article = Article(web_id, title, link, date_posted, summary, SOURCE_TYPE.NBC7)
        articles.append(article)

    log(f"Fetched {len(articles)} articles from NBC7.")
    return articles


def save_results(articles: List[Article]):
    latest_data_df = pd.DataFrame.from_records([vars(a) for a in articles])

    duplicates = 0
    existing_data_df = read_file_s3(os.getenv("S3_ARTICLES_FILENAME"))
    concatted_df = pd.concat([existing_data_df, latest_data_df])
    total_ = concatted_df.shape[0]
    concatted_df.drop_duplicates(subset=["unique_id"], inplace=True)
    duplicates = total_ - concatted_df.shape[0]

    log(f"Found {duplicates} duplicates.")
    log(f"Saving {concatted_df.shape[0]} articles to AWS.")

    article_filename = os.getenv("S3_ARTICLES_FILENAME")
    upload_file_s3(concatted_df, article_filename)


def main(args: Namespace):
    # Fetch articles
    articles = []
    if args.source == SOURCE_TYPE.FOX5:
        articles = fetch_fox5()
    elif args.source == SOURCE_TYPE.NBC7:
        articles = fetch_nbc7()
    else:
        fox_articles = fetch_fox5()
        nbc_articles = fetch_nbc7()
        articles = fox_articles + nbc_articles

    # Get article text
    for article in articles:
        log(f"Fetching {article.link}")
        article.set_article_text()

    # Evaluate their relevance
    process_articles(articles)

    # Save results
    if args.save_results:
        save_results(articles)
    else:
        print(articles)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source", action="store_const", default="all")
    parser.add_argument("--save-results", action="store_true", default=True)
    args = args = parser.parse_args()
    load_dotenv()
    main(args)
