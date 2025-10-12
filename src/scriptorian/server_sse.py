"""MCP server for scripture study with SSE transport for hosted deployment."""

import os
import sys
from pathlib import Path

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

from .server import ScripturianServer


def create_app():
    """Create Starlette app for SSE transport."""
    
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
    
    # Create SSE transport
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        """Handle SSE connection."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as (read_stream, write_stream):
            await scripture_server.app.run(
                read_stream,
                write_stream,
                scripture_server.app.create_initialization_options()
            )
    
    async def handle_messages(request):
        """Handle POST messages."""
        return await sse.handle_post_message(request.scope, request.receive, request._send)

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
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )
    
    return app


# For deployment with uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
