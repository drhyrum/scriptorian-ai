# Virtual Environment Setup

## Overview

Scriptorian now uses a virtual environment (`.venv`) to isolate its dependencies from your system Python installation.

## What Changed

### Installation Script (`install.sh`)

The installation script now:
1. **Creates `.venv`** virtual environment automatically
2. **Installs all dependencies** into the venv using `uv pip install`
3. **Runs tests** using `uv run python` to use the venv
4. **Indexes scriptures** using the venv Python

### Benefits

✅ **Isolated dependencies** - Won't conflict with other Python projects
✅ **Reproducible** - Everyone gets the same environment
✅ **Clean uninstall** - Just delete `.venv` directory
✅ **Version locked** - Dependencies stay consistent

## Using the Virtual Environment

### Option 1: Activate the venv (Recommended for development)

```bash
# Activate
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Now use python normally
python -m scriptorian.server
python scripts/index_scriptures.py
pytest

# Deactivate when done
deactivate
```

### Option 2: Use uv run (No activation needed)

```bash
# Run commands directly
uv run python -m scriptorian.server
uv run python scripts/index_scriptures.py
uv run pytest
```

### Option 3: Claude Desktop (Uses venv automatically)

The MCP config now points directly to the venv Python:

```json
{
  "mcpServers": {
    "scriptorian": {
      "command": "/Users/hyrum/src/scriptorian/.venv/bin/python",
      "args": ["-m", "scriptorian.server"],
      "cwd": "/Users/hyrum/src/scriptorian"
    }
  }
}
```

## Installation

### Automated (Recommended)

```bash
cd /Users/hyrum/src/scriptorian
./install.sh
```

This will:
1. Create `.venv` virtual environment
2. Install all dependencies
3. Test the installation
4. Optionally index scriptures

### Manual

```bash
cd /Users/hyrum/src/scriptorian

# Create venv
uv venv

# Install dependencies
uv pip install -e .

# Test
uv run python -c "import scriptorian; print('OK')"

# Optional: Index scriptures
uv run python scripts/index_scriptures.py
```

## Directory Structure

```
scriptorian/
├── .venv/                    # Virtual environment (gitignored)
│   ├── bin/                  # Executables (python, pip, etc)
│   ├── lib/                  # Installed packages
│   └── pyvenv.cfg            # Config file
├── src/scriptorian/          # Source code
├── scripts/                  # Utility scripts
├── pyproject.toml            # Dependencies definition
└── install.sh                # Installation script
```

## Checking Your Setup

### Verify venv exists

```bash
ls -la .venv/
```

Should show:
```
.venv/
├── bin/
├── lib/
└── pyvenv.cfg
```

### Check Python version

```bash
source .venv/bin/activate
which python
# Should show: /Users/hyrum/src/scriptorian/.venv/bin/python

python --version
# Should show: Python 3.11.x or 3.12.x
```

### Verify dependencies

```bash
source .venv/bin/activate
pip list
```

Should include:
- mcp (1.17.0+)
- sentence-transformers (2.2.0+)
- chromadb (0.4.0+)
- numpy, torch, etc.

## Troubleshooting

### "Command not found: uv"

Install uv first:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### ".venv already exists"

If you need to recreate:
```bash
rm -rf .venv
./install.sh
```

### "Module not found" errors

Make sure you're using the venv:
```bash
# Check which Python
which python
# Should show: /path/to/scriptorian/.venv/bin/python

# If not, activate:
source .venv/bin/activate
```

Or use `uv run`:
```bash
uv run python -m scriptorian.server
```

### Claude Desktop can't find module

Update your MCP config to use the full path:
```json
{
  "command": "/Users/hyrum/src/scriptorian/.venv/bin/python"
}
```

NOT:
```json
{
  "command": "python"  // ❌ Uses system Python
}
```

## Updating Dependencies

### Add new dependency

```bash
# Edit pyproject.toml, then:
uv pip install -e .
```

### Update all dependencies

```bash
uv pip install -e . --upgrade
```

### Update specific package

```bash
uv pip install --upgrade sentence-transformers
```

## Development Workflow

### Daily Development

```bash
# Activate once per terminal session
source .venv/bin/activate

# Work normally
python -m scriptorian.server
pytest
python scripts/index_scriptures.py

# Deactivate when done
deactivate
```

### Quick Testing

```bash
# No activation needed
uv run pytest
uv run python -m scriptorian.server
```

### IDE Setup

#### VS Code

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

#### PyCharm

1. Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `.venv/bin/python`

## CI/CD

### GitHub Actions Example

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    uv venv
    uv pip install -e .

- name: Run tests
  run: uv run pytest
```

## Deployment

### Option 1: Deploy with venv

```bash
# Build on deployment server
./install.sh

# Configure MCP with absolute path
{
  "command": "/full/path/to/.venv/bin/python"
}
```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv venv
RUN uv pip install -e .

CMD ["uv", "run", "python", "-m", "scriptorian.server"]
```

## Best Practices

1. ✅ **Always use venv** for isolation
2. ✅ **Commit `pyproject.toml`** for dependency tracking
3. ✅ **Don't commit `.venv/`** (already in .gitignore)
4. ✅ **Use `uv run`** for one-off commands
5. ✅ **Activate venv** for interactive development
6. ✅ **Full paths in MCP config** for Claude Desktop

## Migration from System Python

If you previously installed to system Python:

```bash
# Uninstall from system
pip uninstall scriptorian

# Clean up
rm -rf build/ dist/ *.egg-info/

# Install with venv
./install.sh
```

## Summary

The virtual environment ensures:
- 🔒 **Isolated** dependencies
- 🔄 **Reproducible** installations
- 🧹 **Clean** uninstalls
- ⚡ **Fast** setup with uv
- 🎯 **Consistent** across all environments

Just run `./install.sh` and everything is handled automatically!
