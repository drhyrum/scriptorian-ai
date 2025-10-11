"""Parse plain text scripture references into structured format."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class VerseSegment:
    """Represents a range of verses."""
    start: int
    end: int


@dataclass
class ChapterSegment:
    """Represents a chapter with optional verse ranges."""
    start: int
    end: int
    verses: List[VerseSegment]


@dataclass
class BookReference:
    """Represents a book with chapter and verse ranges."""
    book: str
    chapters: List[ChapterSegment]


@dataclass
class ParsedReference:
    """Result of parsing a reference string."""
    references: List[BookReference]
    pretty_string: str
    valid: bool
    error: Optional[str] = None


class ReferenceParser:
    """Parse plain text scripture references."""

    # Common book abbreviations (case-insensitive)
    BOOK_ABBR = {
        # Old Testament
        'gen': 'genesis', 'ex': 'exodus', 'lev': 'leviticus', 'num': 'numbers',
        'deut': 'deuteronomy', 'josh': 'joshua', 'judg': 'judges', 'ruth': 'ruth',
        '1sam': '1_sam', '2sam': '2_sam', '1kgs': '1_kgs', '2kgs': '2_kgs',
        '1chr': '1_chr', '2chr': '2_chr', 'ezra': 'ezra', 'neh': 'nehemiah',
        'esth': 'esther', 'job': 'job', 'ps': 'psalms', 'prov': 'proverbs',
        'eccl': 'ecclesiastes', 'song': 'song', 'isa': 'isaiah', 'jer': 'jeremiah',
        'lam': 'lamentations', 'ezek': 'ezekiel', 'dan': 'daniel', 'hosea': 'hosea',
        'joel': 'joel', 'amos': 'amos', 'obad': 'obadiah', 'jonah': 'jonah',
        'micah': 'micah', 'nahum': 'nahum', 'hab': 'habakkuk', 'zeph': 'zephaniah',
        'hag': 'haggai', 'zech': 'zechariah', 'mal': 'malachi',

        # New Testament
        'matt': 'matthew', 'mark': 'mark', 'luke': 'luke', 'john': 'john',
        'acts': 'acts', 'rom': 'romans', '1cor': '1_cor', '2cor': '2_cor',
        'gal': 'galatians', 'eph': 'ephesians', 'philip': 'philippians',
        'col': 'colossians', '1thes': '1_thes', '2thes': '2_thes',
        '1tim': '1_tim', '2tim': '2_tim', 'titus': 'titus', 'philem': 'philemon',
        'heb': 'hebrews', 'james': 'james', 'jas': 'james',
        '1pet': '1_pet', '2pet': '2_pet', '1jn': '1_jn', '2jn': '2_jn',
        '3jn': '3_jn', 'jude': 'jude', 'rev': 'revelation',

        # Book of Mormon
        '1ne': '1_ne', '1nephi': '1_ne', '2ne': '2_ne', '2nephi': '2_ne',
        'jacob': 'jacob', 'enos': 'enos', 'jarom': 'jarom', 'omni': 'omni',
        'wofm': 'w_of_m', 'mosiah': 'mosiah', 'alma': 'alma', 'hel': 'helaman',
        'helaman': 'helaman', '3ne': '3_ne', '3nephi': '3_ne', '4ne': '4_ne',
        '4nephi': '4_ne', 'morm': 'mormon', 'mormon': 'morm', 'ether': 'ether',
        'moro': 'moroni', 'moroni': 'moro',

        # D&C and PGP
        'dc': 'sec', 'd&c': 'sec', 'od': 'od', 'moses': 'moses',
        'abr': 'abraham', 'abraham': 'abr', 'jsm': 'js_m', 'jsh': 'js_h',
        'aoff': 'a_of_f', 'aof': 'a_of_f',
    }

    @classmethod
    def parse(cls, reference: str) -> ParsedReference:
        """
        Parse a scripture reference string.

        Examples:
            "1 Ne 3:7" -> 1 Nephi chapter 3, verse 7
            "Alma 1-2" -> Alma chapters 1-2
            "Alma 4-5:10" -> Alma chapters 4-5, verse 10 of chapter 5
            "Alma 1-2;4-5:10;jas 1:5-6" -> Multiple books and ranges
        """
        if not reference or not reference.strip():
            return ParsedReference(
                references=[],
                pretty_string="",
                valid=False,
                error="Empty reference string"
            )

        try:
            # Split by semicolon for multiple book references
            book_refs = reference.split(';')
            parsed_books = []

            for book_ref in book_refs:
                book_ref = book_ref.strip()
                if not book_ref:
                    continue

                parsed_book = cls._parse_book_reference(book_ref)
                if parsed_book:
                    parsed_books.append(parsed_book)

            if not parsed_books:
                return ParsedReference(
                    references=[],
                    pretty_string="",
                    valid=False,
                    error="No valid references found"
                )

            pretty = cls._format_pretty_string(parsed_books)

            return ParsedReference(
                references=parsed_books,
                pretty_string=pretty,
                valid=True
            )

        except Exception as e:
            return ParsedReference(
                references=[],
                pretty_string="",
                valid=False,
                error=f"Parse error: {str(e)}"
            )

    @classmethod
    def _parse_book_reference(cls, ref: str) -> Optional[BookReference]:
        """Parse a single book reference."""
        # Match book name at start
        match = re.match(r'^([a-zA-Z0-9\s&]+?)\s*(\d+.*)', ref)
        if not match:
            return None

        book_name = match.group(1).strip()
        rest = match.group(2).strip()

        # Normalize book name
        book_abbr = cls._normalize_book_name(book_name)
        if not book_abbr:
            return None

        # Parse chapter:verse ranges
        chapters = cls._parse_chapter_ranges(rest)

        return BookReference(book=book_abbr, chapters=chapters)

    @classmethod
    def _normalize_book_name(cls, name: str) -> Optional[str]:
        """Normalize book name to standard abbreviation."""
        # Remove spaces and make lowercase
        normalized = name.lower().replace(' ', '').replace('.', '')
        return cls.BOOK_ABBR.get(normalized, normalized)

    @classmethod
    def _parse_chapter_ranges(cls, text: str) -> List[ChapterSegment]:
        """Parse chapter and verse ranges."""
        chapters = []

        # Split by comma for multiple chapter segments
        segments = re.split(r'[,;]', text)

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            # Check if there are verses specified (contains colon)
            if ':' in segment:
                chapter_part, verse_part = segment.split(':', 1)

                # Parse chapter range
                chapter_range = cls._parse_range(chapter_part.strip())
                if not chapter_range:
                    continue

                # Parse verse ranges
                verse_ranges = []
                for verse_seg in verse_part.split(','):
                    verse_range = cls._parse_range(verse_seg.strip())
                    if verse_range:
                        verse_ranges.append(VerseSegment(
                            start=verse_range[0],
                            end=verse_range[1]
                        ))

                chapters.append(ChapterSegment(
                    start=chapter_range[0],
                    end=chapter_range[1],
                    verses=verse_ranges
                ))
            else:
                # No verses, just chapter range
                chapter_range = cls._parse_range(segment)
                if chapter_range:
                    chapters.append(ChapterSegment(
                        start=chapter_range[0],
                        end=chapter_range[1],
                        verses=[]
                    ))

        return chapters

    @staticmethod
    def _parse_range(text: str) -> Optional[tuple[int, int]]:
        """Parse a numeric range like '1-5' or single number '3'."""
        text = text.strip()
        if '-' in text:
            parts = text.split('-', 1)
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                return (start, end)
            except ValueError:
                return None
        else:
            try:
                num = int(text)
                return (num, num)
            except ValueError:
                return None

    @classmethod
    def _format_pretty_string(cls, refs: List[BookReference]) -> str:
        """Format references into a pretty string."""
        book_strs = []

        for ref in refs:
            chapter_strs = []
            for chapter in ref.chapters:
                if chapter.start == chapter.end:
                    ch_str = str(chapter.start)
                else:
                    ch_str = f"{chapter.start}-{chapter.end}"

                if chapter.verses:
                    verse_strs = []
                    for verse in chapter.verses:
                        if verse.start == verse.end:
                            verse_strs.append(str(verse.start))
                        else:
                            verse_strs.append(f"{verse.start}-{verse.end}")
                    ch_str += ':' + ','.join(verse_strs)

                chapter_strs.append(ch_str)

            book_name = ref.book.replace('_', ' ').title()
            book_strs.append(f"{book_name} {'; '.join(chapter_strs)}")

        return '; '.join(book_strs)

    def to_dict(self, parsed: ParsedReference) -> Dict[str, Any]:
        """Convert ParsedReference to dictionary format matching API spec."""
        result = {
            "references": [],
            "prettyString": parsed.pretty_string,
            "valid": parsed.valid
        }

        if parsed.error:
            result["error"] = parsed.error

        for ref in parsed.references:
            book_dict = {
                "book": ref.book,
                "chapters": []
            }

            for chapter in ref.chapters:
                chapter_dict = {
                    "start": chapter.start,
                    "end": chapter.end,
                    "verses": []
                }

                for verse in chapter.verses:
                    chapter_dict["verses"].append({
                        "start": verse.start,
                        "end": verse.end
                    })

                book_dict["chapters"].append(chapter_dict)

            result["references"].append(book_dict)

        return result
