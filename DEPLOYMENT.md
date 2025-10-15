# Deployment Guide

## Overview

This MCP server uses the **Streamable HTTP transport** (MCP protocol version 2025-03-26 and later), which provides:

- Better scalability with stateless server support
- Bidirectional communication over standard HTTP
- Optional session management with secure session IDs
- Support for cloud deployments (AWS Lambda, Railway, Render, etc.)
- Works seamlessly with load balancers and serverless platforms
- No requirement for long-lived connections

## Deploying to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `scriptorian-ai` repository (https://github.com/drhyrum/scriptorian-ai)
4. Railway will automatically detect the `railway.json` configuration
5. Set environment variables (optional):
   - `SCRIPTORIAN_DATA_PATH`: Path to scripture data (default: ./data)
   - `SCRIPTORIAN_VECTOR_DB_PATH`: Path to vector database (default: ./vector_db)
6. Deploy! Your server will be available at: `https://your-app.railway.app/mcp`

## Deploying to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your `scriptorian-ai` repository (https://github.com/drhyrum/scriptorian-ai)
4. Render will automatically detect the `render.yaml` configuration
5. Click "Create Web Service"
6. Your server will be available at: `https://scriptorian.onrender.com/mcp`

## Using the Hosted Server

Once deployed, update your Claude Desktop config to use the hosted version with the Streamable HTTP endpoint:

```json
{
  "mcpServers": {
    "scriptorian": {
      "url": "https://your-deployment-url.com/mcp"
    }
  }
}
```

Replace `your-deployment-url.com` with your actual deployment URL.

## Custom Domain (scriptorian.ai)

### Railway
1. In your Railway project settings, go to "Settings" → "Domains"
2. Click "Custom Domain" and add `scriptorian.ai`
3. Update your DNS records with Railway's provided values

### Render
1. In your Render service settings, go to "Settings" → "Custom Domain"
2. Add `scriptorian.ai`
3. Update your DNS A record to point to Render's IP

## Environment Variables

- `PORT`: Port to run the server on (default: 8000)
- `SCRIPTORIAN_DATA_PATH`: Custom path to scripture data
- `SCRIPTORIAN_VECTOR_DB_PATH`: Custom path to vector database

## Pre-indexing for Production

For better first-request performance, you can pre-index the scriptures:

```bash
python scripts/index_scriptures.py
```

Then commit the `vector_db/` directory (update `.gitignore` to allow it).

## Transport Details

### Streamable HTTP Transport

The server uses the MCP Streamable HTTP transport, which provides:

- **Single HTTP Endpoint**: `/mcp` handles POST, GET, and DELETE requests
- **Session Management**: Optional session IDs for tracking connections
- **POST Requests**: Client sends JSON-RPC messages to the server
- **GET Requests**: Client establishes SSE stream for server-initiated messages
- **DELETE Requests**: Client can explicitly terminate sessions

### Protocol Headers

Clients must include these headers:

- `Accept`: Must include both `application/json` and `text/event-stream`
- `Content-Type`: Must be `application/json` for POST requests
- `MCP-Protocol-Version`: Protocol version (defaults to `2025-03-26`)
- `MCP-Session-Id`: Session identifier (if session management is enabled)

### Health Checks

The server provides health check endpoints for monitoring:

- `GET /` - Returns `{"status": "healthy", "service": "scriptorian-mcp"}`
- `GET /health` - Same as above

These endpoints can be used by deployment platforms for health monitoring.
