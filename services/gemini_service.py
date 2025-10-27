import time
from google import genai
from datetime import datetime
from typing import List
from entity.Article import Article
from utils.logging import log
from dotenv import load_dotenv
import os

MAX_REQUESTS_PER_MINUTE = 30
GEMINI_MODEL = 'gemini-2.0-flash-lite'
DELIM='^'
BASE_PROMPT = 'Answer the following questions about the article in the format question{DELIM}answer (my script will look for the answer after the {DELIM}). Does it talk about a traffic collision (1 or 0), location of collision, date of collision (MM/DD/YYYY Pacific Timezone).'

def get_gemini_client():
    load_dotenv()
    return genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def prompt_gemini(client: genai.Client, prompt: str, model: str = 'gemini-2.0-flash-lite') -> str:
    try:
        response = client.models.generate_content(
            model=model, contents=prompt,
        )
        return response.text
    except Exception as e:
        raise e

# We process all articles at once to deal with the time limit
def process_articles(articles: List[Article]) -> None:
    requests_sent = 0
    client = get_gemini_client()
    start = datetime.now()
    for article in articles:
        # deal with rate limit
        time_since_start = datetime.now() - start
        if requests_sent == MAX_REQUESTS_PER_MINUTE and time_since_start.seconds <= 60:
            halt = 61 - time_since_start
            log(f'Time limit reached, sent {requests_sent} requests in {time_since_start.seconds} seconds, sleeping for {halt}')
            time.sleep(halt)
            
        # prompt gemini
        log(f'Processing article {article.title}.')
        prompt = f'{BASE_PROMPT} Article Text: {article.text}, Article publication date: {article.date_posted}.'
        gemini_response = prompt_gemini(client, prompt, GEMINI_MODEL)
        print(f'\n{gemini_response}\n')
        requests_sent += 1
        
        # extract info from prompt
        count = 0
        relevant = None
        location = None
        date = None
        splits = gemini_response.split('\n')
        for split in splits:
            components = split.split('{DELIM}')
            if len(components) > 1:
                if count == 0:
                    relevant = int(split.split('{DELIM}')[1].strip())
                    count += 1
                elif count == 1 and relevant:
                    location = split.split('{DELIM}')[1].strip()
                    count += 1
                elif count == 2 and relevant:
                    date = split.split('{DELIM}')[1].strip()
                    count += 1
                
        # update article fields
        article.is_relevant = relevant
        article.collision_location = location
        article.collision_date = date