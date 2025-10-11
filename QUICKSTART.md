# Scriptorian Quick Start Guide

This guide will help you get Scriptorian up and running quickly.

## Installation

### Automated Installation (Recommended)

Run the installation script which will:
- Install Python dependencies
- Test the installation
- Optionally index scriptures for semantic search (takes 5-10 minutes)

```bash
cd /Users/hyrum/src/scriptorian
./install.sh
```

When prompted, choose **Yes** to index scriptures now, or **No** to skip and index later.

### Manual Installation

If you prefer manual control:

```bash
cd /Users/hyrum/src/scriptorian
uv pip install -e .

# Optional: Index scriptures for semantic search
python scripts/index_scriptures.py
```

## Running the Server Standalone

Test the server directly:

```bash
python -m scriptorian.server
```

The server will run in stdio mode, ready to accept MCP protocol messages.

## Configure with Claude Desktop

1. Open your Claude Desktop MCP configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Scriptorian server configuration:

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

3. Restart Claude Desktop

4. Verify the server is loaded by checking the MCP tools menu

## First Steps

### 1. Fetch a Scripture

Try fetching a well-known verse:

```
Can you show me 1 Nephi 3:7?
```

Claude will use the `fetch_scripture` tool to retrieve the verse.

### 2. Search for Text

Try an exact search:

```
Search for all verses containing "faith hope charity"
```

### 3. Semantic Search (Ready if you indexed during install)

If you indexed during installation, semantic search is already ready! Try it:

```
Find verses about trusting God during difficult times
```

**If you skipped indexing**, you can index now:
- Run: `python scripts/index_scriptures.py`
- Or use Claude: "Please index the scriptures for semantic search"

The index is saved to disk permanently, so this only needs to be done once.

### 4. Semantic Search

Once indexed, try semantic search:

```
Find verses about trusting God during difficult times
```

## Tool Reference

### fetch_scripture
Fetch verses from a natural language reference.

Example queries:
- "Show me 1 Nephi 3:7"
- "What does Alma 32:21 say?"
- "Look up D&C 121:1-6"

### parse_reference
Parse a reference into structured JSON.

Example:
- "Parse the reference 'Alma 1-2;4-5:10'"

### exact_search
Search for exact text matches.

Example queries:
- "Search for 'faith hope charity'"
- "Find all verses with 'if ye are prepared'"

### semantic_search
Find verses by meaning, not just keywords.

Example queries:
- "Find verses about trusting God during trials"
- "What scriptures discuss the importance of prayer?"
- "Show me verses about forgiveness"

### index_scriptures
Index all scriptures (required once before semantic search).

## Troubleshooting

### "Module not found" error

Make sure PYTHONPATH is set correctly in your MCP configuration:

```json
"env": {
  "PYTHONPATH": "/Users/hyrum/src/scriptorian/src"
}
```

### Semantic search not working

1. Verify indexing completed: Run `index_scriptures` tool
2. Check vector_db folder exists: `ls vector_db/`
3. Check dependencies: `uv pip list | grep -E 'sentence-transformers|chromadb'`

### Slow semantic search on first use

The first time you run semantic search, the embedding model needs to be downloaded. This is normal and only happens once.

## Advanced Usage

### Re-indexing Scriptures

If you need to rebuild the semantic search index:

```
Please reindex the scriptures with force_reindex set to true
```

### Custom Search Parameters

You can specify advanced parameters:

```
Search for "faith" with case_sensitive true and max_results 100
```

```
Semantic search for "prayer" with n_results 20
```

## Data Location

- Scripture data: `polymer-citation-index/model/`
- Vector database: `vector_db/`
- Source code: `src/scriptorian/`

## Getting Help

For issues or questions:
1. Check the main README.md
2. Review the test files in `tests/` for usage examples
3. Open an issue on GitHub

## Next Steps

- Explore different search queries
- Combine multiple tools in a single request
- Use semantic search to discover scriptural themes
- Parse complex scripture references
