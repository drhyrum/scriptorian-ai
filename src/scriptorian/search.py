"""Search functionality for scriptures."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from .data_loader import ScriptureLoader, Verse


@dataclass
class SearchResult:
    """Represents a search result."""
    reference: str
    short_reference: str
    verse_text: str
    context: str  # Phrase with search term highlighted
    book_name: str
    chapter: int
    verse: int
    volume: str
    score: Optional[float] = None


class ExactSearch:
    """Exact string search across scriptures."""

    def __init__(self, loader: ScriptureLoader):
        """Initialize with scripture loader."""
        self.loader = loader

    def search(
        self,
        query: str,
        case_sensitive: bool = False,
        context_words: int = 5
    ) -> List[SearchResult]:
        """
        Search for exact string matches across all scriptures.

        Args:
            query: Search string
            case_sensitive: Whether search is case-sensitive
            context_words: Number of words to include before/after match

        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            return []

        results = []
        verses = self.loader.load_all_verses()

        search_pattern = query if case_sensitive else query.lower()

        for verse in verses:
            verse_text = verse.text if case_sensitive else verse.text.lower()

            if search_pattern in verse_text:
                # Extract context around the match
                context = self._extract_context(
                    verse.text,
                    query,
                    context_words,
                    case_sensitive
                )

                result = SearchResult(
                    reference=verse.reference,
                    short_reference=verse.short_reference,
                    verse_text=verse.text,
                    context=context,
                    book_name=verse.book_name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    volume=verse.volume
                )
                results.append(result)

        return results

    def _extract_context(
        self,
        text: str,
        query: str,
        context_words: int,
        case_sensitive: bool
    ) -> str:
        """Extract context around the match with highlighting."""
        # Find the position of the match
        search_text = text if case_sensitive else text.lower()
        search_query = query if case_sensitive else query.lower()

        pos = search_text.find(search_query)
        if pos == -1:
            return text[:100] + "..." if len(text) > 100 else text

        # Split into words
        words = text.split()

        # Find which word contains the match
        char_count = 0
        match_word_idx = 0

        for idx, word in enumerate(words):
            if char_count <= pos < char_count + len(word):
                match_word_idx = idx
                break
            char_count += len(word) + 1  # +1 for space

        # Extract context
        start_idx = max(0, match_word_idx - context_words)
        end_idx = min(len(words), match_word_idx + context_words + 1)

        context_words_list = words[start_idx:end_idx]

        # Add ellipsis if truncated
        if start_idx > 0:
            context_words_list.insert(0, "...")
        if end_idx < len(words):
            context_words_list.append("...")

        context = ' '.join(context_words_list)

        # Highlight the match (wrap in **bold** markers)
        if not case_sensitive:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            context = pattern.sub(f"**{query}**", context, count=1)
        else:
            context = context.replace(query, f"**{query}**", 1)

        return context


class SemanticSearch:
    """Semantic search using embeddings and vector database."""

    def __init__(
        self,
        loader: ScriptureLoader,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        db_path: Optional[str] = None
    ):
        """
        Initialize semantic search.

        Args:
            loader: Scripture loader
            model_name: Name of the embedding model
            db_path: Path to vector database (ChromaDB)
        """
        self.loader = loader
        self.model_name = model_name
        self.db_path = db_path
        self.embedder = None
        self.collection = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the embedding model and vector database."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
        except ImportError as e:
            raise ImportError(
                "Semantic search requires sentence-transformers and chromadb. "
                "Install with: uv pip install sentence-transformers chromadb"
            ) from e

        # Initialize embedding model
        self.embedder = SentenceTransformer(self.model_name)

        # Initialize ChromaDB
        if self.db_path:
            client = chromadb.PersistentClient(path=self.db_path)
        else:
            client = chromadb.Client()

        # Get or create collection
        self.collection = client.get_or_create_collection(
            name="scriptures",
            metadata={"description": "Scripture verses with embeddings"}
        )

        self._initialized = True

    def index_scriptures(self, force_reindex: bool = False) -> None:
        """Index all scriptures into the vector database."""
        if not self._initialized:
            self.initialize()

        # Check if already indexed
        if not force_reindex and self.collection.count() > 0:
            print(f"Collection already contains {self.collection.count()} verses")
            return

        verses = self.loader.load_all_verses()
        print(f"Indexing {len(verses)} verses...")

        batch_size = 100
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i + batch_size]

            texts = [v.text for v in batch]
            embeddings = self.embedder.encode(texts, show_progress_bar=True)

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
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

        print(f"Indexing complete. Total verses: {self.collection.count()}")

    def search(
        self,
        query: str,
        n_results: int = 10,
        context_words: int = 5
    ) -> List[SearchResult]:
        """
        Perform semantic search.

        Args:
            query: Search query
            n_results: Number of results to return
            context_words: Number of words for context

        Returns:
            List of SearchResult objects
        """
        if not self._initialized:
            self.initialize()

        if not query or not query.strip():
            return []

        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]

        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )

        # Convert to SearchResult objects
        search_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i] if 'distances' in results else None

            # Calculate similarity score (1 - distance for cosine)
            score = 1 - distance if distance is not None else None

            # Create context (for semantic search, we can show the full verse)
            context = document[:150] + "..." if len(document) > 150 else document

            result = SearchResult(
                reference=metadata['reference'],
                short_reference=metadata['short_reference'],
                verse_text=document,
                context=context,
                book_name=metadata['book_name'],
                chapter=int(metadata['chapter']),
                verse=int(metadata['verse']),
                volume=metadata['volume'],
                score=score
            )
            search_results.append(result)

        return search_results


def format_search_results(results: List[SearchResult]) -> List[Dict[str, Any]]:
    """Format search results as JSON-serializable dictionaries."""
    return [
        {
            "reference": r.reference,
            "shortReference": r.short_reference,
            "verseText": r.verse_text,
            "context": r.context,
            "bookName": r.book_name,
            "chapter": r.chapter,
            "verse": r.verse,
            "volume": r.volume,
            "score": r.score
        }
        for r in results
    ]
