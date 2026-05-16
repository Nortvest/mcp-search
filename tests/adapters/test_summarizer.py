from unittest.mock import MagicMock, patch

import pytest
from langdetect import LangDetectException

from src.adapters.base import Summarizer
from src.adapters.summarizer import SumySummarizer


class TestSummarizer:
    def test_abstract_class_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            Summarizer()  # type: ignore[abstract]


class TestSumySummarizer:
    @pytest.fixture
    def summarizer(self) -> SumySummarizer:
        return SumySummarizer(max_sentences=3)

    def test_summarize_returns_string(self, summarizer: SumySummarizer) -> None:
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = summarizer.summarize(text)
        assert isinstance(result, str)

    def test_summarize_english_text(self, summarizer: SumySummarizer) -> None:
        sentences = [f"This is sentence number {i} in English text." for i in range(1, 21)]
        text = " ".join(sentences)
        result = summarizer.summarize(text)
        assert len(result.split(". ")) >= 1

    def test_summarize_russian_text(self, summarizer: SumySummarizer) -> None:
        sentences = [f"Это предложение номер {i} на русском языке." for i in range(1, 21)]
        text = " ".join(sentences)
        result = summarizer.summarize(text)
        assert len(result.strip()) > 0

    def test_summarize_empty_text(self, summarizer: SumySummarizer) -> None:
        result = summarizer.summarize("")
        assert not result

    def test_summarize_whitespace_only(self, summarizer: SumySummarizer) -> None:
        result = summarizer.summarize("   \n\t  ")
        assert not result

    @patch("langdetect.detect")
    def test_summarize_fallback_on_detect_error(self, mock_detect: MagicMock, summarizer: SumySummarizer) -> None:
        mock_detect.side_effect = LangDetectException("message", "error")
        text = "This is a test sentence. Another sentence here."
        result = summarizer.summarize(text)
        assert isinstance(result, str)

    @patch("langdetect.detect")
    def test_summarize_unknown_language_fallback(self, mock_detect: MagicMock, summarizer: SumySummarizer) -> None:
        mock_detect.return_value = "xx"
        text = "This is a test sentence. Another sentence here."
        result = summarizer.summarize(text)
        assert isinstance(result, str)

    def test_summarize_short_text(self, summarizer: SumySummarizer) -> None:
        text = "Only one sentence in this short text."
        result = summarizer.summarize(text)
        assert len(result.strip()) > 0

    @patch("langdetect.detect")
    def test_summarize_preserves_language(self, mock_detect: MagicMock, summarizer: SumySummarizer) -> None:
        mock_detect.return_value = "en"
        text = "Hello world. This is a test."
        result = summarizer.summarize(text)
        assert "hello" in result.lower() or "world" in result.lower()

    def test_summarize_with_custom_max_sentences(self) -> None:
        custom_summarizer = SumySummarizer(max_sentences=1)
        text = " ".join([f"Sentence number {i}." for i in range(1, 31)])
        result = custom_summarizer.summarize(text)
        assert isinstance(result, str)
