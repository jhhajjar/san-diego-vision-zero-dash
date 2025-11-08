import uuid
from utils.constants import FOX5_HEADERS, NBC7_HEADERS
from datetime import datetime
from enum import Enum
from bs4 import BeautifulSoup
import requests


class SOURCE_TYPE(Enum):
    FOX5 = "FOX5"
    NBC7 = "NBC7"


class Article:
    def __init__(
        self,
        web_id: str,
        title: str,
        link: str,
        date_posted: datetime,
        summary: str,
        source: SOURCE_TYPE,
    ):
        self.id = uuid.uuid4()
        self.web_id = web_id
        self.title = title
        self.link = link
        self.date_posted = date_posted
        self.summary = summary
        self.source = source

        self.text = None
        self.is_relevant = None
        self.collision_description = None
        self.collision_location = None
        self.collision_date = None

        self.unique_id = f"{source}{web_id}"

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def get_headers(self):
        if self.source == SOURCE_TYPE.FOX5:
            return FOX5_HEADERS
        if self.source == SOURCE_TYPE.NBC7:
            return NBC7_HEADERS

    def set_article_text(self) -> None:
        if self.text:
            return

        if not self.link:
            raise Exception("Article does not have a link, cannot set article text")

        response = requests.get(self.link, headers=self.get_headers())
        parsed = BeautifulSoup(response.text, "html.parser")
        self.text = parse_article(parsed, self.source)


def parse_article(soup: BeautifulSoup, source: SOURCE_TYPE):
    if source == SOURCE_TYPE.FOX5:
        return _parse_fox5_article(soup)
    if source == SOURCE_TYPE.NBC7:
        return _parse_nbc7_article(soup)


def _parse_fox5_article(soup: BeautifulSoup):
    html_text = soup.find("article").findAll("p")
    full_text = [tag.get_text().strip() for tag in html_text]
    return " ".join(full_text)


def _parse_nbc7_article(soup: BeautifulSoup):
    html_text = soup.find("article").findAll("p")
    full_text = [tag.get_text().strip() for tag in html_text]
    return " ".join(full_text)
