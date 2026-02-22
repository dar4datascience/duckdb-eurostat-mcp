# DuckDB Eurostat MCP Server - Project Overview

## Project Purpose

This MCP (Model Context Protocol) server enables querying Eurostat data using natural language by leveraging the DuckDB Eurostat extension. It translates human queries into SQL and executes them against the Eurostat database.

## Key Differentiator

Unlike the existing `ano-kuhanathan/eurostat-mcp` which uses direct SDMX API calls, this implementation:
- Uses the **DuckDB Eurostat extension** for data access
- Provides **SQL-based querying** with filter pushdown optimization
- Supports **natural language to SQL translation** via Claude API
- Offers **better performance** through DuckDB's query optimization

## Architecture

### Core Components

1. **server.py** - Main MCP server with 5 tools:
   - `query_eurostat` - Natural language queries
   - `list_dataflows` - Browse available datasets
   - `get_dataflow_structure` - Inspect dataset schema
   - `execute_sql` - Direct SQL execution
   - `list_providers` - List API endpoints

2. **duckdb_manager.py** - DuckDB connection and query execution
   - Manages DuckDB connection lifecycle
   - Loads and initializes Eurostat extension
   - Executes queries with error handling
   - Formats results as markdown tables

3. **query_translator.py** - Natural language to SQL translation
   - Uses Claude API (Anthropic)
   - Context-aware translation with Eurostat-specific knowledge
   - Handles common query patterns

## DuckDB Eurostat Extension Functions

- `EUROSTAT_Endpoints()` - List providers (ESTAT, ECFIN, EMPL, GROW, TAXUD)
- `EUROSTAT_Dataflows()` - List available datasets
- `EUROSTAT_DataStructure()` - Get dataset schema/dimensions
- `EUROSTAT_Read()` - Read actual data with filter pushdown

## Technology Stack

- **Python 3.10+** - Core language
- **DuckDB** - Database engine with Eurostat extension
- **MCP SDK** - Model Context Protocol implementation
- **Anthropic Claude** - Natural language processing
- **pytest** - Testing framework

## Development Workflow

1. Use virtual environment (always!)
2. Install in development mode: `pip install -e ".[dev]"`
3. Run tests before committing: `pytest`
4. Format code: `black src/ tests/`
5. Lint: `ruff check src/ tests/`

## Testing Strategy

- **Unit tests** - Individual component testing
- **Integration tests** - DuckDB extension interaction
- **Mock tests** - API calls (Anthropic)
- **Coverage target** - 80%+ code coverage

## Configuration

Required environment variables:
- `ANTHROPIC_API_KEY` - For natural language translation (optional for direct SQL)

## Future Enhancements

- Caching layer for frequently accessed datasets
- Data visualization hints in responses
- Batch query execution
- Enhanced error messages with suggestions
- Dataset recommendation engine
- Support for more complex aggregations
