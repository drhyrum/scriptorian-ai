# Testing Scriptorian MCP Server

This guide shows how to test the Scriptorian MCP server using cleverchatty-cli.

## Prerequisites

1. **Go** - Install from https://go.dev/doc/install
2. **Ollama** (optional) - Install from https://ollama.ai
   ```bash
   # Pull a small model for testing
   ollama pull qwen2.5:3b
   ```

## Quick Test

### Test Local Server (stdio)
```bash
./test_mcp.sh local
```

### Test Remote Server (Streamable HTTP)
```bash
./test_mcp.sh remote
```

### With Custom Model
```bash
./test_mcp.sh local ollama:llama3.2
./test_mcp.sh remote ollama:mistral
```

## Manual Testing

### Local Server
```bash
go run github.com/gelembjuk/cleverchatty-cli@latest \
    --config test_mcp_local.json \
    -m ollama:qwen2.5:3b
```

### Remote Server
```bash
go run github.com/gelembjuk/cleverchatty-cli@latest \
    --config test_mcp_remote.json \
    -m ollama:qwen2.5:3b
```

## Example Queries

Once the chat starts, try these:

### Fetch Scripture
```
Show me 1 Nephi 3:7
```

### Exact Search
```
Search for verses containing "faith hope charity"
```

### Semantic Search (requires indexing)
```
What scriptures talk about trusting God during trials?
```

### Parse Reference
```
Parse this reference: Alma 1-2;4-5:10
```

## Configuration Files

### test_mcp_local.json
Tests the local stdio server running on your machine.

```json
{
  "mcpServers": {
    "scriptorian": {
      "command": "/Users/hyrum/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/hyrum/src/scriptorian",
        "run",
        "python",
        "-m",
        "scriptorian.server"
      ]
    }
  }
}
```

### test_mcp_remote.json
Tests the remote Streamable HTTP server deployed on Render.

```json
{
  "mcpServers": {
    "scriptorian": {
      "url": "https://scriptorian-ai.onrender.com/mcp",
      "headers": []
    }
  }
}
```

## Troubleshooting

### "Go not found"
Install Go from https://go.dev/doc/install

### "Ollama not found"
Install Ollama from https://ollama.ai or use a different model provider.

### "Connection refused" (local)
Make sure the local server can start:
```bash
uv run python -m scriptorian.server
```

### "Connection timeout" (remote)
Check if the Render deployment is awake:
```bash
curl https://scriptorian-ai.onrender.com/health
```

## Alternative MCP Clients

You can also test with:
- **Claude Desktop** - Use the configuration in your Claude config
- **MCP Inspector** - https://github.com/modelcontextprotocol/inspector
- **Custom client** - Build your own using the MCP SDK

## What to Test

- [ ] Server connects successfully
- [ ] `fetch_scripture` - Retrieve verses by reference
- [ ] `parse_reference` - Parse plain text references
- [ ] `exact_search` - Find exact text matches
- [ ] `semantic_search` - AI-powered search (may need indexing)
- [ ] Error handling - Invalid references, missing verses
