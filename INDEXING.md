# Scripture Indexing Guide

This document explains how scripture indexing works in Scriptorian and how to manage the vector database.

## What is Indexing?

Indexing is the process of:
1. Loading all scripture verses (~6,000 verses)
2. Generating AI embeddings for each verse using a neural network
3. Storing embeddings in a vector database (ChromaDB)
4. Enabling semantic search by meaning, not just keywords

## Automatic Indexing During Installation

When you run `./install.sh`, you'll be prompted:

```
Would you like to index scriptures for semantic search now?
This will:
  - Download AI model (~80MB, one-time)
  - Generate embeddings for all verses (5-10 minutes)
  - Enable AI-powered semantic search

Index now? (Y/n):
```

### If You Choose Yes
- Indexing begins immediately after dependency installation
- Progress updates show verses processed: `Progress: 2,500/6,000 verses (41.7%)`
- Vector database saved to `vector_db/` directory
- Semantic search ready to use in Claude Desktop

### If You Choose No
- Installation completes without indexing
- You can index later using one of the methods below
- Exact search still works (no indexing required)

## Manual Indexing

### Method 1: Standalone Script (Recommended)

Run the dedicated indexing script:

```bash
cd /Users/hyrum/src/scriptorian
python scripts/index_scriptures.py
```

**Features:**
- Interactive prompts if database already exists
- Progress tracking with percentage complete
- Detailed statistics on completion
- Database size reporting

**Output Example:**
```
============================================================
Scriptorian - Scripture Indexing
============================================================

📂 Data path: /Users/hyrum/src/scriptorian/polymer-citation-index/model
📂 Vector DB path: /Users/hyrum/src/scriptorian/vector_db

Loading scripture metadata...
✓ Loaded 5 volumes, 89 books

Initializing AI model (this may download ~80MB on first run)...
✓ Model loaded successfully

============================================================
Indexing Scriptures (this will take 5-10 minutes)
============================================================

Loading all scripture verses...
✓ Loaded 6,000 verses

Generating embeddings and building vector database...
(This requires significant computation, please be patient)

  Progress: 6,000/6,000 verses (100.0%)

✓ Indexing complete!

📊 Vector database statistics:
   Total verses indexed: 6,000
   Database location: /Users/hyrum/src/scriptorian/vector_db
   Database size: 45.2 MB

============================================================
✅ Scripture indexing completed successfully!
============================================================
```

### Method 2: Via Claude Desktop

After setting up the MCP server in Claude Desktop:

```
Please index the scriptures for semantic search
```

Claude will use the `index_scriptures` tool to build the database.

### Method 3: Python API

For programmatic access:

```python
from pathlib import Path
from scriptorian.data_loader import ScriptureLoader
from scriptorian.search import SemanticSearch

# Setup paths
data_path = Path("polymer-citation-index/model")
vector_db_path = Path("vector_db")

# Initialize
loader = ScriptureLoader(data_path)
loader.load_volumes()

search = SemanticSearch(loader, db_path=str(vector_db_path))
search.initialize()

# Index (takes 5-10 minutes)
search.index_scriptures(force_reindex=False)
```

## Re-indexing

### When to Re-index

You might need to re-index if:
- Scripture data files are updated
- Database becomes corrupted
- You want to switch embedding models
- Testing or development purposes

### How to Re-index

**Option 1: Interactive Script**
```bash
python scripts/index_scriptures.py
# When prompted about existing database, choose 'y' to reindex
```

**Option 2: Force Reindex**
```python
search.index_scriptures(force_reindex=True)
```

**Option 3: Delete and Rebuild**
```bash
rm -rf vector_db/
python scripts/index_scriptures.py
```

## Database Details

### Storage Location
- **Path**: `vector_db/` in project root
- **Format**: ChromaDB (SQLite + parquet files)
- **Size**: ~45-50 MB when fully indexed

### What's Stored

For each verse, the database contains:
- **Embedding**: 384-dimensional vector (float32)
- **Text**: Full verse text
- **Metadata**:
  - `reference`: "1 Nephi 3:7"
  - `short_reference`: "1 Ne. 3:7"
  - `book_name`: "First Nephi"
  - `chapter`: "3"
  - `verse`: "7"
  - `volume`: "Book of Mormon"

### Files Created

```
vector_db/
├── chroma.sqlite3        # Metadata and index
├── [collection_id]/
│   ├── data_level0.bin   # Vector data
│   ├── header.bin        # Collection header
│   ├── link_lists.bin    # HNSW graph
│   └── length.bin        # Vector lengths
```

## Performance

### Indexing Time
- **CPU**: 5-10 minutes (varies by processor)
- **GPU**: 2-4 minutes (if CUDA available)
- **Batch size**: 100 verses at a time
- **Progress**: Real-time updates

### Search Time
- **First search**: ~100-200ms (model loading)
- **Subsequent searches**: <50ms
- **Embedding generation**: ~10ms per query
- **Vector similarity**: <20ms for top 10 results

### Resource Usage
- **Memory**: ~500 MB (model + vectors)
- **Disk**: ~50 MB (vector database)
- **Network**: ~80 MB (one-time model download)

## Embedding Model

### Current Model
- **Name**: `sentence-transformers/all-MiniLM-L6-v2`
- **Size**: 22 million parameters
- **Dimensions**: 384
- **Speed**: Very fast inference
- **Quality**: Good for scripture similarity

### Why This Model?

1. **Lightweight**: Small enough to run on any machine
2. **Fast**: Quick embedding generation
3. **Quality**: Good semantic understanding
4. **Efficient**: Low memory footprint
5. **Open Source**: Free and available

### Alternative Models

You can use different models by modifying `search.py`:

```python
# For higher quality (slower)
semantic_search = SemanticSearch(
    loader,
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# For multilingual support
semantic_search = SemanticSearch(
    loader,
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

**Trade-offs:**
- Larger models: Better quality, slower, more memory
- Smaller models: Faster, less memory, lower quality

## Troubleshooting

### "Out of memory" Error

**Solution 1**: Reduce batch size in `scripts/index_scriptures.py`:
```python
batch_size = 50  # Reduce from 100
```

**Solution 2**: Close other applications

**Solution 3**: Use smaller embedding model

### "Model download failed"

**Causes:**
- Network connectivity issues
- Hugging Face Hub unreachable
- Disk space insufficient

**Solutions:**
1. Check internet connection
2. Check disk space: `df -h`
3. Manually download model: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`

### "Database locked" Error

**Cause**: Another process is using the database

**Solutions:**
1. Close Claude Desktop
2. Stop any running MCP servers
3. Wait a few seconds and retry

### Indexing Very Slow

**Normal times:**
- Old laptop: 10-15 minutes
- Modern laptop: 5-8 minutes
- Desktop with GPU: 2-4 minutes

**If slower:**
1. Check CPU usage (should be high during indexing)
2. Close resource-intensive applications
3. Ensure SSD (not HDD) for vector_db/

## Verifying Index

### Check if indexed:
```bash
ls -lh vector_db/
# Should show ~45-50 MB of files
```

### Count indexed verses:
```python
from scriptorian.search import SemanticSearch
from scriptorian.data_loader import ScriptureLoader
from pathlib import Path

loader = ScriptureLoader(Path("polymer-citation-index/model"))
loader.load_volumes()

search = SemanticSearch(loader, db_path="vector_db")
search.initialize()

print(f"Indexed verses: {search.collection.count()}")
# Should print: Indexed verses: 6000 (approximately)
```

### Test search:
```python
results = search.search("faith in Jesus Christ", n_results=5)
for r in results:
    print(f"{r.reference}: {r.score:.3f}")
```

## Best Practices

1. **Index once**: The database persists, no need to reindex unless data changes
2. **Backup**: Copy `vector_db/` to backup before major changes
3. **Version control**: Add `vector_db/` to `.gitignore` (already done)
4. **Testing**: Use separate database path for test environments
5. **Production**: Pre-index before deploying to avoid first-run delay

## Advanced Usage

### Custom Database Location

```python
search = SemanticSearch(
    loader,
    db_path="/custom/path/to/vector_db"
)
```

### Metadata Filtering

```python
# Search only in Book of Mormon
results = search.collection.query(
    query_embeddings=[embedding],
    where={"volume": "Book of Mormon"},
    n_results=10
)
```

### Hybrid Search

Combine exact and semantic search:

```python
# Exact matches first
exact_results = exact_search.search("faith")

# Semantic for broader meaning
semantic_results = semantic_search.search("having faith")

# Merge and deduplicate
combined = merge_results(exact_results, semantic_results)
```

## Future Enhancements

Potential improvements:
- Incremental indexing (add verses without full rebuild)
- Multiple language embeddings
- Fine-tuned model on scripture text
- GPU acceleration for faster indexing
- Compressed embeddings (lower disk usage)
- Cross-reference embeddings
