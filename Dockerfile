FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-install-project
RUN python -c "import nltk;nltk.download('punkt')"

COPY src/ src/

EXPOSE 8080


CMD ["uv", "run", "src/presentation/app.py"]
