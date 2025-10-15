"""MCP server for scripture study with Streamable HTTP transport for hosted deployment."""

import asyncio
import os
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server.streamable_http import StreamableHTTPServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

from .server import ScripturianServer


def create_app():
    """Create Starlette app for Streamable HTTP transport."""

    # Get data paths
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
        sys.exit(1)

    vector_db_path.mkdir(parents=True, exist_ok=True)

    # Create scripture server
    scripture_server = ScripturianServer(data_path, vector_db_path)

    # Generate a session ID for this server instance
    # In production, you might want to use a more sophisticated session management system
    session_id = str(uuid.uuid4())

    # Create Streamable HTTP transport with optional session ID
    # Set session_id to None if you don't need session management
    transport = StreamableHTTPServerTransport(
        mcp_session_id=session_id,
        is_json_response_enabled=False  # Use SSE streaming for responses
    )

    # Background task for running the MCP server
    mcp_task = None

    @asynccontextmanager
    async def lifespan(app):
        """Manage the MCP server lifecycle."""
        nonlocal mcp_task

        async def run_mcp_server():
            """Run the MCP server with the transport."""
            async with transport.connect() as (read_stream, write_stream):
                await scripture_server.app.run(
                    read_stream,
                    write_stream,
                    scripture_server.app.create_initialization_options()
                )

        # Start the MCP server in the background
        mcp_task = asyncio.create_task(run_mcp_server())

        yield

        # Cleanup on shutdown
        if mcp_task:
            mcp_task.cancel()
            try:
                await mcp_task
            except asyncio.CancelledError:
                pass

    async def handle_http(request):
        """Handle HTTP POST, GET, and DELETE requests."""
        await transport.handle_request(
            request.scope,
            request.receive,
            request._send
        )

    async def health_check(request):
        """Health check endpoint for deployment platforms."""
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "healthy", "service": "scriptorian-mcp"})

    # Create Starlette app
    app = Starlette(
        debug=True,
        routes=[
            Route("/", endpoint=health_check),
            Route("/health", endpoint=health_check),
            Route("/mcp", endpoint=handle_http, methods=["POST", "GET", "DELETE"]),
        ],
        lifespan=lifespan
    )

    return app


# For deployment with uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
