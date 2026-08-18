import asyncio
import aiohttp
import feedparser
import re
from urllib.parse import urlparse

RSS_FEEDS = {
    "general": [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.ndtv.com/rss/top-stories",
        "https://indianexpress.com/section/india/feed/",
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    ],
    "business": [
        "https://www.business-standard.com/rss/latest.rss",
        "https://www.thehindubusinessline.com/?service=rss",
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    ],
    "sports": [
        "https://sports.ndtv.com/rss/all",
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    ],
    "technology": [
        "https://www.gadgets360.com/rss/news",
        "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
    ],
    "entertainment": [
        "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
        "https://www.bollywoodhungama.com/rss/news.xml",
    ],
    "health": [
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",
        "https://www.ndtv.com/health/rss",
    ],
    "science": [
        "https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms",
    ],
}

def clean_html(raw):
    if not raw:
        return ""
    return re.sub('<[^<]+?>', '', raw).strip()

def get_image(entry):
    try:
        if hasattr(entry, 'media_content') and entry.media_content:
            url = entry.media_content[0].get('url')
            if url:
                return url
    except Exception:
        pass
    try:
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            url = entry.media_thumbnail[0].get('url')
            if url:
                return url
    except Exception:
        pass
    try:
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                href = enc.get('href') or enc.get('url')
                if href and 'image' in enc.get('type', ''):
                    return href
            href = entry.enclosures[0].get('href') or entry.enclosures[0].get('url')
            if href:
                return href
    except Exception:
        pass
    return None

async def fetch_feed(session, url, category):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"  Warning: {response.status} from {url}")
                return []
            text = await response.text()
            feed = feedparser.parse(text)
            if feed.bozo and not feed.entries:
                return []
            source_name = ""
            try:
                source_name = feed.feed.get('title', '')
            except Exception:
                pass
            if not source_name:
                source_name = urlparse(url).netloc

            articles = []
            for entry in feed.entries:
                title = entry.title if 'title' in entry else ""
                if not title:
                    continue
                description = clean_html(entry.summary) if 'summary' in entry else ""
                articles.append({
                    "title": title.strip(),
                    "description": description[:300],
                    "url": entry.link if 'link' in entry else "",
                    "urlToImage": get_image(entry),
                    "publishedAt": entry.get('published', entry.get('updated', '')),
                    "source": source_name,
                    "category": category,
                })
            print(f"  -> Found {len(articles)} articles from {url}")
            return articles
    except Exception as e:
        print(f"  Error connecting to {url}: {e}")
        return []

async def get_all_news():
    tasks_meta = [(url, cat) for cat, urls in RSS_FEEDS.items() for url in urls]
    print(f"🚀 Fetching {len(tasks_meta)} feeds across {len(RSS_FEEDS)} categories...")

    articles_list = []
    articles_by_category = {cat: [] for cat in RSS_FEEDS.keys()}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url, cat) for url, cat in tasks_meta]
        results = await asyncio.gather(*tasks)
        for (url, cat), result in zip(tasks_meta, results):
            articles_list.extend(result)
            articles_by_category[cat].extend(result)

    print(f"✅ Fetched {len(articles_list)} articles total.")
    return {"articles": articles_list, "by_category": articles_by_category}
