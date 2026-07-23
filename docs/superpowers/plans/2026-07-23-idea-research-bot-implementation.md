# AI Idea Research Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an automated daily research reporter bot that scrapes Hacker News, Product Hunt, Reddit, and GitHub Trending, filters and analyzes the ideas using the Gemini 2.5 Flash API, and reports 5 ideas per category (Business, Technology, YouTube) to Telegram twice daily at 9:00 AM and 2:00 PM VN time.

**Architecture:** A lightweight Python script containing modular scraper, analyzer, and publisher components. It runs via GitHub Actions scheduled workflow, with state managed within each run (filtering items to the last 12 hours) and API secrets retrieved from GitHub Secrets.

**Tech Stack:** Python 3.11, `requests`, `feedparser`, `beautifulsoup4`, `google-genai`, `pytest`, `pytest-mock`.

## Global Constraints
- Target platform: Python 3.11 on GitHub Actions Ubuntu Runner.
- Use the official Google Gen AI SDK (`google-genai`) for Gemini API interactions.
- All report content must be formatted in clean Vietnamese Markdown.
- Limit scraping data to the past 12 hours.
- Telegram message split limit: max 4096 characters per message.

---

### Task 1: Scraper Module

**Files:**
- Create: `src/scraper.py`
- Test: `tests/test_scraper.py`

**Interfaces:**
- Consumes: None
- Produces: 
  - `fetch_hacker_news(hours: int = 12) -> list[dict]`
  - `fetch_product_hunt(hours: int = 12) -> list[dict]`
  - `fetch_reddit(hours: int = 12) -> list[dict]`
  - `fetch_github_trending(hours: int = 12) -> list[dict]`
  
Each dictionary in the returned list contains keys: `title`, `link`, `description`, `source`, `created_at` (epoch timestamp).

- [ ] **Step 1: Write the failing test**
  Create `tests/test_scraper.py` containing mocks for Hacker News, Product Hunt, Reddit, and GitHub trending.

  ```python
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
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_scraper.py`
  Expected: FAIL (ModuleNotFoundError: No module named 'src.scraper')

- [ ] **Step 3: Write minimal implementation**
  Create `src/scraper.py` implementing the APIs and RSS/HTML parsers.
  ```python
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
                      "description": entry.summary,
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
                          "source": f"Reddit",
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
              title_a = article.select_one("h2.h3 lh-condensed a, h2 a, h1 a")
              if not title_a:
                  title_a = article.select_one("h2 a") or article.select_one("h1 a")
              if not title_a:
                  continue
              href = title_a.get("href", "")
              repo_name = title_a.text.strip().replace("\n", "").replace(" ", "")
              link = f"https://github.com{href}"
              
              desc_p = article.select_one("p.col-9, p.color-fg-muted")
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
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_scraper.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add src/scraper.py tests/test_scraper.py
  git commit -m "feat: implement scraper module with unit tests"
  ```

---

### Task 2: AI Analyzer Module

**Files:**
- Create: `src/analyzer.py`
- Test: `tests/test_analyzer.py`

**Interfaces:**
- Consumes: None
- Produces:
  - `analyze_ideas(raw_ideas: list[dict], api_key: str) -> str`

- [ ] **Step 1: Write the failing test**
  Create `tests/test_analyzer.py`. We will mock the `google-genai` client API call.

  ```python
  import pytest
  from unittest.mock import patch, MagicMock
  from src.analyzer import analyze_ideas

  @patch('src.analyzer.client.Client')
  def test_analyze_ideas_success(mock_client_class):
      mock_client = MagicMock()
      mock_client_class.return_value = mock_client
      
      # Mock Gemini API response
      mock_response = MagicMock()
      mock_response.text = "💡 I. KINH DOANH & SAAS\n1. AI Business Idea..."
      mock_client.models.generate_content.return_value = mock_response
      
      raw_ideas = [
          {"title": "Idea 1", "link": "http://example.com/1", "description": "Desc 1", "source": "HN"}
      ]
      
      result = analyze_ideas(raw_ideas, api_key="fake-key")
      assert "💡 I. KINH DOANH & SAAS" in result
      mock_client.models.generate_content.assert_called_once()
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_analyzer.py`
  Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**
  Create `src/analyzer.py` using `google-genai` SDK.
  ```python
  import json
  from google import genai
  from google.genai import types

  def analyze_ideas(raw_ideas: list[dict], api_key: str) -> str:
      if not raw_ideas:
          return "Không tìm thấy ý tưởng mới nào trong 12 giờ qua."
      
      # Setup client
      client = genai.Client(api_key=api_key)
      
      # Convert raw ideas to a readable text representation for the model
      ideas_summary = ""
      for i, idea in enumerate(raw_ideas, 1):
          ideas_summary += f"{i}. Tiêu đề: {idea['title']}\n"
          ideas_summary += f"   Nguồn: {idea['source']} ({idea['link']})\n"
          ideas_summary += f"   Mô tả: {idea['description']}\n\n"
          
      prompt = f"""
Bạn là chuyên gia phân tích kinh doanh, công nghệ và phát triển nội dung YouTube.
Dưới đây là danh sách các ý tưởng, bài đăng công nghệ và sản phẩm mới nổi bật trong 12 giờ qua:

{ideas_summary}

Hãy chọn ra chính xác:
- 5 ý tưởng nổi bật nhất về lĩnh vực **Kinh doanh & SaaS**
- 5 ý tưởng nổi bật nhất về lĩnh vực **Công nghệ & Open-Source / AI Tools**
- 5 ý tưởng làm video **YouTube & Content** dựa trên các xu hướng này.

Phản hồi của bạn PHẢI tuân thủ nghiêm ngặt định dạng Markdown Tiếng Việt sau đây. KHÔNG thêm bất cứ lời mở đầu hay kết bài nào khác ngoài mẫu:

💡 I. KINH DOANH & SAAS (5 ý tưởng nổi bật)
1. [Tên ý tưởng] ([Nguồn](link))
   - Tóm tắt: [Tóm tắt ngắn gọn 2-3 câu]
   - Tiềm năng kinh doanh: [Điểm số/10] - [Lý do ngắn gọn]
   - Khả năng code bằng AI: [Điểm số/10] - [Gợi ý cách code nhanh và techstack ví dụ Cursor, Bolt.new, Lovable]

2. ... (lần lượt đến 5)

🛠 II. CÔNG NGHỆ & OPEN-SOURCE (5 ý tưởng nổi bật)
1. [Tên dự án/Công cụ] ([Nguồn](link))
   - Tóm tắt tính năng: [Tóm tắt ngắn gọn 2-3 câu]
   - Khả năng ứng dụng: [Gợi ý cách áp dụng vào công việc/dự án cá nhân]
   - Gợi ý techstack làm bằng AI: [Cursor / Lovable / Bolt.new]

2. ... (lần lượt đến 5)

📹 III. Ý TƯỞNG KÊNH YOUTUBE & CONTENT (5 ý tưởng nổi bật)
1. [Tiêu đề video gợi ý]
   - Chủ đề cốt lõi: [Chủ đề công nghệ/kinh doanh làm gốc]
   - Kịch bản/Góc tiếp cận: [Gợi ý cách làm video thu hút người xem]
   - Tiêu đề & Thumbnail gợi ý: [Ý tưởng ảnh thu nhỏ và tiêu đề giật gân]

2. ... (lần lượt đến 5)
"""
      try:
          response = client.models.generate_content(
              model='gemini-2.5-flash',
              contents=prompt
          )
          return response.text or "AI không phản hồi."
      except Exception as e:
          return f"Lỗi gọi Gemini API: {str(e)}"
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_analyzer.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add src/analyzer.py tests/test_analyzer.py
  git commit -m "feat: implement analyzer module using gemini api"
  ```

---

### Task 3: Telegram Bot Publisher

**Files:**
- Create: `src/telegram_bot.py`
- Test: `tests/test_telegram_bot.py`

**Interfaces:**
- Consumes: None
- Produces:
  - `send_telegram_report(report_text: str, token: str, chat_id: str) -> bool`
  - `split_message(text: str, max_chars: int = 4000) -> list[str]`

- [ ] **Step 1: Write the failing test**
  Create `tests/test_telegram_bot.py`. We will mock post requests to Telegram API and verify message splitting works.

  ```python
  import pytest
  from unittest.mock import patch, MagicMock
  from src.telegram_bot import send_telegram_report, split_message

  def test_split_message_no_split():
      text = "Short text"
      parts = split_message(text, max_chars=100)
      assert len(parts) == 1
      assert parts[0] == "Short text"

  def test_split_message_with_split():
      text = "Section 1\n---\nSection 2\n---\nSection 3"
      # Split by delimiter if possible
      parts = split_message(text, max_chars=20)
      assert len(parts) > 1

  @patch('src.telegram_bot.requests.post')
  def test_send_telegram_report_success(mock_post):
      mock_response = MagicMock()
      mock_response.status_code = 200
      mock_post.return_value = mock_response
      
      res = send_telegram_report("Hello Telegram", token="token", chat_id="123")
      assert res is True
      mock_post.assert_called_once()
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_telegram_bot.py`
  Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**
  Create `src/telegram_bot.py`.
  ```python
  import requests

  def split_message(text: str, max_chars: int = 4000) -> list[str]:
      if len(text) <= max_chars:
          return [text]
          
      # Split by categories (I, II, III) if possible
      parts = []
      lines = text.split("\n")
      current_part = ""
      
      for line in lines:
          if len(current_part) + len(line) + 1 > max_chars:
              if current_part:
                  parts.append(current_part)
                  current_part = line
              else:
                  # Force split line if a single line is too long
                  parts.append(line[:max_chars])
                  current_part = line[max_chars:]
          else:
              if current_part:
                  current_part += "\n" + line
              else:
                  current_part = line
      if current_part:
          parts.append(current_part)
      return parts

  def send_telegram_report(report_text: str, token: str, chat_id: str) -> bool:
      if not token or not chat_id:
          print("Lỗi: Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
          return False
          
      parts = split_message(report_text, max_chars=4000)
      success = True
      
      for part in parts:
          url = f"https://api.telegram.org/bot{token}/sendMessage"
          # Using HTML parse mode is safer than MarkdownV2 since MDV2 requires complex escaping.
          # We'll use standard markdown first or pass plain formatting. Let's send plain / html.
          # Telegram supports basic markdown formatting in parse_mode='Markdown'.
          payload = {
              "chat_id": chat_id,
              "text": part,
              "parse_mode": "Markdown",
              "disable_web_page_preview": True
          }
          try:
              r = requests.post(url, json=payload, timeout=15)
              if r.status_code != 200:
                  print(f"Telegram API error: {r.status_code} - {r.text}")
                  success = False
          except Exception as e:
              print(f"Exception sending to Telegram: {e}")
              success = False
              
      return success
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_telegram_bot.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add src/telegram_bot.py tests/test_telegram_bot.py
  git commit -m "feat: implement telegram bot publisher with split support"
  ```

---

### Task 4: Orchestration Script

**Files:**
- Create: `src/main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes:
  - `src/scraper.py`
  - `src/analyzer.py`
  - `src/telegram_bot.py`
- Produces:
  - CLI application running orchestration flow.

- [ ] **Step 1: Write the failing test**
  Create `tests/test_main.py` to mock scraper, analyzer, telegram bot, and run the pipeline.

  ```python
  import pytest
  from unittest.mock import patch, MagicMock
  import sys
  from src.main import run_pipeline

  @patch('src.main.fetch_hacker_news')
  @patch('src.main.fetch_product_hunt')
  @patch('src.main.fetch_reddit')
  @patch('src.main.fetch_github_trending')
  @patch('src.main.analyze_ideas')
  @patch('src.main.send_telegram_report')
  def test_run_pipeline_success(
      mock_telegram, mock_analyze, mock_github, mock_reddit, mock_ph, mock_hn
  ):
      mock_hn.return_value = [{"title": "HN Idea", "link": "http://a", "description": "A", "source": "HN"}]
      mock_ph.return_value = []
      mock_reddit.return_value = []
      mock_github.return_value = []
      mock_analyze.return_value = "AI report"
      mock_telegram.return_value = True
      
      env_vars = {
          "TELEGRAM_BOT_TOKEN": "token",
          "TELEGRAM_CHAT_ID": "chat",
          "GEMINI_API_KEY": "gemini"
      }
      
      with patch.dict('os.environ', env_vars):
          run_pipeline(debug=False)
          
      mock_hn.assert_called_once()
      mock_analyze.assert_called_once()
      mock_telegram.assert_called_once_with("AI report", "token", "chat")
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_main.py`
  Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**
  Create `src/main.py`.
  ```python
  import os
  import sys
  import argparse
  from src.scraper import (
      fetch_hacker_news,
      fetch_product_hunt,
      fetch_reddit,
      fetch_github_trending
  )
  from src.analyzer import analyze_ideas
  from src.telegram_bot import send_telegram_report

  def run_pipeline(debug: bool = False):
      print("Bắt đầu thu thập dữ liệu trong 12 giờ qua...")
      
      hn_ideas = fetch_hacker_news(hours=12)
      ph_ideas = fetch_product_hunt(hours=12)
      reddit_ideas = fetch_reddit(hours=12)
      github_ideas = fetch_github_trending(hours=12)
      
      all_ideas = hn_ideas + ph_ideas + reddit_ideas + github_ideas
      print(f"Tổng hợp thu thập được {len(all_ideas)} tin tức thô.")
      
      if not all_ideas:
          msg = "Không có ý tưởng mới nào được tìm thấy trong 12 giờ qua."
          print(msg)
          if not debug:
              token = os.environ.get("TELEGRAM_BOT_TOKEN")
              chat_id = os.environ.get("TELEGRAM_CHAT_ID")
              send_telegram_report(msg, token, chat_id)
          return

      # Get Gemini API key
      gemini_key = os.environ.get("GEMINI_API_KEY")
      if not gemini_key:
          print("Lỗi: Thiếu GEMINI_API_KEY.")
          return
          
      print("Đang gửi dữ liệu sang Gemini API để phân tích...")
      report = analyze_ideas(all_ideas, api_key=gemini_key)
      
      if debug:
          print("\n=== [DEBUG MODE] BÁO CÁO CỦA BẠN ===\n")
          print(report)
          print("\n====================================\n")
      else:
          print("Đang gửi báo cáo qua Telegram...")
          token = os.environ.get("TELEGRAM_BOT_TOKEN")
          chat_id = os.environ.get("TELEGRAM_CHAT_ID")
          if send_telegram_report(report, token, chat_id):
              print("Gửi báo cáo thành công!")
          else:
              print("Gửi báo cáo thất bại.")

  if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="AI Idea Research Reporter Bot")
      parser.add_argument("--debug", action="store_true", help="Chạy chế độ debug, in ra màn hình thay vì gửi Telegram")
      args = parser.parse_args()
      
      # Make sure env vars are present if not debug
      if not args.debug:
          if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
              print("Lỗi: Cần cấu hình TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID ở môi trường hệ thống.")
              sys.exit(1)
              
      if not os.environ.get("GEMINI_API_KEY"):
          print("Lỗi: Cần cấu hình GEMINI_API_KEY.")
          sys.exit(1)
          
      run_pipeline(debug=args.debug)
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_main.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add src/main.py tests/test_main.py
  git commit -m "feat: add pipeline orchestrator and main CLI script"
  ```

---

### Task 5: Automation Workflow Setup

**Files:**
- Create: `.github/workflows/daily_report.yml`

**Interfaces:**
- Consumes: `src/main.py`
- Produces: Scheduled GitHub Actions workflow.

- [ ] **Step 1: Write the config file**
  Create `.github/workflows/daily_report.yml`

  ```yaml
  name: Daily AI Idea Research Report

  on:
    schedule:
      - cron: '0 2 * * *'  # 9:00 AM VN Time (02:00 UTC)
      - cron: '0 7 * * *'  # 2:00 PM VN Time (07:00 UTC)
    workflow_dispatch:      # Allows manual trigger

  jobs:
    run-report:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout repository
          uses: actions/checkout@v4

        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: '3.11'
            cache: 'pip'

        - name: Install dependencies
          run: |
            pip install requests feedparser beautifulsoup4 google-genai pytest pytest-mock

        - name: Run unit tests
          run: |
            pytest tests/

        - name: Run research script
          env:
            TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
            TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
            GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          run: python src/main.py
  ```

- [ ] **Step 2: Commit workflow config**
  ```bash
  git add .github/workflows/daily_report.yml
  git commit -m "ci: configure daily report workflow with tests"
  ```
