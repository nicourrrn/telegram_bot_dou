import feedparser
from time import mktime
from datetime import datetime
base_url = "https://jobs.dou.ua/vacancies/feeds/"


async def get_feeds(category: str, search: str) -> list[dict]:
    feed = feedparser.parse(f"{base_url}?category={category}&search={search}").entries
    for i, f in enumerate(feed):
        feed[i].published_parsed = datetime.fromtimestamp(mktime(f.published_parsed))
    return feed
