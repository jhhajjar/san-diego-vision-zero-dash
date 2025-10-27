from typing import List
import uuid
from datetime import datetime
from enum import Enum

from bs4 import BeautifulSoup
import requests

from utils.constants import FOX5_HEADERS, NBC7_HEADERS

class SOURCE_TYPE(Enum):
    FOX5 = 'FOX5'
    NBC7 = 'NBC7'

KEYWORDS = {
    SOURCE_TYPE.FOX5: [
        'kill',
        'injur',
        'cyclist',
        'pedestrian',
        'bike',
        'fatal',
        'crash',
        'collision',
        'strike',
        'driver',
        'bicycle',
        'dead',
        'vehicle'
    ],
    SOURCE_TYPE.NBC7: [

    ]
}

class Article:
    def __init__(self, web_id: str, title: str, link: str, date_posted: datetime, summary: str, source: SOURCE_TYPE):
        self.id = uuid.uuid4()
        self.web_id = web_id
        self.title = title
        self.link = link
        self.date_posted = date_posted
        self.summary = summary
        self.source = source
        
        self.text = None
        self.is_relevant = None
        self.collision_location = None
        self.collision_date = None

        self.unique_id = f'{source}{web_id}'

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __str__(self):
        return f"{{\n\tid: {self.id}\n\tweb_id: {self.web_id}\n\ttitle: {self.title}\n\tlink: {self.link}\n\tdate_posted: {self.date_posted}\n\tsummary: {self.summary}\n\tcreated_at: {self.created_at}\n\tupdated_at: {self.updated_at}\n}}"
    
    def relevant(self) -> bool:
        """
        Determines if an article title is relevant
        """
        title = self.title.lower()
        summary = self.summary.lower() if self.summary else ''
        article_data = f'{title} {summary}'

        keywords = self.get_keywords()

        for kw in keywords:
            if(kw.lower() not in article_data):
                continue
            return True
        return False
    
    def csv_header() -> str:
        return "id,web_id,title,link,date_posted,summary,source,unique_id,created_at"
    
    def to_csv_line(self) -> str:
        """
        converts to csv line
        """
        return f"{self.id},{self.web_id},{self.title},{self.link},{self.date_posted},{self.summary},{self.source},{self.unique_id},{self.created_at}"
    
    def get_keywords(self) -> List[str]:
        if self.source not in KEYWORDS.keys():
            raise Exception('Invalid source type: {}'.format(self.source))
        return KEYWORDS[self.source]
    
    def evaluate_relevance(self) -> None:
        """
        Determines and stores whether an article is relevant
        """
        self.is_relevant = self.relevant()
        
    def get_headers(self):
        if self.source == SOURCE_TYPE.FOX5:
            return FOX5_HEADERS
        if self.source == SOURCE_TYPE.NBC7:
            return NBC7_HEADERS
        
    def set_article_text(self) -> None:
        if self.text:
            return
        
        if not self.link:
            raise Exception('Article does not have a link, cannot set article text')
        
        response = requests.get(self.link, headers=self.get_headers())
        parsed = BeautifulSoup(response.text, 'html.parser')
        self.text = parse_article(parsed, self.source)
        
    def gemini_process(self) -> None:
        prompt = f'Extract the following from the article in a list in the following format: does it talk about a traffic collision (1 or 0), location of collision, date of collision (MM/DD/YYYY Pacific Timezone): {article.text}, Date posted: {article.date_posted}.'
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", contents=prompt,
        )
        print(response.text)
        content = response.text
        splits = content.split('\n')
        count = 0
        for split in splits:
            if len(split) and split[0] == '*':
                if count == 0:
                    relevant = split.split(':')[1].strip()
                    count += 1
                elif count == 1:
                    location = split.split(':')[1].strip()
                    count += 1
                elif count == 2:
                    date = split.split(':')[1].strip()
                    count += 1
        
def parse_article(soup: BeautifulSoup, source: SOURCE_TYPE):
    if source == SOURCE_TYPE.FOX5:
        return _parse_fox5_article(soup)
    if source == SOURCE_TYPE.NBC7:
        return _parse_nbc7_article(soup)
    
def _parse_fox5_article(soup: BeautifulSoup):
    html_text = soup.find('article').findAll('p')
    full_text = [tag.get_text().strip() for tag in html_text]
    return ' '.join(full_text)

def _parse_nbc7_article(soup: BeautifulSoup):
    html_text = soup.find('article').findAll('p')
    full_text = [tag.get_text().strip() for tag in html_text]
    return ' '.join(full_text)



