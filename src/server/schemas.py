from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from src.domain.models import SearchBatchResult, SearchResult

ISO_LANGUAGE_LENGTH = 2


class SearchInput(BaseModel):
    query: str
    language: str = "auto"
    categories: str = "general"
    engine: str | None = None  # resolves to DEFAULT_ENGINE if not provided
    num_results: int = Field(10, ge=1, le=50)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v in {"auto"} or len(v) != ISO_LANGUAGE_LENGTH or not v.isalpha():
            raise ValueError("language must be a 2-letter ISO code (e.g. 'en')")
        return v.lower()


class GetResultInput(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL")
        return v


class SearchOutput(BaseModel):
    results: list[SearchResult]


class GetResultOutput(BaseModel):
    url: str
    title: str
    text: str


class SearchBatchOutput(BaseModel):
    results: list[SearchBatchResult]
