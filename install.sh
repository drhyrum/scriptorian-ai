#!/bin/bash
# Scriptorian Installation Script

set -e

echo "========================================="
echo "Scriptorian Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' package manager not found."
    echo "Please install uv first: https://github.com/astral-sh/uv"
    exit 1
fi

echo "Found uv package manager"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
    echo "✓ Virtual environment created"
else
    echo "Using existing virtual environment"
fi

echo ""

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

echo ""
echo "Testing installation..."
uv run python -c "from src.scriptorian.data_loader import ScriptureLoader; print('✓ Data loader import successful')"
uv run python -c "from src.scriptorian.reference_parser import ReferenceParser; print('✓ Reference parser import successful')"
uv run python -c "from src.scriptorian.search import ExactSearch; print('✓ Search engine import successful')"
uv run python -c "from src.scriptorian.server import ScripturianServer; print('✓ MCP server import successful')"

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""

# Ask about indexing
echo "Would you like to index scriptures for semantic search now?"
echo "This will:"
echo "  - Download AI model (~80MB, one-time)"
echo "  - Generate embeddings for all verses (5-10 minutes)"
echo "  - Enable AI-powered semantic search"
echo ""
read -p "Index now? (Y/n): " index_choice
index_choice=${index_choice:-Y}

if [[ "$index_choice" =~ ^[Yy]$ ]]; then
    echo ""
    echo "========================================="
    echo "Starting Scripture Indexing"
    echo "========================================="
    echo ""
    uv run python scripts/index_scriptures.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Semantic search is ready to use!"
    else
        echo ""
        echo "⚠️  Indexing failed or was interrupted."
        echo "You can run indexing later with:"
        echo "  uv run python scripts/index_scriptures.py"
    fi
else
    echo ""
    echo "Skipping indexing. You can run it later with:"
    echo "  uv run python scripts/index_scriptures.py"
    echo ""
    echo "Or use the 'index_scriptures' tool from Claude Desktop."
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Virtual environment: .venv"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate  # Linux/macOS"
echo "  .venv\\Scripts\\activate     # Windows"
echo ""
echo "Next steps:"
echo "1. Review QUICKSTART.md for usage instructions"
echo "2. Add server to Claude Desktop config (see mcp_config_example.json)"
echo "3. Restart Claude Desktop"
echo ""
echo "To test standalone (with venv activated):"
echo "  python -m scriptorian.server"
echo ""
echo "Or without activating venv:"
echo "  uv run python -m scriptorian.server"
echo ""
