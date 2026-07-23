import pytest
from unittest.mock import patch, MagicMock
import os
from src.main import run_pipeline

@patch('src.main.fetch_hacker_news')
@patch('src.main.fetch_product_hunt')
@patch('src.main.fetch_reddit')
@patch('src.main.fetch_github_trending')
@patch('src.main.fetch_devto')
@patch('src.main.fetch_lobsters')
@patch('src.main.analyze_ideas')
@patch('src.main.send_telegram_report')
def test_run_pipeline_success(
    mock_telegram, mock_analyze, mock_lobsters, mock_devto, mock_github, mock_reddit, mock_ph, mock_hn
):
    mock_hn.return_value = [{"title": "HN Idea", "link": "http://a", "description": "A", "source": "HN"}]
    mock_ph.return_value = [{"title": "PH Idea", "link": "http://b", "description": "B", "source": "PH"}]
    mock_reddit.return_value = []
    mock_github.return_value = []
    mock_devto.return_value = []
    mock_lobsters.return_value = []
    mock_analyze.return_value = "AI Report Markdown"
    mock_telegram.return_value = True

    env_vars = {
        "TELEGRAM_BOT_TOKEN": "test_bot_token",
        "TELEGRAM_CHAT_ID": "test_chat_id",
        "GEMINI_API_KEY": "test_gemini_key"
    }

    with patch.dict('os.environ', env_vars):
        run_pipeline(debug=False)

    mock_hn.assert_called_once_with(hours=12)
    mock_ph.assert_called_once_with(hours=12)
    mock_reddit.assert_called_once_with(hours=12)
    mock_github.assert_called_once_with(hours=12)
    
    mock_analyze.assert_called_once()
    assert len(mock_analyze.call_args[0][0]) == 2
    assert mock_analyze.call_args[1]["api_key"] == "test_gemini_key"
    
    sent_msg = mock_telegram.call_args[0][0]
    assert "AI Report Markdown" in sent_msg
    assert "BÁO CÁO CẬP NHẬT Ý TƯỞNG AI" in sent_msg

@patch('src.main.fetch_hacker_news')
@patch('src.main.fetch_product_hunt')
@patch('src.main.fetch_reddit')
@patch('src.main.fetch_github_trending')
@patch('src.main.analyze_ideas')
@patch('src.main.send_telegram_report')
def test_run_pipeline_debug_mode(
    mock_telegram, mock_analyze, mock_github, mock_reddit, mock_ph, mock_hn
):
    mock_hn.return_value = [{"title": "HN Idea", "link": "http://a", "description": "A", "source": "HN"}]
    mock_ph.return_value = []
    mock_reddit.return_value = []
    mock_github.return_value = []
    mock_analyze.return_value = "AI Report Debug"

    env_vars = {
        "GEMINI_API_KEY": "test_gemini_key"
    }

    with patch.dict('os.environ', env_vars, clear=True):
        run_pipeline(debug=True)

    mock_analyze.assert_called_once()
    mock_telegram.assert_not_called()

@patch('src.main.fetch_hacker_news')
@patch('src.main.fetch_product_hunt')
@patch('src.main.fetch_reddit')
@patch('src.main.fetch_github_trending')
@patch('src.main.fetch_devto')
@patch('src.main.fetch_lobsters')
@patch('src.main.send_telegram_report')
def test_run_pipeline_no_ideas(
    mock_telegram, mock_lobsters, mock_devto, mock_github, mock_reddit, mock_ph, mock_hn
):
    mock_hn.return_value = []
    mock_ph.return_value = []
    mock_reddit.return_value = []
    mock_github.return_value = []
    mock_devto.return_value = []
    mock_lobsters.return_value = []

    env_vars = {
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "chat",
        "GEMINI_API_KEY": "key"
    }

    with patch.dict('os.environ', env_vars):
        run_pipeline(debug=False)

    mock_telegram.assert_called_once()
    assert "Không có ý tưởng mới" in mock_telegram.call_args[0][0]

@patch('src.main.fetch_hacker_news')
@patch('src.main.fetch_product_hunt')
@patch('src.main.fetch_reddit')
@patch('src.main.fetch_github_trending')
@patch('src.main.analyze_ideas')
def test_run_pipeline_missing_gemini_key(
    mock_analyze, mock_github, mock_reddit, mock_ph, mock_hn
):
    mock_hn.return_value = [{"title": "HN Idea"}]
    mock_ph.return_value = []
    mock_reddit.return_value = []
    mock_github.return_value = []

    with patch.dict('os.environ', {}, clear=True):
        run_pipeline(debug=False)

    mock_analyze.assert_not_called()
