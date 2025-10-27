from datetime import datetime
from entity.Article import SOURCE_TYPE, Article


def get_fox5_mock_article() -> Article:
    return Article(
        2484339,
        'Teen driver hits 13-year-old girl on e-bike',
        'https://fox5sandiego.com/traffic/teen-driver-hits-13-year-old-girl-on-e-bike-in-northern-san-diego/',
        '2025-08-11 21:48:42-07:00',
        None,
        SOURCE_TYPE.FOX5,
    )
    
def get_nbc7_mock_article() -> Article:
    return Article(
        238,
        'Something',
        'https://www.nbcsandiego.com/news/local/pedestrian-63-seriously-injured-in-el-cajon-hit-and-run/3921202/',
        datetime.now(),
        None,
        source=SOURCE_TYPE.NBC7,
    )
    