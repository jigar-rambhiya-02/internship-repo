"""
tests/test_contextualizer.py

Unit tests for the context prefix generator, using a mock Groq client
to avoid real API calls in the test suite.
"""

import pytest
from unittest.mock import MagicMock
from production_rag.contextualizer import generate_context_prefix


def _make_mock_groq(response_text: str):
    """Helper: returns a mock Groq client that yields response_text."""
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_generate_context_prefix_returns_string():
    mock_client = _make_mock_groq("This chunk discusses annual revenue growth in section 2.")
    result = generate_context_prefix("Revenue grew 12%.", "Annual Report 2023", mock_client)
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_context_prefix_strips_whitespace():
    mock_client = _make_mock_groq("  This chunk is about headcount growth.  \n")
    result = generate_context_prefix("Headcount grew.", "Report", mock_client)
    assert result == "This chunk is about headcount growth."


def test_generate_context_prefix_fallback_on_api_error():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API timeout")
    result = generate_context_prefix("Some text.", "Doc", mock_client)
    assert result == ""


def test_groq_called_with_correct_model():
    mock_client = _make_mock_groq("Context sentence.")
    generate_context_prefix("Sample text about revenue.", "Report.pdf", mock_client)
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "llama-3.3-70b-versatile"
    assert call_kwargs["temperature"] == 0
