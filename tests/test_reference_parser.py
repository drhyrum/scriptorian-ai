"""Tests for reference parser."""

import pytest
from scriptorian.reference_parser import ReferenceParser


def test_simple_reference():
    """Test parsing a simple reference."""
    result = ReferenceParser.parse("1 Ne 3:7")

    assert result.valid
    assert len(result.references) == 1
    assert result.references[0].book == "1_ne"
    assert len(result.references[0].chapters) == 1
    assert result.references[0].chapters[0].start == 3
    assert result.references[0].chapters[0].end == 3
    assert len(result.references[0].chapters[0].verses) == 1
    assert result.references[0].chapters[0].verses[0].start == 7
    assert result.references[0].chapters[0].verses[0].end == 7


def test_verse_range():
    """Test parsing a verse range."""
    result = ReferenceParser.parse("Alma 32:21-23")

    assert result.valid
    assert result.references[0].book == "alma"
    assert result.references[0].chapters[0].verses[0].start == 21
    assert result.references[0].chapters[0].verses[0].end == 23


def test_chapter_range():
    """Test parsing a chapter range."""
    result = ReferenceParser.parse("Alma 1-2")

    assert result.valid
    assert result.references[0].book == "alma"
    assert result.references[0].chapters[0].start == 1
    assert result.references[0].chapters[0].end == 2
    assert len(result.references[0].chapters[0].verses) == 0


def test_multiple_books():
    """Test parsing multiple books."""
    result = ReferenceParser.parse("Alma 1-2;James 1:5-6")

    assert result.valid
    assert len(result.references) == 2
    assert result.references[0].book == "alma"
    assert result.references[1].book == "james"


def test_complex_reference():
    """Test parsing a complex reference."""
    result = ReferenceParser.parse("Alma 1-2;4-5:10")

    assert result.valid
    assert len(result.references) == 1
    assert len(result.references[0].chapters) == 2
    assert result.references[0].chapters[0].start == 1
    assert result.references[0].chapters[0].end == 2
    assert result.references[0].chapters[1].start == 4
    assert result.references[0].chapters[1].end == 5
    assert result.references[0].chapters[1].verses[0].start == 10


def test_invalid_reference():
    """Test parsing an invalid reference."""
    result = ReferenceParser.parse("")

    assert not result.valid
    assert result.error is not None


def test_pretty_string():
    """Test pretty string formatting."""
    result = ReferenceParser.parse("1ne3:7")

    assert result.valid
    assert "Nephi" in result.pretty_string or "Ne" in result.pretty_string
    assert "3:7" in result.pretty_string


def test_dc_reference():
    """Test D&C reference."""
    result = ReferenceParser.parse("D&C 121:1-6")

    assert result.valid
    assert result.references[0].book == "sec"
    assert result.references[0].chapters[0].start == 121
    assert result.references[0].chapters[0].verses[0].start == 1
    assert result.references[0].chapters[0].verses[0].end == 6
