import pytest
from unittest.mock import patch, MagicMock
from src.analyzer import analyze_ideas

def test_analyze_ideas_success():
    sample_ideas = [
        {
            "title": "AI Code Assistant",
            "link": "https://example.com/1",
            "description": "An AI coding helper",
            "source": "Hacker News"
        },
        {
            "title": "SaaS Analytics Tool",
            "link": "https://example.com/2",
            "description": "Analytics for SaaS",
            "source": "Product Hunt"
        }
    ]

    with patch('src.analyzer.genai.Client') as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "## Business & SaaS\n1. SaaS Analytics Tool\n\n## Tech & Open Source\n1. AI Code Assistant\n\n## YouTube & Content\n1. Video idea"
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        result = analyze_ideas(sample_ideas, api_key="fake-api-key")

        mock_client_cls.assert_called_once_with(api_key="fake-api-key")
        mock_client_instance.models.generate_content.assert_called_once()
        
        call_kwargs = mock_client_instance.models.generate_content.call_args.kwargs
        assert call_kwargs.get("model") == "gemini-flash-latest"
        prompt = call_kwargs.get("contents")
        assert "KINH DOANH & SAAS" in prompt
        assert "CÔNG NGHỆ & OPEN-SOURCE" in prompt
        assert "YouTube & Content" in prompt
        assert "AI Code Assistant" in prompt

        assert result == mock_response.text

def test_analyze_ideas_empty():
    with patch('src.analyzer.genai.Client') as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Không có ý tưởng nào để phân tích."
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        result = analyze_ideas([], api_key="fake-api-key")
        assert "Không có ý tưởng" in result or result == mock_response.text

def test_analyze_ideas_api_exception():
    with patch('src.analyzer.genai.Client') as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.side_effect = Exception("API connection error")
        mock_client_cls.return_value = mock_client_instance

        result = analyze_ideas([{"title": "Test"}], api_key="fake-api-key")
        assert "Lỗi" in result or "Error" in result or "error" in result.lower()
