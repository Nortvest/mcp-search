from enum import StrEnum


class Language(StrEnum):
    """ISO 639-1 language codes mapped to sumy Tokenizer language names."""

    en = "english"
    ru = "russian"
    de = "german"
    fr = "french"
    es = "spanish"
    it = "italian"
    pt = "portuguese"
    nl = "dutch"
    pl = "polish"
    tr = "turkish"
    zh = "chinese"
    ja = "japanese"
    ko = "korean"
