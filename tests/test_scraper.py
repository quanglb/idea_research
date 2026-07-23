import pytest
from unittest.mock import patch, MagicMock
from src.scraper import (
    fetch_hacker_news,
    fetch_product_hunt,
    fetch_reddit,
    fetch_github_trending
)

@patch('src.scraper.requests.get')
def test_fetch_hacker_news_success(mock_get):
    # Mock Hacker News API Algolia response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hits": [
            {
                "title": "HN Idea",
                "url": "https://hn.example.com",
                "created_at_i": 1700000000,
                "story_text": "HN Description"
            }
        ]
    }
    mock_get.return_value = mock_response
    
    results = fetch_hacker_news(hours=12)
    assert len(results) == 1
    assert results[0]['title'] == "HN Idea"
    assert results[0]['link'] == "https://hn.example.com"
    assert results[0]['source'] == "Hacker News"

@patch('src.scraper.requests.get')
def test_fetch_hacker_news_error(mock_get):
    mock_get.side_effect = Exception("API error")
    results = fetch_hacker_news(hours=12)
    assert results == []

@patch('src.scraper.feedparser.parse')
def test_fetch_product_hunt_success(mock_parse):
    import time
    mock_feed = MagicMock()
    # Entry published very recently
    recent_time = time.gmtime(time.time() - 3600)
    mock_feed.entries = [
        MagicMock(
            title="PH Product",
            link="https://ph.example.com",
            summary="PH Summary",
            published_parsed=recent_time
        )
    ]
    mock_parse.return_value = mock_feed
    
    results = fetch_product_hunt(hours=12)
    assert len(results) == 1
    assert results[0]['title'] == "PH Product"
    assert results[0]['link'] == "https://ph.example.com"
    assert results[0]['source'] == "Product Hunt"

@patch('src.scraper.feedparser.parse')
def test_fetch_product_hunt_error(mock_parse):
    mock_parse.side_effect = Exception("Feed error")
    results = fetch_product_hunt(hours=12)
    assert results == []

@patch('src.scraper.requests.get')
def test_fetch_reddit_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    import time
    recent_timestamp = time.time() - 3600
    mock_response.json.return_value = {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Reddit Idea",
                        "permalink": "/r/saas/comments/xyz",
                        "selftext": "Reddit text",
                        "created_utc": recent_timestamp
                    }
                }
            ]
        }
    }
    mock_get.return_value = mock_response
    
    results = fetch_reddit(hours=12)
    assert len(results) == 2  # one for sideproject, one for saas
    assert results[0]['title'] == "Reddit Idea"
    assert results[0]['link'] == "https://www.reddit.com/r/saas/comments/xyz"
    assert results[0]['source'] == "Reddit"

@patch('src.scraper.requests.get')
def test_fetch_reddit_error(mock_get):
    mock_get.side_effect = Exception("Reddit connection error")
    results = fetch_reddit(hours=12)
    assert results == []

@patch('src.scraper.requests.get')
def test_fetch_github_trending_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <article class="Box-row">
      <h2 class="h3 lh-condensed"><a href="/trending/repo">owner / repo</a></h2>
      <p class="col-9 color-fg-muted my-1 pr-4">Repo description</p>
      <span class="d-inline-block float-sm-right">100 stars today</span>
    </article>
    """
    mock_get.return_value = mock_response
    
    results = fetch_github_trending(hours=12)
    assert len(results) == 1
    assert results[0]['title'] == "owner / repo"
    assert results[0]['link'] == "https://github.com/trending/repo"
    assert results[0]['source'] == "GitHub Trending"

@patch('src.scraper.requests.get')
def test_fetch_github_trending_error(mock_get):
    mock_get.side_effect = Exception("GitHub connection error")
    results = fetch_github_trending(hours=12)
    assert results == []
