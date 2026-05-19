# MCP Search

Self-hosted MCP (Model Context Protocol) server for internet search with pluggable search engines. Currently supports SearXNG as the first integration. Deployable via Docker over HTTP transport.

## Features

- **MCP Protocol**: Exposes tools via JSON-RPC 2.0 over HTTP
- **Pluggable Engines**: Architecture-ready for adding new search engines (Google, Brave, Tavily, etc.)
- **Content Fetching**: Retrieve full page content from search results
- **Deep Search**: Combined search + content fetching + summarization in a single tool call
- **Docker Deployment**: Single-command deployment with docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- A SearXNG instance running locally or remotely (or deploy one alongside)

### Running with Docker Compose

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and set your SearXNG base URL:

```env
ENGINE_SEARXNG_BASE_URL=http://localhost:8081
```

3. Start both MCP Search and a SearXNG instance:

```bash
docker compose --profile all up -d
```

MCP Search will be available at `http://localhost:8080`.

### Running MCP Search Only (with external SearXNG)

If you already have a SearXNG instance running, start only the search server:

```bash
docker-compose up -d
```

## Configuration

All configuration is done via environment variables in the `.env` file. See `.env.example` for all available options:

| Variable | Description | Default      |
|----------|-------------|--------------|
| `MCP_HOST` | Server bind address | `0.0.0.0`    |
| `MCP_PORT` | Server port | `8080`       |
| `MCP_NAME` | MCP server name | `mcp-search` |
| `ENGINE_SEARXNG_ENABLED` | Enable SearXNG engine | `true`       |
| `ENGINE_SEARXNG_TYPE` | Engine type identifier | `searxng`    |
| `ENGINE_SEARXNG_BASE_URL` | SearXNG API URL | -            |
| `ENGINE_SEARXNG_API_KEY` | SearXNG API key (optional) | -            |
| `DEFAULT_ENGINE` | Default search engine | `SEARXNG`    |
| `MAX_CONTENT_LENGTH` | Max content fetch size in bytes | `50000`      |
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | `10`         |
| `SUMMARY_ENABLE` | Enable content summarization | `true`       |
| `SUMMARY_MAX_CONTENT_LENGTH_READABILITY` | Max content length for readability parsing | `512000`     |
| `SUMMARY_MAX_SENTENCES` | Max sentences in summarized content | `16`         |
| `LOG_LEVEL` | Logging level | `INFO`       |

## MCP Tools

The server exposes six tools via MCP JSON-RPC over HTTP.

### Tool 1: `search`

Searches the internet using a configured search engine.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | yes | Search query |
| language | string | no | Language code, must be 2-letter ISO code (default: `"auto"`) |
| categories | string | no | SearXNG categories, comma-separated (default: `"general"`) |
| engine | string | no | Engine name from config (default: `DEFAULT_ENGINE`) |
| num_results | integer | no | Number of results (default: `10`, max: `50`) |

### Tool 2: `search_batch`

Searches using multiple queries in parallel.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queries | array of objects | yes | Array of search query objects (same parameters as `search`) |

### Tool 3: `fetch_website`

Fetches full content from a URL returned by search.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | yes | URL to fetch content from |

### Tool 4: `fetch_and_summarize_website`

Fetches full content from a URL and returns a concise summary.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | yes | URL to fetch and summarize content from |

### Tool 5: `deep_search`

Searches the internet, then fetches and summarizes content from top results for deeper analysis. Combines search and content summarization in a single tool call, returning enriched results with snippet + full summarized content.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | yes | Search query |
| language | string | no | Language code, must be 2-letter ISO code (default: `"auto"`) |
| categories | string | no | SearXNG categories, comma-separated (default: `"general"`) |
| engine | string | no | Engine name from config (default: `DEFAULT_ENGINE`) |
| num_results | integer | no | Number of results (default: `10`, max: `50`) |

### Tool 6: `deep_search_batch`

Deep search with multiple queries — searches and fetches+summarizes content from top results for each query in parallel.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queries | array of objects | yes | Array of search query objects (same parameters as `deep_search`) |


### MCP Endpoint

- **URL:** `POST http://localhost:8080/mcp`
- **Content-Type:** `application/json`

## SearXNG Setup Guide

### Option 1: Deploy with Docker Compose

The included `docker-compose.yml` has a SearXNG service ready to use. Start it alongside MCP Search:

```bash
docker-compose --profile all up -d
```

This deploys SearXNG on port `8081`. Set your `.env`:

```env
ENGINE_SEARXNG_BASE_URL=http://searxng:8080
```

### Option 2: Deploy SearXNG Separately

Install SearXNG using their official Docker setup. Once running, configure the base URL in `.env`.

### Option 3: Use a Public Instance

Use any public SearXNG instance (e.g., `https://search.example.com`). If the instance requires an API key, set `ENGINE_SEARXNG_API_KEY` in your `.env`.

## Architecture

The project follows Clean Architecture principles with five layers:

- **Presentation Layer** (`presentation/`) — Entry point, HTTP transport startup
- **Server Layer** (`server/`) — MCP protocol tools and schemas
- **Service Layer** (`services/`) — Business logic orchestration
- **Adapters Layer** (`adapters/`) — External integrations (search engines, content fetchers)
- **Domain Layer** (`domain/`) — Pure business entities (DTOs)
- **Core Layer** (`core/`) — Config, logger, dependency injection

Inner layers know nothing about outer layers. Dependencies flow inward only.

## Development

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) — fast Python package installer

### Setup

```bash
# Install dependencies
uv sync

# Run linter
uv run ruff check .

# Run type checker
uv run mypy .

# Run tests
uv run pytest
```

## Adding a New Search Engine

The architecture makes it easy to add new engines:

1. Implement an `EngineFetcher` subclass for the new engine (receives `HttpClient` via DI, returns `SearchResponse`)
2. Implement a `SearchEngineAdapter` subclass (only implements `search()`, receives fetcher via DI)
3. Register in `DependencyContainer.build()` — map engine type string to class
4. Add config in `.env`: `ENGINE_<NAME>_TYPE=<engine_name>`, etc.

No changes needed in domain, services, server, or presentation layers.

## License

MIT
