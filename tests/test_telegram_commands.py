import pytest
from unittest.mock import patch, MagicMock
from src.telegram_commands import handle_command

def test_handle_help_command():
    with patch('src.telegram_commands.send_telegram_report') as mock_send:
        mock_send.return_value = True
        res = handle_command("/help", token="fake_token", chat_id="123")
        assert "Hướng dẫn sử dụng Bot IdeaRadar AI" in res
        mock_send.assert_called_once()

def test_handle_test_command():
    with patch('src.telegram_commands.send_telegram_report') as mock_send:
        mock_send.return_value = True
        res = handle_command("/test", token="fake_token", chat_id="123")
        assert "Bot đang hoạt động bình thường" in res
        mock_send.assert_called_once()

@patch('src.telegram_commands.run_pipeline')
def test_handle_run_command(mock_pipeline):
    with patch('src.telegram_commands.send_telegram_report') as mock_send:
        mock_send.return_value = True
        res = handle_command("/run", token="fake_token", chat_id="123", gemini_key="gemini_key")
        assert "Đang tiến hành quét" in res
        mock_pipeline.assert_called_once()
