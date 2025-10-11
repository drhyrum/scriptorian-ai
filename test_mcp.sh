#!/bin/bash
# Test script for Scriptorian MCP server

set -e

echo "========================================="
echo "Scriptorian MCP Server Test Script"
echo "========================================="
echo ""

# Check if go is installed
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed. Please install Go first."
    echo "Visit: https://go.dev/doc/install"
    exit 1
fi

# Check if ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Warning: Ollama is not installed."
    echo "Install from: https://ollama.ai"
    echo ""
fi

# Parse arguments
TEST_TYPE="${1:-local}"
MODEL="${2:-ollama:qwen2.5:3b}"

if [ "$TEST_TYPE" = "local" ]; then
    echo "Testing LOCAL MCP server (stdio)"
    echo "Config: test_mcp_local.json"
    echo "Model: $MODEL"
    echo ""
    echo "Starting test..."
    echo "Try commands like:"
    echo "  - Show me 1 Nephi 3:7"
    echo "  - Search for verses about faith"
    echo ""
    go run github.com/gelembjuk/cleverchatty-cli@latest \
        --config test_mcp_local.json \
        -m "$MODEL"
elif [ "$TEST_TYPE" = "remote" ]; then
    echo "Testing REMOTE MCP server (SSE)"
    echo "URL: https://scriptorian-ai.onrender.com/sse"
    echo "Config: test_mcp_remote.json"
    echo "Model: $MODEL"
    echo ""
    echo "Starting test..."
    echo "Try commands like:"
    echo "  - Show me 1 Nephi 3:7"
    echo "  - Search for verses about faith"
    echo ""
    go run github.com/gelembjuk/cleverchatty-cli@latest \
        --config test_mcp_remote.json \
        -m "$MODEL"
else
    echo "Usage: ./test_mcp.sh [local|remote] [model]"
    echo ""
    echo "Examples:"
    echo "  ./test_mcp.sh local                    # Test local server with default model"
    echo "  ./test_mcp.sh remote                   # Test remote server with default model"
    echo "  ./test_mcp.sh local ollama:llama3.2    # Test with different model"
    echo ""
    echo "Default model: ollama:qwen2.5:3b"
    exit 1
fi
