---
description: Setup development environment and run tests for the DuckDB Eurostat MCP server
auto_execution_mode: 2
---

# Setup and Test Workflow

This workflow guides you through setting up the development environment and running tests for the DuckDB Eurostat MCP server.

## Prerequisites

- Python 3.10 or higher installed
- Git installed
- Anthropic API key (for natural language query translation)

## Steps

### 1. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

// turbo
### 2. Install dependencies in development mode

```bash
pip install -e ".[dev]"
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

**Important:** Replace `your-api-key-here` with your actual Anthropic API key.

### 4. Run all tests

// turbo
```bash
pytest
```

### 5. Run tests with coverage report

```bash
pytest --cov=duckdb_eurostat_mcp --cov-report=html
```

### 6. Run specific test file

```bash
pytest tests/test_duckdb_manager.py -v
```

### 7. Format code with Black

// turbo
```bash
black src/ tests/
```

### 8. Lint code with Ruff

// turbo
```bash
ruff check src/ tests/
```

### 9. Type check with mypy

```bash
mypy src/
```

## Testing the MCP Server Locally

### 10. Test with MCP Inspector (recommended)

Install the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Then run your server:

```bash
python -m duckdb_eurostat_mcp.server
```

### 11. Test individual components in Python REPL

```python
from duckdb_eurostat_mcp.duckdb_manager import DuckDBManager

# Initialize manager
db = DuckDBManager()

# Test listing providers
result = db.execute_query("SELECT * FROM EUROSTAT_Endpoints()")
print(result)

# Test listing dataflows
result = db.execute_query("SELECT * FROM EUROSTAT_Dataflows(language := 'en') LIMIT 5")
print(result)

# Test reading data
result = db.execute_query("SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') WHERE geo = 'DE' LIMIT 5")
print(result)
```

## Troubleshooting

- **DuckDB extension not loading**: Ensure you have internet connection for the first run to download the extension
- **Tests failing**: Make sure virtual environment is activated and all dependencies are installed
- **Import errors**: Verify the package is installed in development mode (`pip install -e .`)
- **API key errors**: Ensure `ANTHROPIC_API_KEY` is set in your environment or `.env` file

## Next Steps

After successful setup and testing:
1. Configure the MCP server in Claude Desktop or other MCP clients
2. Start building queries and testing natural language translation
3. Explore different Eurostat datasets
