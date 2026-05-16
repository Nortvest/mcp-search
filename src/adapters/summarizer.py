from langdetect import LangDetectException, detect
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer

from src.adapters.base import Summarizer
from src.domain.language_map import Language


class SumySummarizer(Summarizer):
    def __init__(self, max_sentences: int = 16) -> None:
        self._max_sentences = max_sentences

    def summarize(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        try:
            detected: str = detect(text)
        except LangDetectException:
            detected = "en"

        lang = Language(detected) if detected in Language else Language.en

        tokenizer = Tokenizer(lang.value)
        parser = PlaintextParser.from_string(text, tokenizer)
        summarizer = TextRankSummarizer()
        sentences_count = max(1, self._max_sentences)

        summary_doc = summarizer(parser.document, sentences_count)
        return " ".join(str(sentence) for sentence in summary_doc)
