from pydantic import BaseModel, field_validator


class SearchQuery(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        return v

    engine: str
    num_results: int = 10
    language: str = "en"
    categories: str = "general"


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class ContentResult(BaseModel):
    url: str
    title: str
    text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
