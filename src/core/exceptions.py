class MaxContentLengthError(Exception):
    def __init__(self, content_length: int, max_content_length: int) -> None:
        self.max_content_length = max_content_length
        self.content_length = content_length

    def __str__(self) -> str:
        return (f"Response exceeds max content length of {self.max_content_length}. "
                f"Context length: {self.content_length}")
