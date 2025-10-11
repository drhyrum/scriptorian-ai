#!/usr/bin/env python
"""Standalone script to index scriptures for semantic search."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from scriptorian.data_loader import ScriptureLoader
from scriptorian.search import SemanticSearch


def main():
    """Index all scriptures into vector database."""
    print("=" * 60)
    print("Scriptorian - Scripture Indexing")
    print("=" * 60)
    print()

    # Setup paths
    data_path = project_root / "polymer-citation-index" / "model"
    vector_db_path = project_root / "vector_db"

    if not data_path.exists():
        print(f"ERROR: Scripture data not found at: {data_path}")
        print("Please ensure polymer-citation-index/ directory exists.")
        sys.exit(1)

    # Create vector_db directory
    vector_db_path.mkdir(exist_ok=True)

    print(f"📂 Data path: {data_path}")
    print(f"📂 Vector DB path: {vector_db_path}")
    print()

    # Initialize loader
    print("Loading scripture metadata...")
    loader = ScriptureLoader(data_path)
    loader.load_volumes()
    print(f"✓ Loaded {len(loader.volumes)} volumes, {len(loader.books)} books")
    print()

    # Initialize semantic search
    print("Initializing AI model (this may download ~80MB on first run)...")
    semantic_search = SemanticSearch(
        loader,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        db_path=str(vector_db_path)
    )

    try:
        semantic_search.initialize()
        print("✓ Model loaded successfully")
        print()
    except Exception as e:
        print(f"ERROR initializing model: {e}")
        sys.exit(1)

    # Check if already indexed
    count = semantic_search.collection.count()
    if count > 0:
        print(f"⚠️  Vector database already contains {count} verses")
        response = input("Do you want to reindex? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Skipping indexing.")
            sys.exit(0)
        force_reindex = True
    else:
        force_reindex = False

    # Index scriptures
    print()
    print("=" * 60)
    print("Indexing Scriptures (this will take 5-10 minutes)")
    print("=" * 60)
    print()

    try:
        # Load all verses
        print("Loading all scripture verses...")
        verses = loader.load_all_verses()
        total_verses = len(verses)
        print(f"✓ Loaded {total_verses:,} verses")
        print()

        # Index in batches
        print("Generating embeddings and building vector database...")
        print("(This requires significant computation, please be patient)")
        print()

        batch_size = 100
        for i in range(0, total_verses, batch_size):
            batch = verses[i:i + batch_size]

            # Progress indicator
            progress = (i + len(batch)) / total_verses * 100
            print(f"  Progress: {i + len(batch):,}/{total_verses:,} verses ({progress:.1f}%)", end='\r')

            # Generate embeddings for batch
            texts = [v.text for v in batch]
            embeddings = semantic_search.embedder.encode(texts, show_progress_bar=False)

            # Prepare metadata
            metadatas = [
                {
                    "reference": v.reference,
                    "short_reference": v.short_reference,
                    "book_name": v.book_name,
                    "chapter": str(v.chapter),
                    "verse": str(v.verse),
                    "volume": v.volume
                }
                for v in batch
            ]

            # Generate IDs
            ids = [f"{v.book_id}_{v.chapter}_{v.verse}" for v in batch]

            # Add to collection
            if force_reindex and i == 0:
                # Delete existing and add new
                try:
                    semantic_search.collection.delete(ids=ids)
                except:
                    pass

            semantic_search.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

        print()  # New line after progress
        print()
        print("✓ Indexing complete!")
        print()

        # Verify
        final_count = semantic_search.collection.count()
        print(f"📊 Vector database statistics:")
        print(f"   Total verses indexed: {final_count:,}")
        print(f"   Database location: {vector_db_path}")
        print(f"   Database size: {sum(f.stat().st_size for f in vector_db_path.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
        print()

        print("=" * 60)
        print("✅ Scripture indexing completed successfully!")
        print("=" * 60)
        print()
        print("You can now use semantic search in Claude Desktop.")
        print("The vector database is persisted and doesn't need to be rebuilt.")
        print()

    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Indexing interrupted by user")
        print("You can run this script again to continue indexing.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"ERROR during indexing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
