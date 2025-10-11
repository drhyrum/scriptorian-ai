# Scriptorian Project Summary

## Overview

Scriptorian is a complete MCP (Model Context Protocol) server implementation for scripture study, providing AI-powered tools for accessing and searching LDS scriptures.

## What Was Built

### Core Components

1. **Data Loader** (`src/scriptorian/data_loader.py` - 150 lines)
   - Loads scripture data from JSON files
   - Provides verse, book, and volume models
   - Handles all five volumes of scripture (OT, NT, BoM, D&C, PGP)

2. **Reference Parser** (`src/scriptorian/reference_parser.py` - 303 lines)
   - Parses natural language scripture references
   - Supports complex formats: "Alma 1-2;4-5:10;jas 1:5-6"
   - Returns structured JSON matching the API specification
   - Handles all common book abbreviations

3. **Search Engine** (`src/scriptorian/search.py` - 289 lines)
   - **Exact Search**: Fast string matching with context extraction
   - **Semantic Search**: AI-powered meaning-based search using:
     - sentence-transformers (all-MiniLM-L6-v2 model)
     - ChromaDB vector database
     - Persistent indexing for fast repeated searches

4. **MCP Server** (`src/scriptorian/server.py` - 419 lines)
   - Five MCP tools exposed:
     - `fetch_scripture`: Retrieve verses by reference
     - `parse_reference`: Parse references to JSON
     - `exact_search`: Find exact text matches
     - `semantic_search`: Find verses by meaning
     - `index_scriptures`: Build semantic search index
   - Full async/await support
   - Proper error handling
   - JSON and formatted text output

### Supporting Files

- `pyproject.toml`: Project configuration with dependencies
- `README.md`: Complete documentation (200+ lines)
- `QUICKSTART.md`: Step-by-step setup guide
- `mcp_config_example.json`: Example MCP configuration
- `tests/test_reference_parser.py`: Unit tests
- `.gitignore`: Proper Python gitignore

## Project Structure

```
scriptorian/
├── src/scriptorian/
│   ├── __init__.py
│   ├── __main__.py
│   ├── data_loader.py
│   ├── reference_parser.py
│   ├── search.py
│   └── server.py
├── polymer-citation-index/
│   └── model/
│       ├── volumes.json
│       └── scripture/  (1500+ JSON files)
├── tests/
│   └── test_reference_parser.py
├── pyproject.toml
├── README.md
├── QUICKSTART.md
├── PROJECT_SUMMARY.md
└── mcp_config_example.json
```

## Key Features

### 1. Natural Language Reference Parsing
```
Input: "1 Ne 3:7-8"
Output: 1 Nephi chapter 3, verses 7-8 with full text
```

### 2. Exact Search
- Fast full-text search across all scriptures
- Context extraction with keyword highlighting
- Case-sensitive and case-insensitive options

### 3. Semantic Search
- Understands meaning, not just keywords
- Finds relevant verses even with different wording
- Ranked by relevance score
- One-time indexing, persistent database

### 4. Complete Scripture Coverage
- Old Testament (39 books)
- New Testament (27 books)
- Book of Mormon (15 books)
- Doctrine & Covenants (138 sections)
- Pearl of Great Price (5 books)

## Dependencies

### Required
- `mcp>=0.9.0` - Model Context Protocol
- `numpy>=1.24.0` - Numerical operations
- `sentence-transformers>=2.2.0` - Embedding model
- `chromadb>=0.4.0` - Vector database
- `torch>=2.0.0` - PyTorch (for embeddings)

### Optional (Development)
- `pytest>=7.4.0`
- `pytest-asyncio>=0.21.0`

## Installation & Usage

### Quick Start

```bash
# Install dependencies
cd /Users/hyrum/src/scriptorian
uv pip install -e .

# Test installation
python -c "from src.scriptorian.data_loader import ScriptureLoader; print('OK')"

# Run standalone
python -m scriptorian.server
```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scriptorian": {
      "command": "python",
      "args": ["-m", "scriptorian.server"],
      "cwd": "/Users/hyrum/src/scriptorian",
      "env": {
        "PYTHONPATH": "/Users/hyrum/src/scriptorian/src"
      }
    }
  }
}
```

## Example Interactions

### Fetch Scripture
```
User: Show me 1 Nephi 3:7