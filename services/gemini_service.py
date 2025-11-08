import json
import time
import os
from entity.Article import Article
from utils.logging import log
from pydantic import BaseModel, Field
from datetime import datetime
from google import genai
from typing import List
from dotenv import load_dotenv

MAX_REQUESTS_PER_MINUTE = (
    20  # max is actually 30 for gemini-2.0-flash-lite, but play it safe
)
GEMINI_MODEL = "gemini-2.0-flash-lite"
BASE_PROMPT = "Please extract the information from the article."


class GeminiResponse(BaseModel):
    aboutTrafficCollision: bool = Field(
        description="Determine if the article is reporting on a single, specific, recent traffic collision that occurred at a named location."
    )
    collisionDesc: str = Field(
        description="A brief description of the collision (if aboutTrafficCollision is True)"
    )
    location: str = Field(description="The location where the collision occurred")
    date: str = Field(description="The date when the collision occured")


def get_gemini_client():
    load_dotenv()
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def prompt_gemini(
    client: genai.Client, prompt: str, model: str = "gemini-2.0-flash-lite"
) -> GeminiResponse:
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiResponse.model_json_schema(),
            },
        )
        return json.loads(response.text)
    except Exception as e:
        raise e


def create_prompt(article: Article) -> str:
    prompt = f"{BASE_PROMPT} Article headline: {article.title} | Article Text: {article.text} | Article publication date: {article.date_posted}."
    return prompt


# We process all articles at once to deal with the time limit
def process_articles(articles: List[Article]) -> None:
    requests_sent = 0
    client = get_gemini_client()
    start = datetime.now()
    for article in articles:
        # deal with rate limit
        time_since_start = datetime.now() - start
        if requests_sent == MAX_REQUESTS_PER_MINUTE and time_since_start.seconds <= 60:
            halt = 61 - time_since_start.seconds
            log(
                f"Time limit reached, sent {requests_sent} requests in {time_since_start.seconds} seconds, sleeping for {halt}"
            )
            time.sleep(halt)

        # prompt gemini
        log(f"Processing article {article.title}.")
        prompt = create_prompt(article)
        gemini_response = prompt_gemini(client, prompt, GEMINI_MODEL)
        log(f"\n{gemini_response}\n")
        requests_sent += 1

        # update article fields
        article.is_relevant = gemini_response["aboutTrafficCollision"]
        article.collision_description = gemini_response["collisionDesc"]
        article.collision_location = gemini_response["location"]
        article.collision_date = gemini_response["date"]
