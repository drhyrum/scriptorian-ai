# Scriptorian

An MCP (Model Context Protocol) server for scripture study, providing tools for fetching, parsing, and searching LDS scriptures with both exact and semantic search capabilities.

## Features

- **Fetch Scripture References**: Natural language scripture lookup (e.g., "1 Ne 3:7-8", "Alma 32", "John 3:16")
- **Reference Parser**: Parse plain text references into structured JSON format
- **Exact Search**: Search for exact text matches across all scriptures
- **Semantic Search**: AI-powered semantic search to find verses by meaning, not just keywords
- **Complete Scripture Index**: Includes Old Testament, New Testament, Book of Mormon, Doctrine & Covenants, and Pearl of Great Price

## Installation

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/scriptorian.git
cd scriptorian

# Install with uv (recommended)
uv pip install -e .

# Or install with pip
pip install -e .
```

### Optional: Index for Semantic Search

Semantic search requires a one-time indexing process (takes 5-10 minutes):

```bash
uv run python scripts/index_scriptures.py
# or
python scripts/index_scriptures.py
```

This creates a vector database in the `vector_db/` directory for AI-powered semantic search.

### For Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Usage

### Running the MCP Server

The server can be run directly:

```bash
python -m scriptorian.server
```

### Configure with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "scriptorian": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/scriptorian",
        "run",
        "python",
        "-m",
        "scriptorian.server"
      ]
    }
  }
}
```

Replace `/path/to/scriptorian` with your actual installation path.

### Or use the hosted version (coming soon)

```json
{
  "mcpServers": {
    "scriptorian": {
      "url": "https://scriptorian.ai/sse"
    }
  }
}
```

### Available Tools

#### 1. `fetch_scripture`

Fetch scripture verses from a natural language reference.

**Parameters:**
- `reference` (string, required): Scripture reference (e.g., "1 Ne 3:7-8")

**Example:**
```json
{
  "reference": "1 Ne 3:7"
}
```

**Returns:** Full text of the requested verses in standard format.

#### 2. `parse_reference`

Parse a plain text scripture reference into structured JSON.

**Parameters:**
- `reference` (string, required): Plain text reference to parse

**Example:**
```json
{
  "reference": "Alma 1-2;4-5:10;jas 1:5-6"
}
```

**Returns:** Structured JSON with book, chapter, and verse information.

#### 3. `exact_search`

Search for exact string matches across all scriptures.

**Parameters:**
- `query` (string, required): Text to search for
- `case_sensitive` (boolean, optional): Whether search is case-sensitive (default: false)
- `max_results` (integer, optional): Maximum number of results (default: 50)

**Example:**
```json
{
  "query": "faith hope charity",
  "case_sensitive": false,
  "max_results": 10
}
```

**Returns:** List of matching verses with context highlighting.

#### 4. `semantic_search`

Perform AI-powered semantic search to find verses by meaning.

**Parameters:**
- `query` (string, required): Search query (phrase or question)
- `n_results` (integer, optional): Number of results to return (default: 10)

**Example:**
```json
{
  "query": "having faith in difficult times",
  "n_results": 5
}
```

**Returns:** Verses similar in meaning to the query, ranked by relevance.

**Note:** If you didn't index during installation, run `python scripts/index_scriptures.py` or use the `index_scriptures` tool first.

#### 5. `index_scriptures`

Index all scriptures for semantic search. Run this once before using `semantic_search`.

**Parameters:**
- `force_reindex` (boolean, optional): Force reindexing (default: false)

**Example:**
```json
{
  "force_reindex": false
}
```

**Note:** Initial indexing may take several minutes.

## Architecture

### Components

1. **Data Loader** (`data_loader.py`): Loads scripture data from JSON files
2. **Reference Parser** (`reference_parser.py`): Parses natural language references
3. **Search Engine** (`search.py`): Implements exact and semantic search
4. **MCP Server** (`server.py`): Exposes tools via Model Context Protocol

### Data Format

Scripture data is stored in JSON format with the following structure:
- `model/volumes.json`: Volume and book metadata
- `model/scripture/`: Individual chapter files (e.g., `205.3.json` for 1 Nephi 3)

### Semantic Search

Semantic search uses:
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (lightweight, 22M parameters)
- **Vector Database**: ChromaDB for efficient similarity search
- **Storage**: Persistent database in `vector_db/` directory

## Example Usage in Claude

### Fetching Scriptures

```
User: Can you show me 1 Nephi 3:7?

Claude: [Uses fetch_scripture tool]
**1 Ne. 3:7**

And it came to pass that I, Nephi, said unto my father: I will go and do
the things which the Lord hath commanded, for I know that the Lord giveth
no commandments unto the children of men, save he shall prepare a way for
them that they may accomplish the thing which he commandeth them.
```

### Exact Search

```
User: Find all verses about "faith and works"

Claude: [Uses exact_search tool]
Found 8 matches for 'faith and works'...
```

### Semantic Search

```
User: What scriptures talk about trusting God during trials?

Claude: [Uses semantic_search tool]
1. **1 Ne. 3:7** (score: 0.842)
   And it came to pass that I, Nephi, said unto my father: I will go and do...

2. **Ether 12:6** (score: 0.831)
   And now, I, Moroni, would speak somewhat concerning these things...
```

## Development

### Project Structure

```
scriptorian/
├── src/scriptorian/
│   ├── __init__.py
│   ├── data_loader.py      # Scripture data loading
│   ├── reference_parser.py # Reference parsing
│   ├── search.py           # Search functionality
│   └── server.py           # MCP server
├── polymer-citation-index/  # Scripture data
│   └── model/
│       ├── volumes.json
│       └── scripture/
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
└── README.md
```

### Running Tests

```bash
pytest
```

### Adding New Features

1. Add new tool to `server.py` in `_register_tools()`
2. Implement handler method (e.g., `_my_new_tool()`)
3. Update README with tool documentation

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
