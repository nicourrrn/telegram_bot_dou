import feedparser
from time import mktime
from datetime import datetime, timedelta


class FeedUpdater:
    base_url = "https://jobs.dou.ua/vacancies/feeds/?"
    categories = {
        "Project Manager": ("Project+Manager", ""),
        "Software Architect": ("Architect", "", ""),
        "UI/UX Designer": ("Design", "UX+UI"),
        "QA Engineer": ("QA", ""),
        "HR": ("HR", ""),
        "DevOps": ("DevOps", ""),
        "Business Analyst": ("", "Business+Analyst", ""),
        "Developer": ("", "Developer")
    }

    def __init__(self):
        self.feeds_by_category = {}
        last_week = datetime.now() - timedelta(days=7)
        self.last_update = dict([(key, last_week) for key in self.categories.keys()])
        for key in self.categories.keys():
            self.update_category(key)

    async def pop_category(self, category: str) -> dict | None:
        if category not in self.feeds_by_category.keys():
            raise KeyError
        if len(self.feeds_by_category[category]) > 0:
            return self.feeds_by_category[category].pop()
        elif self.last_update[category] < datetime.now() - timedelta(hours=1):
            self.update_category(category)
            return await self.pop_category(category)
        else:
            return None

    def update_category(self, category: str) -> None:
        temp = self.get_feeds(*self.categories[category])
        self.feeds_by_category[category] = \
            self.get_from_time(self.last_update[category], temp)
        self.last_update[category] = datetime.now()

    def get_feeds(self, category: str, search: str, exp="0-1") -> list[dict]:
        print(f"{self.base_url}&category={category}&search={search}&exp={exp}")
        feed = feedparser.parse(f"{self.base_url}&category={category}&search={search}&exp={exp}").entries
        for i, f in enumerate(feed):
            feed[i].published_parsed = datetime.fromtimestamp(mktime(f.published_parsed))
        return feed

    @staticmethod
    def get_from_time(time_from: datetime, feeds: list[dict]) -> list[dict]:
        return list(filter(lambda f: f.published_parsed > time_from, feeds))
