from typing import List
import requests
import json
import os
from bs4 import BeautifulSoup
from entity.Article import Article, SOURCE_TYPE
from datetime import datetime
import pandas as pd

RESULTS_PATH = './articles.csv'

def fetch_fox5():
    """
    Fetches the list of traffic articles on the Fox 5 san diego page.

    Note: Fox 5 does server side rendering, so we make an api call for the html, then parse the html for data.
    """
    headers = {
        "Host": "fox5sandiego.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Cookie": "_pxhd=2b4e910bd95026954cec04726b569a87c1375a9309cc3edd2ed6c916e3458ab7:91d570d8-6b48-11f0-a9a7-6309a78f3214; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+04+2025+20%3A37%3A50+GMT-0700+(Pacific+Daylight+Time)&version=202507.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=8fc09176-e907-48e0-9b31-0126ce4ca207&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=C0001%3A1%2CSSPD_BG%3A1%2CC0002%3A1%2CC0004%3A1%2CC0007%3A1%2CC0003%3A1&intType=3&geolocation=US%3BCA&AwaitingReconsent=false; OTGPPConsent=DBABLA~BVQqAAAAAACA.QA; usprivacy=1YNN; pxcts=92ae0797-6b48-11f0-9be0-0b47c33df98d; _pxvid=91d570d8-6b48-11f0-a9a7-6309a78f3214; OptanonAlertBoxClosed=2025-07-28T00:19:52.575Z; OneTrustWPCCPAGoogleOptOut=false; nxstoryVariation=nxstory-auto-minimalist; _px2=eyJ1IjoiOGZhYmZlYTAtNzFhZC0xMWYwLWFiMjQtNmZmYjhhZjQ5MWNmIiwidiI6IjkxZDU3MGQ4LTZiNDgtMTFmMC1hOWE3LTYzMDlhNzhmMzIxNCIsInQiOjE3NTQzNjUzNzE4MzQsImgiOiJhNmQ5YjkyYjQ0ZTQxNmE0ZDNjYzVjODM1YmZjN2ViNzYzMTQ4MGY1Yjg5MGQxNmIyOGZlYzdlNzZiZGQ1ODFjIn0=; referralId=Direct",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    data = requests.get('https://fox5sandiego.com/traffic/', headers=headers)

    if (data.status_code != 200):
        raise Exception(f'API request to Fox5 returned {data.status_code}.')

    html = BeautifulSoup(data.content, 'html.parser')
    article_container = html.find('div', class_='article-list__content')
    if (not article_container):
        raise Exception('Couldn\'t find the div with class "article-list__content".')
    
    article_objects = []
    articles = article_container.find_all('article')
    for article in articles:
        a_tag = article.find('a', class_='article-list__article-link')
        if(not a_tag):
            raise Exception('No a tag found for this article')
        
        link = a_tag['href']
        
        title = a_tag.text.strip()
        
        web_id = article['data-article-id'].strip()
        
        date_posted = article.find('time')
        date_format = '%Y-%m-%dT%H:%M:%S%z'
        if date_posted is not None:
            date_posted = datetime.strptime(date_posted['datetime'], date_format)

        object = Article(
            web_id,
            title,
            link,
            date_posted,
            '',
            SOURCE_TYPE.FOX5
        )
        object.evaluate_relevance()
        if(object.is_relevant):
            article_objects.append(object)

    return article_objects

def fetch_nbc():
    url = 'https://www.nbcsandiego.com/wp-json/nbc/v1/template/term/1:13:461?page=1'
    headers = {
        "Host": "www.nbcsandiego.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.nbcsandiego.com/news/local/",
        "Connection": "keep-alive",
        "Cookie": "AMCV_A8AB776A5245B4220A490D44%40AdobeOrg=-2121179033%7CMCIDTS%7C20298%7CMCMID%7C28000392046703943609144673079011456402%7CMCOPTOUT-1753770351s%7CNONE%7CvVersion%7C5.3.0; AMCVS_A8AB776A5245B4220A490D44%40AdobeOrg=1; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Jul+28+2025+21%3A25%3A51+GMT-0700+(Pacific+Daylight+Time)&version=202309.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=cd8d7aac-e574-4d02-a9e9-3c8a9cd56be3&interactionCount=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=15%3A1%2C12%3A1%2C9%3A1%2C13%3A1%2CSPD_BG%3A1%2CUSP%3A1%2COOF%3A1&AwaitingReconsent=false; OTGPPConsent=DBABLA~BVQqAAAAAgA.QA; usprivacy=1YNN; OneTrustWPCCPAGoogleOptOut=false",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }

    data = requests.get(url, headers=headers)

    if(data.status_code != 200):
        raise Exception(f'API request to NBC7 returned {data.status_code}.')
    
    object = json.loads(data.content)
    date_format = '%Y-%m-%dT%H:%M:%S%z'
    articles = []
    for item in object['template_items']['items']:
        title = item['title'].strip()
        summary_soup = BeautifulSoup(item['summary'].strip(), 'html.parser')
        summary = summary_soup.text
        date_posted = datetime.strptime(item['date_time'], date_format)
        web_id = item['post_noid']
        link = item['link']

        article = Article(
            web_id,
            title,
            link,
            date_posted,
            summary,
            SOURCE_TYPE.NBC7
        )
        article.is_relevant = True
        articles.append(article)

    return articles


def save_results(articles: List[Article]):
    latest_data_df = pd.DataFrame.from_records([vars(a) for a in articles])
    
    if os.path.exists(RESULTS_PATH):
        existing_data_df = pd.read_csv(RESULTS_PATH)
        concatted_df = pd.concat([existing_data_df, latest_data_df])
        concatted_df.drop_duplicates(subset=['unique_id'], inplace=True)
    else:
        concatted_df = latest_data_df
    
    concatted_df.to_csv(RESULTS_PATH, index=False)
    print(f"Saved {concatted_df.shape[0]} articles.")


articles1 = fetch_nbc()
articles2 = fetch_fox5()
all_articles = [*articles1, *articles2]

save_results(all_articles)


