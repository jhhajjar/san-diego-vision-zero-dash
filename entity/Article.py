from typing import List
import uuid
from datetime import datetime
from enum import Enum

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





