"""Load and index scripture data from JSON files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Verse:
    """Represents a single verse."""
    book_id: str
    book_name: str
    book_abbr: str
    chapter: int
    verse: int
    text: str
    volume: str

    @property
    def reference(self) -> str:
        """Return formatted reference."""
        return f"{self.book_name} {self.chapter}:{self.verse}"

    @property
    def short_reference(self) -> str:
        """Return abbreviated reference."""
        return f"{self.book_abbr} {self.chapter}:{self.verse}"


@dataclass
class Book:
    """Represents a book of scripture."""
    id: int
    abbr: str
    cite_abbr: str
    full_name: str
    num_chapters: int
    parent_book_id: int


@dataclass
class Volume:
    """Represents a volume of scripture."""
    id: int
    abbr: str
    full_name: str
    books: List[Book]


class ScriptureLoader:
    """Loads scripture data from JSON files."""

    def __init__(self, data_path: Path):
        """Initialize loader with path to data directory."""
        self.data_path = data_path
        self.volumes: Dict[str, Volume] = {}
        self.books: Dict[str, Book] = {}
        self.verses: List[Verse] = []

    def load_volumes(self) -> None:
        """Load volume and book metadata."""
        volumes_file = self.data_path / "volumes.json"
        with open(volumes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for vol_data in data:
            books = []
            for book_data in vol_data.get('books', []):
                book = Book(
                    id=book_data['id'],
                    abbr=book_data['abbr'],
                    cite_abbr=book_data['citeAbbr'],
                    full_name=book_data['fullName'],
                    num_chapters=book_data['numChapters'],
                    parent_book_id=vol_data['id']
                )
                books.append(book)
                self.books[book.abbr] = book
                self.books[str(book.id)] = book

            volume = Volume(
                id=vol_data['id'],
                abbr=vol_data['abbr'],
                full_name=vol_data['fullName'],
                books=books
            )
            self.volumes[volume.abbr] = volume
            self.volumes[str(volume.id)] = volume

    def load_scripture_verses(self, book_id: int, chapter: int) -> List[Verse]:
        """Load verses for a specific book and chapter."""
        scripture_file = self.data_path / "scripture" / f"{book_id}.{chapter}.json"

        if not scripture_file.exists():
            return []

        with open(scripture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        book = self.books.get(str(book_id))
        if not book:
            return []

        volume = self.volumes.get(str(book.parent_book_id))
        volume_name = volume.full_name if volume else "Unknown"

        verses = []
        for verse_data in data:
            verse = Verse(
                book_id=str(book_id),
                book_name=book.full_name,
                book_abbr=book.cite_abbr,
                chapter=chapter,
                verse=int(verse_data['Verse']),
                text=verse_data['Text'],
                volume=volume_name
            )
            verses.append(verse)

        return verses

    def load_all_verses(self) -> List[Verse]:
        """Load all verses from all books."""
        if self.verses:
            return self.verses

        scripture_dir = self.data_path / "scripture"
        if not scripture_dir.exists():
            return []

        all_verses = []
        for scripture_file in sorted(scripture_dir.glob("*.json")):
            # Parse filename: bookId.chapter.json
            parts = scripture_file.stem.split('.')
            if len(parts) != 2:
                continue

            try:
                book_id = int(parts[0])
                chapter = int(parts[1])
                verses = self.load_scripture_verses(book_id, chapter)
                all_verses.extend(verses)
            except (ValueError, KeyError):
                continue

        self.verses = all_verses
        return all_verses

    def get_book_by_abbr(self, abbr: str) -> Optional[Book]:
        """Get book by abbreviation (case-insensitive)."""
        abbr_lower = abbr.lower()
        for key, book in self.books.items():
            if book.abbr.lower() == abbr_lower or book.cite_abbr.lower() == abbr_lower:
                return book
        return None

    def get_book_by_name(self, name: str) -> Optional[Book]:
        """Get book by full or partial name (case-insensitive)."""
        name_lower = name.lower()
        for book in self.books.values():
            if isinstance(book, Book):
                if name_lower in book.full_name.lower():
                    return book
        return None
