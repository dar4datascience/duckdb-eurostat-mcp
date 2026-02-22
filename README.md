# DuckDB Eurostat MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables querying Eurostat data using natural language. This server leverages the [DuckDB Eurostat extension](https://github.com/ahuarte47/duckdb-eurostat) to translate human queries into SQL and execute them efficiently against the Eurostat database.

## Features

- 🗣️ **Natural Language Queries** - Ask questions in plain English, get SQL and data back
- 🤖 **Flexible LLM Support** - Choose from Anthropic, OpenAI, Ollama (local), or Azure OpenAI
- 🚀 **DuckDB Powered** - Fast query execution with filter pushdown optimization
- 📊 **Rich Dataset Access** - Access all Eurostat datasets (GDP, unemployment, population, etc.)
- 🔍 **Dataset Discovery** - Browse and search available datasets
- 📈 **Schema Inspection** - Understand dataset structure before querying
- 🎯 **Direct SQL Support** - Execute raw SQL for advanced use cases
- 🔒 **Privacy Options** - Use local LLMs with Ollama for complete data privacy

## Key Differentiator

Unlike other Eurostat MCP implementations that use direct SDMX API calls, this server:
- Uses the **DuckDB Eurostat extension** for optimized data access
- Provides **SQL-based querying** with automatic filter pushdown
- Supports **natural language to SQL translation** via Claude API
- Offers **better performance** through DuckDB's query optimization

## Installation

### Prerequisites

- Python 3.10 or higher
- LLM Provider (choose one):
  - **Anthropic API key** (default, recommended)
  - **OpenAI API key**
  - **Ollama** (local, free, no API key needed)
  - **Azure OpenAI** (enterprise)

### Install with pip

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/duckdb-eurostat-mcp.git
cd duckdb-eurostat-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with your preferred LLM provider
pip install -e ".[anthropic]"  # Anthropic Claude (default)
# OR
pip install -e ".[openai]"     # OpenAI GPT
# OR
pip install -e ".[ollama]"     # Ollama (local)
# OR
pip install -e ".[azure]"      # Azure OpenAI
# OR
pip install -e ".[all-providers]"  # All providers

# For development (includes all providers)
pip install -e ".[dev]"
```

## Configuration

### LLM Provider Setup

The server supports multiple LLM providers. Choose the one that fits your needs:

#### Option 1: Anthropic Claude (Default, Recommended)

```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-api-key-here
```

**Get API Key:** https://console.anthropic.com/

#### Option 2: OpenAI GPT

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
```

**Get API Key:** https://platform.openai.com/api-keys

#### Option 3: Ollama (Local, Free, Private)

```bash
export LLM_PROVIDER=ollama
# No API key needed!
```

**Setup:**
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama3.1`
3. Start Ollama: `ollama serve`

**Benefits:** No API costs, complete privacy, works offline

#### Option 4: Azure OpenAI

```bash
export LLM_PROVIDER=azure
export AZURE_OPENAI_API_KEY=your-api-key-here
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

### Claude Desktop Configuration

Add to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**With Anthropic (default):**
```json
{
  "mcpServers": {
    "duckdb-eurostat": {
      "command": "python",
      "args": ["-m", "duckdb_eurostat_mcp.server"],
      "env": {
        "LLM_PROVIDER": "anthropic",
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**With OpenAI:**
```json
{
  "mcpServers": {
    "duckdb-eurostat": {
      "command": "python",
      "args": ["-m", "duckdb_eurostat_mcp.server"],
      "env": {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**With Ollama (local):**
```json
{
  "mcpServers": {
    "duckdb-eurostat": {
      "command": "python",
      "args": ["-m", "duckdb_eurostat_mcp.server"],
      "env": {
        "LLM_PROVIDER": "ollama"
      }
    }
  }
}
```

**See [docs/LLM_PROVIDERS.md](docs/LLM_PROVIDERS.md) for detailed configuration guide.**

## Available Tools

### 1. query_eurostat

Query Eurostat data using natural language.

**Example:**
```
Query: "Get population data for Germany in 2020"
```

### 2. list_dataflows

List available Eurostat datasets with optional filtering.

**Parameters:**
- `provider` (optional): Filter by provider (e.g., 'ESTAT')
- `search` (optional): Search term to filter by label
- `limit` (optional): Maximum results (default: 50)

### 3. get_dataflow_structure

Get the structure (dimensions and concepts) of a specific dataset.

**Parameters:**
- `provider_id`: Provider ID (e.g., 'ESTAT')
- `dataflow_id`: Dataset ID (e.g., 'DEMO_R_D2JAN')

### 4. execute_sql

Execute raw SQL queries against the DuckDB Eurostat database.

**Parameters:**
- `sql`: SQL query to execute
- `limit` (optional): Maximum rows to return (default: 100)

### 5. list_providers

List all available Eurostat API endpoints/providers.

## Usage Examples

### Natural Language Queries

```
"Show unemployment rates for EU countries in 2023"
"What was the GDP of France from 2015 to 2020?"
"List population data for Germany by age group"
```

### Direct SQL Queries

```sql
-- Get population data for Germany
SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') 
WHERE geo = 'DE' AND time_period = '2020'
LIMIT 10;

-- List available datasets about GDP
SELECT dataflow_id, label 
FROM EUROSTAT_Dataflows(language := 'en')
WHERE label ILIKE '%GDP%'
LIMIT 20;

-- Get dataset structure
SELECT dimension, concept 
FROM EUROSTAT_DataStructure('ESTAT', 'DEMO_R_D2JAN', language := 'en');
```

## Popular Datasets

- **DEMO_R_D2JAN** - Population by age, sex, and NUTS-2 region
- **UNE_RT_A** - Unemployment rates
- **NAMA_10_GDP** - GDP and main components
- **PRC_HICP_MIDX** - HICP - Monthly index (inflation)
- **COMEXT** - International trade data

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=duckdb_eurostat_mcp --cov-report=html

# Run specific test file
pytest tests/test_duckdb_manager.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### Testing with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Run your server
python -m duckdb_eurostat_mcp.server
```

## Project Structure

```
duckdb-eurostat-mcp/
├── src/
│   └── duckdb_eurostat_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server
│       ├── duckdb_manager.py   # DuckDB connection management
│       └── query_translator.py # Natural language to SQL
├── tests/
│   ├── test_server.py
│   ├── test_duckdb_manager.py
│   └── test_query_translator.py
├── .windsurf/
│   ├── workflows/              # Development workflows
│   └── memories/               # Project documentation
├── pyproject.toml
└── README.md
```

## Workflows

This project includes helpful workflows in `.windsurf/workflows/`:

- **setup-and-test.md** - Setup development environment and run tests
- **deploy-to-github.md** - Deploy to GitHub with CI/CD
- **add-new-feature.md** - Add new features to the server

Use them with: `/setup-and-test`, `/deploy-to-github`, `/add-new-feature`

## Troubleshooting

### DuckDB Extension Not Loading

Ensure you have internet connection on first run to download the extension.

### API Key Errors

Verify `ANTHROPIC_API_KEY` is set correctly in your environment.

### Query Performance

Use filters to reduce data volume:
```sql
WHERE geo = 'DE' AND time_period >= '2020'
```

See `.windsurf/memories/common-issues.md` for more solutions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black src/ tests/`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [DuckDB Eurostat Extension](https://github.com/ahuarte47/duckdb-eurostat) by ahuarte47
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Eurostat](https://ec.europa.eu/eurostat) for providing the data

## Related Projects

- [eurostat-mcp](https://github.com/ano-kuhanathan/eurostat-mcp) - Alternative MCP implementation using direct SDMX API
- [DuckDB](https://duckdb.org/) - Fast in-process analytical database

## Support

For issues and questions:
- Open an issue on GitHub
- Check `.windsurf/memories/common-issues.md` for common problems
- Review the workflows in `.windsurf/workflows/`