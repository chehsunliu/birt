# Birt Backend

FastAPI backend service for the Birt platform.

## Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Setup

Install dependencies:

```bash
uv sync
```

## Development

### Running the Server

Start the development server:

```bash
uv run uvicorn birt_backend.app:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### Running Tests

Run unit tests:

```bash
make ut
```

Run integration tests:

```bash
make it
```

### Code Quality

Format code (imports, formatting, linting fixes):

```bash
make fmt
```

Check code quality (formatting, linting, type checking):

```bash
make check
```

## Workspace

This project is part of a `uv` workspace. Related packages:
- `birt-shared` - Shared utilities and types
- `birt-testkit` - Testing utilities

These are automatically resolved from the workspace when using `uv`.
