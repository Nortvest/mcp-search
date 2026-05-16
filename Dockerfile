FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock ./
COPY src/ src/
RUN pip install uv && uv sync --frozen
RUN uv run - "import nltk;nltk.download('punkt', download_dir='/usr/share/nltk_data')"

EXPOSE 8080

CMD ["uv", "run", "src/presentation/app.py"]
