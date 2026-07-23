import pytest
from unittest.mock import patch, MagicMock
from src.telegram_bot import send_telegram_report, split_message

def test_split_message_small_text():
    text = "Short report text."
    parts = split_message(text, max_chars=4000)
    assert len(parts) == 1
    assert parts[0] == text

def test_split_message_large_text():
    line = "Line of text to reach large size. " * 5 + "\n"
    large_text = line * 60
    assert len(large_text) > 4000

    parts = split_message(large_text, max_chars=4000)
    assert len(parts) > 1
    for part in parts:
        assert len(part) <= 4000

@patch('src.telegram_bot.requests.post')
def test_send_telegram_report_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    res = send_telegram_report("Report content", token="test-token", chat_id="12345")
    assert res is True
    mock_post.assert_called_once_with(
        "https://api.telegram.org/bottest-token/sendMessage",
        json={
            "chat_id": "12345",
            "text": "Report content",
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        },
        timeout=15
    )

@patch('src.telegram_bot.requests.post')
def test_send_telegram_report_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    res = send_telegram_report("Report content", token="test-token", chat_id="12345")
    assert res is False

def test_send_telegram_report_missing_credentials():
    assert send_telegram_report("Report content", token="", chat_id="12345") is False
    assert send_telegram_report("Report content", token="test-token", chat_id="") is False

@patch('src.telegram_bot.requests.post')
def test_send_telegram_report_large_text_splits(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    large_text = "Section content line.\n" * 300
    res = send_telegram_report(large_text, token="test-token", chat_id="12345")
    assert res is True
    assert mock_post.call_count > 1
