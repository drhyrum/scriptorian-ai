"""MCP server for scripture study."""

import json
import difflib
from pathlib import Path
from typing import Any, List, Dict, Tuple

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .data_loader import ScriptureLoader, Verse
from .reference_parser import ReferenceParser, ParsedReference
from .search import ExactSearch, SemanticSearch, format_search_results


class ScripturianServer:
    """MCP Server for scripture study tools."""

    def __init__(self, data_path: Path, vector_db_path: Path):
        """Initialize the server."""
        self.app = Server("scriptorian")
        self.data_path = data_path
        self.vector_db_path = vector_db_path

        # Initialize components
        self.loader = ScriptureLoader(data_path)
        self.loader.load_volumes()

        self.parser = ReferenceParser()
        self.exact_search = ExactSearch(self.loader)
        self.semantic_search = SemanticSearch(
            self.loader,
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            db_path=str(vector_db_path)
        )

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""

        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="fetch_scripture",
                    description=(
                        "Fetch scripture verses from a natural language reference. "
                        "Supports formats like '1 Ne 3:7', 'Alma 32:21-23', "
                        "'John 3:16', 'D&C 121:1-6', etc. Returns the full text "
                        "of the requested verses in standard format."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference": {
                                "type": "string",
                                "description": (
                                    "Scripture reference in natural language "
                                    "(e.g., '1 Ne 3:7-8', 'Alma 32', 'John 3:16')"
                                )
                            }
                        },
                        "required": ["reference"]
                    }
                ),
                Tool(
                    name="parse_reference",
                    description=(
                        "Parse a plain text scripture reference into structured format. "
                        "Returns JSON with book, chapter, and verse information."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference": {
                                "type": "string",
                                "description": "Plain text reference to parse"
                            }
                        },
                        "required": ["reference"]
                    }
                ),
                Tool(
                    name="exact_search",
                    description=(
                        "Search for an exact string across all scriptures. "
                        "Returns matching verses with context highlighting the match."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Text to search for"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Whether search is case-sensitive",
                                "default": False
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 50
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="semantic_search",
                    description=(
                        "Perform semantic search across scriptures using AI embeddings. "
                        "Finds verses similar in meaning to the query, not just exact matches. "
                        "Note: First use requires indexing which may take a few minutes."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (phrase or question)"
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="index_scriptures",
                    description=(
                        "Index all scriptures for semantic search. "
                        "This needs to be run once before using semantic_search. "
                        "May take several minutes."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "force_reindex": {
                                "type": "boolean",
                                "description": "Force reindexing even if already indexed",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="compare_scripture",
                    description=(
                        "Compare two scripture passages and show their differences. "
                        "Useful for comparing parallel passages (e.g., Matthew 5 vs 3 Nephi 12), "
                        "similar texts (e.g., sacramental prayers), or different versions. "
                        "Returns a unified diff showing additions, deletions, and changes."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference1": {
                                "type": "string",
                                "description": "First scripture reference (e.g., 'Moroni 4:3', 'Matthew 5')"
                            },
                            "reference2": {
                                "type": "string",
                                "description": "Second scripture reference (e.g., 'D&C 20:77', '3 Nephi 12')"
                            },
                            "context_lines": {
                                "type": "integer",
                                "description": "Number of context lines to show around differences",
                                "default": 3
                            }
                        },
                        "required": ["reference1", "reference2"]
                    }
                )
            ]

        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "fetch_scripture":
                    return await self._fetch_scripture(arguments)
                elif name == "parse_reference":
                    return await self._parse_reference(arguments)
                elif name == "exact_search":
                    return await self._exact_search(arguments)
                elif name == "semantic_search":
                    return await self._semantic_search(arguments)
                elif name == "index_scriptures":
                    return await self._index_scriptures(arguments)
                elif name == "compare_scripture":
                    return await self._compare_scripture(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _fetch_scripture(self, args: Dict[str, Any]) -> List[TextContent]:
        """Fetch scripture verses from a reference."""
        reference = args.get("reference", "")

        # Parse the reference
        parsed = self.parser.parse(reference)
        if not parsed.valid:
            return [TextContent(
                type="text",
                text=f"Invalid reference: {parsed.error}"
            )]

        # Fetch verses
        all_verses = []
        for book_ref in parsed.references:
            book = self.loader.get_book_by_abbr(book_ref.book)
            if not book:
                continue

            for chapter in book_ref.chapters:
                for ch in range(chapter.start, chapter.end + 1):
                    verses = self.loader.load_scripture_verses(book.id, ch)

                    if chapter.verses:
                        # Filter to specific verses
                        for verse_seg in chapter.verses:
                            filtered = [
                                v for v in verses
                                if verse_seg.start <= v.verse <= verse_seg.end
                            ]
                            all_verses.extend(filtered)
                    else:
                        # All verses in chapter
                        all_verses.extend(verses)

        if not all_verses:
            return [TextContent(
                type="text",
                text="No verses found for the given reference."
            )]

        # Format output
        output = f"**{parsed.pretty_string}**\n\n"
        for verse in all_verses:
            output += f"{verse.short_reference} {verse.text}\n\n"

        return [TextContent(type="text", text=output)]

    async def _parse_reference(self, args: Dict[str, Any]) -> List[TextContent]:
        """Parse a scripture reference."""
        reference = args.get("reference", "")
        parsed = self.parser.parse(reference)
        result = self.parser.to_dict(parsed)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _exact_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform exact text search."""
        query = args.get("query", "")
        case_sensitive = args.get("case_sensitive", False)
        max_results = args.get("max_results", 50)

        results = self.exact_search.search(query, case_sensitive=case_sensitive)

        # Limit results
        results = results[:max_results]

        if not results:
            return [TextContent(
                type="text",
                text=f"No results found for: {query}"
            )]

        # Format output
        output = f"**Found {len(results)} matches for '{query}'**\n\n"
        for result in results:
            output += f"**{result.short_reference}** - {result.context}\n\n"

        # Also return JSON
        json_output = json.dumps(format_search_results(results), indent=2)

        return [
            TextContent(type="text", text=output),
            TextContent(type="text", text=f"\n\nJSON Results:\n{json_output}")
        ]

    async def _semantic_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform semantic search."""
        query = args.get("query", "")
        n_results = args.get("n_results", 10)

        try:
            # Initialize if needed
            if not self.semantic_search._initialized:
                self.semantic_search.initialize()

            # Check if indexed
            if self.semantic_search.collection.count() == 0:
                return [TextContent(
                    type="text",
                    text=(
                        "Scriptures not yet indexed. Please run 'index_scriptures' "
                        "tool first."
                    )
                )]

            results = self.semantic_search.search(query, n_results=n_results)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No results found for: {query}"
                )]

            # Format output
            output = f"**Semantic search results for '{query}'**\n\n"
            for i, result in enumerate(results, 1):
                score_str = f" (score: {result.score:.3f})" if result.score else ""
                output += (
                    f"{i}. **{result.short_reference}**{score_str}\n"
                    f"   {result.verse_text}\n\n"
                )

            # Also return JSON
            json_output = json.dumps(format_search_results(results), indent=2)

            return [
                TextContent(type="text", text=output),
                TextContent(type="text", text=f"\n\nJSON Results:\n{json_output}")
            ]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Semantic search error: {str(e)}"
            )]

    async def _index_scriptures(self, args: Dict[str, Any]) -> List[TextContent]:
        """Index scriptures for semantic search."""
        force_reindex = args.get("force_reindex", False)

        try:
            self.semantic_search.initialize()
            self.semantic_search.index_scriptures(force_reindex=force_reindex)

            count = self.semantic_search.collection.count()
            return [TextContent(
                type="text",
                text=f"Indexing complete. {count} verses indexed."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Indexing error: {str(e)}"
            )]

    def _fetch_verses_for_reference(self, reference: str) -> Tuple[List[Verse], str]:
        """Helper method to fetch verses for a reference.

        Returns:
            Tuple of (verses list, pretty reference string)
        """
        parsed = self.parser.parse(reference)
        if not parsed.valid:
            raise ValueError(f"Invalid reference: {parsed.error}")

        all_verses = []
        for book_ref in parsed.references:
            book = self.loader.get_book_by_abbr(book_ref.book)
            if not book:
                continue

            for chapter in book_ref.chapters:
                for ch in range(chapter.start, chapter.end + 1):
                    verses = self.loader.load_scripture_verses(book.id, ch)

                    if chapter.verses:
                        # Filter to specific verses
                        for verse_seg in chapter.verses:
                            filtered = [
                                v for v in verses
                                if verse_seg.start <= v.verse <= verse_seg.end
                            ]
                            all_verses.extend(filtered)
                    else:
                        # All verses in chapter
                        all_verses.extend(verses)

        return all_verses, parsed.pretty_string

    async def _compare_scripture(self, args: Dict[str, Any]) -> List[TextContent]:
        """Compare two scripture passages and show their differences."""
        reference1 = args.get("reference1", "")
        reference2 = args.get("reference2", "")
        context_lines = args.get("context_lines", 3)

        try:
            # Fetch both passages
            verses1, pretty_ref1 = self._fetch_verses_for_reference(reference1)
            verses2, pretty_ref2 = self._fetch_verses_for_reference(reference2)

            if not verses1:
                return [TextContent(
                    type="text",
                    text=f"No verses found for first reference: {reference1}"
                )]

            if not verses2:
                return [TextContent(
                    type="text",
                    text=f"No verses found for second reference: {reference2}"
                )]

            # Create text representations with verse references
            text1_lines = []
            for verse in verses1:
                text1_lines.append(f"{verse.short_reference}: {verse.text}")

            text2_lines = []
            for verse in verses2:
                text2_lines.append(f"{verse.short_reference}: {verse.text}")

            # Generate unified diff
            diff = difflib.unified_diff(
                text1_lines,
                text2_lines,
                fromfile=pretty_ref1,
                tofile=pretty_ref2,
                lineterm='',
                n=context_lines
            )

            diff_output = '\n'.join(diff)

            # If no differences, say so
            if not diff_output:
                return [TextContent(
                    type="text",
                    text=f"**No differences found**\n\n{pretty_ref1} and {pretty_ref2} have identical text."
                )]

            # Format the output
            output = f"**Comparing: {pretty_ref1} vs {pretty_ref2}**\n\n"
            output += "```diff\n"
            output += diff_output
            output += "\n```\n\n"

            # Add summary statistics
            additions = diff_output.count('\n+') - 1  # Subtract header line
            deletions = diff_output.count('\n-') - 1  # Subtract header line
            output += f"**Summary:** {additions} addition(s), {deletions} deletion(s)\n\n"

            # Add legend
            output += "**Legend:**\n"
            output += "- Lines starting with `-` are in the first passage but not the second\n"
            output += "- Lines starting with `+` are in the second passage but not the first\n"
            output += "- Lines starting with ` ` (space) are common to both\n"

            return [TextContent(type="text", text=output)]

        except ValueError as e:
            return [TextContent(
                type="text",
                text=str(e)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Comparison error: {str(e)}"
            )]

    def run(self):
        """Run the MCP server."""
        import asyncio
        import mcp.server.stdio

        async def main():
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )

        asyncio.run(main())


def main():
    """Entry point for the server."""
    import sys
    import os
    from pathlib import Path

    # Get data path from environment or use default
    data_path_env = os.environ.get("SCRIPTORIAN_DATA_PATH")
    if data_path_env:
        data_path = Path(data_path_env)
    else:
        data_path = Path(__file__).parent.parent.parent / "data"

    vector_db_path_env = os.environ.get("SCRIPTORIAN_VECTOR_DB_PATH")
    if vector_db_path_env:
        vector_db_path = Path(vector_db_path_env)
    else:
        vector_db_path = Path(__file__).parent.parent.parent / "vector_db"

    if not data_path.exists():
        print(f"Error: Data path not found: {data_path}", file=sys.stderr)
        print(f"Please ensure scripture data is available at {data_path}", file=sys.stderr)
        sys.exit(1)

    vector_db_path.mkdir(parents=True, exist_ok=True)

    server = ScripturianServer(data_path, vector_db_path)
    server.run()


if __name__ == "__main__":
    main()
