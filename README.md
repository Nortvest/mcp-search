# MCP Search

Self-hosted MCP (Model Context Protocol) server for internet search with pluggable search engines. Currently supports SearXNG as the first integration. Deployable via Docker over HTTP transport.

## Features

- **MCP Protocol**: Exposes tools via JSON-RPC 2.0 over HTTP
- **Pluggable Engines**: Architecture-ready for adding new search engines (Google, Brave, Tavily, etc.)
- **Content Fetching**: Retrieve full page content from search results
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

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8080` |
| `MCP_NAME` | MCP server name | `mcp-search` |
| `ENGINE_SEARXNG_ENABLED` | Enable SearXNG engine | `true` |
| `ENGINE_SEARXNG_BASE_URL` | SearXNG API URL | - |
| `ENGINE_SEARXNG_API_KEY` | SearXNG API key (optional) | - |
| `DEFAULT_ENGINE` | Default search engine | `SEARXNG` |
| `MAX_CONTENT_LENGTH` | Max content fetch size in bytes | `50000` |
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | `10` |
| `LOG_LEVEL` | Logging level | `INFO` |

## MCP Tools

The server exposes two tools via MCP JSON-RPC over HTTP.

### Tool 1: `search`

Searches the internet using a configured search engine.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | yes | Search query |
| language | string | no | Language code (default: `"auto"`) |
| categories | string | no | SearXNG categories, comma-separated (default: `"general"`) |
| engine | string | no | Engine name from config (default: `DEFAULT_ENGINE`) |
| num_results | integer | no | Number of results (default: `10`, max: `50`) |


### Tool 2: `get_result`

Fetches full content from a URL returned by search.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | yes | URL to fetch content from |


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

The project follows Clean Architecture principles with four layers:

- **Presentation Layer** (`presentation/`) — Entry point, HTTP transport startup
- **Service Layer** (`services/`) — Business logic orchestration
- **Domain Layer** (`domain/`) — Pure business entities (DTOs)
- **Core Layer** (`core/`) — Config, logger, dependency injection

Inner layers know nothing about outer layers. Dependencies flow inward only. See `.opencode/plans/project-plan.md` for the full architecture diagram and design decisions.

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
3. Register in `DependencyContainer._register_adapters()` — map engine type string to class
4. Add config in `.env`: `ENGINE_<NAME>_TYPE=<engine_name>`, etc.

No changes needed in domain, services, server, or presentation layers.

## License

MIT
