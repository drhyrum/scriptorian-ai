# Scriptorian - MCP Server for Scripture Study

An open-source Model Context Protocol (MCP) server providing comprehensive scripture study tools with AI-powered semantic search.

## Project Overview

This is a production-ready MCP server that provides:
- **Scripture fetching** with natural language references (e.g., "1 Ne 3:7-8", "Alma 32")
- **Reference parsing** to convert text references to structured JSON
- **Exact search** across all scriptures
- **Semantic search** using AI embeddings for meaning-based queries
- **Complete scripture data** for Old Testament, New Testament, Book of Mormon, Doctrine & Covenants, and Pearl of Great Price

## Project Structure

```
scriptorian/
├── src/scriptorian/
│   ├── server.py          # Main MCP server (stdio transport)
│   ├── server_sse.py      # SSE server for hosted deployment
│   ├── data_loader.py     # Scripture data loading
│   ├── reference_parser.py # Natural language reference parser
│   └── search.py          # Exact and semantic search
├── data/
│   ├── volumes.json       # Volume and book metadata
│   └── scripture/         # Individual chapter JSON files (1594 files)
├── tests/                 # Pytest test suite
├── scripts/
│   └── index_scriptures.py # Build vector database for semantic search
└── vector_db/             # ChromaDB vector database (created at runtime)
```

## Development Guidelines

### Running Locally

```bash
# Run the stdio server (for Claude Desktop)
uv run python -m scriptorian.server

# Run the SSE server (for hosted deployment)
uv run python -m scriptorian.server_sse

# Run tests
uv run pytest

# Index scriptures for semantic search
uv run python scripts/index_scriptures.py
```

### MCP Tools Provided

1. **fetch_scripture** - Fetch verses from natural language references
2. **parse_reference** - Parse reference strings to structured JSON
3. **exact_search** - Exact string matching across all scriptures
4. **semantic_search** - AI-powered semantic search (requires indexing)
5. **index_scriptures** - Build vector database for semantic search

### Data Format

Scripture data is in JSON format:
- `data/volumes.json` - Volume and book metadata
- `data/scripture/{book_id}.{chapter}.json` - Individual chapters
  - Example: `205.3.json` = 1 Nephi chapter 3 (book ID 205)

### Environment Variables

- `SCRIPTORIAN_DATA_PATH` - Custom path to scripture data (default: `./data`)
- `SCRIPTORIAN_VECTOR_DB_PATH` - Custom path to vector DB (default: `./vector_db`)
- `PORT` - Port for SSE server (default: 8000)

## Deployment

This server supports two deployment modes:

### Local (stdio)
For Claude Desktop and local use. Uses standard input/output for MCP communication.

### Hosted (SSE)
For web deployment (Railway, Render, etc.). Uses Server-Sent Events over HTTP.

See `DEPLOYMENT.md` for detailed deployment instructions.

## Architecture Notes

### Reference Parser
Parses natural language references like:
- Simple: "1 Ne 3:7"
- Ranges: "Alma 32:21-23"
- Multiple: "1 Ne 3:7; Alma 32:21"
- Complex: "Alma 1-2;4-5:10;James 1:5-6"

Returns structured JSON with book, chapter, and verse ranges.

### Search System

**Exact Search:**
- Case-insensitive by default
- Returns verse text with matched phrase in context

**Semantic Search:**
- Uses `sentence-transformers/all-MiniLM-L6-v2` (22M params, lightweight)
- ChromaDB for vector storage
- Returns verses ranked by semantic similarity

### Testing

Tests cover:
- Reference parser (various formats)
- Data loader (books, verses)
- Search functionality (exact and semantic)

Run with: `uv run pytest`

## Contributing

When contributing:
1. Follow existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting PR

## License

MIT License - see LICENSE file
