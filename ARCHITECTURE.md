# Scriptorian Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude Desktop                        │
│                     (MCP Client)                            │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol (stdio)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Scriptorian MCP Server                     │
│                   (server.py)                               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool Registry                                       │  │
│  │  • fetch_scripture                                   │  │
│  │  • parse_reference                                   │  │
│  │  • exact_search                                      │  │
│  │  • semantic_search                                   │  │
│  │  • index_scriptures                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────┬────────────┬────────────┬───────────────────────┘
          │            │            │
┌─────────▼────────┐ ┌─▼──────────┐ ┌▼──────────────────────┐
│ Reference Parser │ │ Data Loader│ │ Search Engines        │
│ (reference_      │ │ (data_     │ │ (search.py)           │
│  parser.py)      │ │  loader.py)│ │                       │
│                  │ │            │ │ ┌──────────────────┐  │
│ • Parse refs     │ │ • Load     │ │ │ Exact Search     │  │
│ • Validate       │ │   volumes  │ │ │ • String match   │  │
│ • Format         │ │ • Load     │ │ │ • Context extract│  │
│                  │ │   verses   │ │ └──────────────────┘  │
│                  │ │ • Book     │ │                       │
│                  │ │   lookup   │ │ ┌──────────────────┐  │
│                  │ │            │ │ │ Semantic Search  │  │
│                  │ │            │ │ │ • Embeddings     │  │
│                  │ │            │ │ │ • Vector DB      │  │
│                  │ │            │ │ │ • Ranking        │  │
│                  │ │            │ │ └──────────────────┘  │
└──────────────────┘ └─────┬──────┘ └───────┬───────────────┘
                           │                │
                     ┌─────▼────────┐  ┌────▼────────────────┐
                     │ Scripture    │  │ AI Models & Vector  │
                     │ Data (JSON)  │  │ Database            │
                     │              │  │                     │
                     │ • volumes    │  │ • sentence-         │
                     │ • books      │  │   transformers      │
                     │ • chapters   │  │ • ChromaDB          │
                     │ • verses     │  │ • Embeddings cache  │
                     └──────────────┘  └─────────────────────┘
```

## Data Flow

### 1. Fetch Scripture

```
User Request: "Show me 1 Nephi 3:7"
      │
      ▼
┌─────────────────────┐
│ fetch_scripture     │
│ tool called         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ ReferenceParser     │
│ parses "1 Ne 3:7"   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ ScriptureLoader     │
│ • Find book ID      │
│ • Load chapter 3    │
│ • Extract verse 7   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Format & Return     │
│ "And it came to     │
│  pass that I..."    │
└─────────────────────┘
```

### 2. Exact Search

```
User Request: "Search for 'faith hope charity'"
      │
      ▼
┌─────────────────────┐
│ exact_search        │
│ tool called         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ ExactSearch         │
│ • Load all verses   │
│ • String match      │
│ • Extract context   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Format Results      │
│ • Reference         │
│ • Context snippet   │
│ • Full verse        │
└─────────────────────┘
```

### 3. Semantic Search

```
User Request: "Find verses about trusting God"
      │
      ▼
┌─────────────────────┐
│ semantic_search     │
│ tool called         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ SemanticSearch      │
│ • Generate query    │
│   embedding         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ ChromaDB            │
│ • Vector similarity │
│   search            │
│ • Retrieve top N    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Format Results      │
│ • Ranked by score   │
│ • With metadata     │
└─────────────────────┘
```

## Component Details

### ScriptureLoader

**Responsibilities:**
- Load scripture metadata (volumes, books)
- Load verse data from JSON files
- Provide lookup by book ID, name, or abbreviation
- Cache loaded data for performance

**Key Methods:**
- `load_volumes()`: Load metadata
- `load_scripture_verses(book_id, chapter)`: Load specific chapter
- `load_all_verses()`: Load entire scripture corpus
- `get_book_by_abbr(abbr)`: Lookup book

### ReferenceParser

**Responsibilities:**
- Parse natural language references
- Handle complex formats (ranges, multiple books)
- Validate references
- Generate pretty-printed strings

**Supported Formats:**
- Simple: `1 Ne 3:7`
- Verse range: `Alma 32:21-23`
- Chapter range: `Alma 1-2`
- Multiple books: `Alma 1-2;James 1:5-6`
- Complex: `Alma 1-2;4-5:10`

**Key Methods:**
- `parse(reference)`: Main parsing function
- `to_dict(parsed)`: Convert to JSON format

### ExactSearch

**Responsibilities:**
- Full-text search across all verses
- Context extraction around matches
- Case-sensitive and case-insensitive modes

**Features:**
- Fast string matching
- Configurable context window
- Result limiting
- Keyword highlighting

**Key Methods:**
- `search(query, case_sensitive, context_words)`: Search verses
- `_extract_context()`: Extract surrounding text

### SemanticSearch

**Responsibilities:**
- AI-powered semantic similarity search
- Vector database management
- One-time indexing of all verses

**Technology Stack:**
- **Model**: sentence-transformers/all-MiniLM-L6-v2
  - Size: 22M parameters
  - Fast inference
  - Good quality embeddings
- **Database**: ChromaDB
  - Persistent storage
  - Efficient similarity search
  - Metadata filtering

**Key Methods:**
- `initialize()`: Load model and connect to DB
- `index_scriptures(force_reindex)`: Build index
- `search(query, n_results)`: Semantic search

### MCP Server

**Responsibilities:**
- Implement MCP protocol
- Register and expose tools
- Handle async communication
- Error handling and formatting

**Communication:**
- stdio-based MCP protocol
- JSON-RPC message format
- Async/await pattern

## File Structure

```
src/scriptorian/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for -m
├── data_loader.py        # Scripture data loading
├── reference_parser.py   # Reference parsing
├── search.py             # Search engines
└── server.py             # MCP server implementation

polymer-citation-index/
└── model/
    ├── volumes.json      # Volume & book metadata
    └── scripture/        # Individual chapter files
        ├── 101.1.json    # Genesis 1
        ├── 205.3.json    # 1 Nephi 3
        └── ...           # ~1500 files

vector_db/                # Created on first index
└── chroma.sqlite3        # Vector database
```

## Performance Considerations

### Data Loading
- Lazy loading: Verses loaded on demand
- Caching: Volumes and books cached in memory
- File size: ~1500 small JSON files (efficient)

### Exact Search
- Linear scan through all verses
- Fast string matching (Python native)
- Typical query: <1 second for full corpus

### Semantic Search
- First-time indexing: 5-10 minutes
- Persistent storage: Subsequent searches instant
- Query time: <100ms for top 10 results
- Memory: ~500MB for loaded model

## Extension Points

### Adding New Search Modes
1. Create new class in `search.py`
2. Implement `search(query)` method
3. Register tool in `server.py`
4. Add tests

### Adding New Scripture Sources
1. Add data files to `polymer-citation-index/model/`
2. Update `volumes.json`
3. Ensure file naming: `{book_id}.{chapter}.json`
4. Run indexing for semantic search

### Custom Embedding Models
1. Modify `SemanticSearch.__init__(model_name=...)`
2. Supported: Any sentence-transformers model
3. Trade-offs: Speed vs quality

## Security & Privacy

- **No external API calls**: All processing local
- **No data collection**: Scripture data stays on device
- **No user tracking**: No analytics or telemetry
- **Open source**: Fully auditable code

## Dependencies

### Core (Required)
- `mcp`: MCP protocol implementation
- `numpy`: Numerical operations
- `sentence-transformers`: Embedding model
- `chromadb`: Vector database
- `torch`: PyTorch (for embeddings)

### Development (Optional)
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support

## Future Enhancements

Potential additions:
- Multi-language support
- Cross-reference lookup
- Study note integration
- Topic indexing
- Historical context
- Advanced filters (by speaker, date, etc.)
