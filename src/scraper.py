import time
import requests
import feedparser
from bs4 import BeautifulSoup

def fetch_hacker_news(hours: int = 12) -> list[dict]:
    since_timestamp = int(time.time()) - (hours * 3600)
    url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{since_timestamp}&hitsPerPage=50"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []
        hits = r.json().get("hits", [])
        results = []
        for hit in hits:
            results.append({
                "title": hit.get("title"),
                "link": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "description": hit.get("story_text") or "",
                "source": "Hacker News",
                "created_at": hit.get("created_at_i")
            })
        return results
    except Exception:
        return []

def fetch_product_hunt(hours: int = 12) -> list[dict]:
    url = "https://www.producthunt.com/feed"
    try:
        feed = feedparser.parse(url)
        now = time.time()
        results = []
        for entry in feed.entries:
            published_time = time.mktime(entry.published_parsed)
            if now - published_time <= hours * 3600:
                results.append({
                    "title": entry.title,
                    "link": entry.link,
                    "description": getattr(entry, "summary", ""),
                    "source": "Product Hunt",
                    "created_at": int(published_time)
                })
        return results
    except Exception:
        return []

def fetch_reddit(hours: int = 12) -> list[dict]:
    subreddits = ["sideproject", "saas"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    now = time.time()
    results = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=30"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                continue
            children = r.json().get("data", {}).get("children", [])
            for child in children:
                data = child.get("data", {})
                created_utc = data.get("created_utc", 0)
                if now - created_utc <= hours * 3600:
                    results.append({
                        "title": data.get("title"),
                        "link": f"https://www.reddit.com{data.get('permalink')}",
                        "description": data.get("selftext", ""),
                        "source": "Reddit",
                        "created_at": int(created_utc)
                    })
        except Exception:
            pass
    return results

def fetch_github_trending(hours: int = 12) -> list[dict]:
    url = "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for article in soup.select("article.Box-row"):
            title_a = article.select_one("h2.h3.lh-condensed a") or article.select_one("h2 a") or article.select_one("h1 a")
            if not title_a:
                continue
            href = title_a.get("href", "")
            repo_name = " ".join(title_a.text.split())
            link = f"https://github.com{href}"
            
            desc_p = article.select_one("p.col-9") or article.select_one("p.color-fg-muted") or article.select_one("p")
            desc = desc_p.text.strip() if desc_p else ""
            
            results.append({
                "title": repo_name,
                "link": link,
                "description": desc,
                "source": "GitHub Trending",
                "created_at": int(time.time())
            })
        return results
    except Exception:
        return []
