#!/bin/bash
# Test script for Scriptorian MCP server

echo "========================================="
echo "Scriptorian MCP Server Test Script"
echo "========================================="
echo ""

# Check if go is installed
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed."
    echo "Install: brew install go"
    exit 1
fi

# Check if ollama is accessible
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "Warning: Ollama doesn't seem to be running."
    echo "Start it with: ollama serve"
    echo "Install from: https://ollama.ai"
    echo ""
fi

TEST_TYPE="${1:-local}"

if [ "$TEST_TYPE" = "local" ]; then
    echo "Testing: LOCAL MCP server (stdio)"
    echo "Config:  test_mcp_local.json"
    echo ""
    go run github.com/gelembjuk/cleverchatty-cli@latest --config test_mcp_local.json
elif [ "$TEST_TYPE" = "remote" ]; then
    echo "Testing: REMOTE MCP server (SSE)"
    echo "Config:  test_mcp_remote.json"
    echo ""
    go run github.com/gelembjuk/cleverchatty-cli@latest --config test_mcp_remote.json
else
    echo "Usage: ./test_mcp.sh [local|remote]"
    echo ""
    echo "Before running, make sure Ollama is running:"
    echo "  ollama serve"
    echo ""
    echo "Examples:"
    echo "  ./test_mcp.sh local   # Test local stdio server"
    echo "  ./test_mcp.sh remote  # Test remote SSE server"
    exit 1
fi
