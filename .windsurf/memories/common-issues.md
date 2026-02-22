# Common Issues and Solutions

## Development Issues

### Issue: DuckDB Extension Not Loading

**Symptoms**: Error "Extension 'eurostat' not found"

**Solutions**:
1. Ensure internet connection (first-time download)
2. Check DuckDB version >= 1.0.0
3. Try manual installation:
   ```python
   import duckdb
   conn = duckdb.connect()
   conn.execute("INSTALL eurostat FROM community")
   conn.execute("LOAD eurostat")
   ```

### Issue: Import Errors After Installation

**Symptoms**: `ModuleNotFoundError: No module named 'duckdb_eurostat_mcp'`

**Solutions**:
1. Ensure virtual environment is activated
2. Install in development mode: `pip install -e .`
3. Check Python path: `python -c "import sys; print(sys.path)"`

### Issue: Tests Failing with API Key Error

**Symptoms**: Tests fail with "ANTHROPIC_API_KEY not configured"

**Solutions**:
1. Set environment variable: `export ANTHROPIC_API_KEY=your-key`
2. Create `.env` file with key
3. For tests, use mock (already configured in conftest.py)

### Issue: Virtual Environment Not Activating

**Symptoms**: Wrong Python version or packages not found

**Solutions**:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify
which python  # Should point to venv
```

## Runtime Issues

### Issue: Query Translation Fails

**Symptoms**: "Failed to translate query" error

**Solutions**:
1. Verify ANTHROPIC_API_KEY is set correctly
2. Check API key has sufficient credits
3. Try simpler query first
4. Use `execute_sql` tool for direct SQL instead

### Issue: Slow Query Performance

**Symptoms**: Queries take too long to execute

**Solutions**:
1. Add filters to reduce data volume:
   ```sql
   WHERE geo = 'DE' AND time_period >= '2020'
   ```
2. Use LIMIT clause
3. Query specific dimensions instead of SELECT *
4. Check if filters are pushed down (dimension filters only)

### Issue: "Data too large" Error

**Symptoms**: Query returns too much data

**Solutions**:
1. Add more specific filters
2. Reduce time range
3. Use aggregation (GROUP BY)
4. Increase limit parameter

### Issue: Dataset Not Found

**Symptoms**: "Dataflow not found" or empty results

**Solutions**:
1. List available dataflows first:
   ```sql
   SELECT * FROM EUROSTAT_Dataflows(language := 'en') LIMIT 100
   ```
2. Check provider_id and dataflow_id spelling
3. Verify dataset is still available in Eurostat

## Testing Issues

### Issue: Tests Hang or Timeout

**Symptoms**: Tests don't complete

**Solutions**:
1. Check for infinite loops in async code
2. Verify mock setup for external APIs
3. Add timeout to pytest: `pytest --timeout=30`

### Issue: Coverage Report Not Generated

**Symptoms**: No coverage.xml or htmlcov/ directory

**Solutions**:
1. Install coverage: `pip install pytest-cov`
2. Run with coverage flag: `pytest --cov=duckdb_eurostat_mcp`
3. Check file permissions in project directory

### Issue: Type Checking Fails

**Symptoms**: mypy reports errors

**Solutions**:
1. Add type hints to function signatures
2. Use `# type: ignore` for known issues
3. Update mypy configuration in pyproject.toml
4. Install type stubs: `pip install types-*`

## Deployment Issues

### Issue: GitHub Actions Failing

**Symptoms**: CI pipeline fails

**Solutions**:
1. Check GitHub Actions logs for specific error
2. Verify secrets are set (ANTHROPIC_API_KEY)
3. Test locally first: `pytest`
4. Check Python version compatibility

### Issue: MCP Server Not Connecting

**Symptoms**: Claude Desktop can't connect to server

**Solutions**:
1. Verify server is running: `python -m duckdb_eurostat_mcp.server`
2. Check MCP configuration in Claude Desktop
3. Look for errors in server logs
4. Test with MCP Inspector first

### Issue: Package Not Installing

**Symptoms**: `pip install` fails

**Solutions**:
1. Update pip: `pip install --upgrade pip`
2. Check Python version >= 3.10
3. Install build dependencies: `pip install build hatchling`
4. Try installing dependencies separately

## Data Issues

### Issue: Unexpected Data Format

**Symptoms**: Data doesn't match expected structure

**Solutions**:
1. Check dataset structure first:
   ```sql
   SELECT * FROM EUROSTAT_DataStructure('ESTAT', 'dataflow_id', language := 'en')
   ```
2. Verify dimension names and values
3. Check for dataset updates in Eurostat

### Issue: Missing Time Periods

**Symptoms**: Recent data not available

**Solutions**:
1. Check Eurostat website for data availability
2. Some datasets have publication delays
3. Use different time frequency (annual vs monthly)

### Issue: Geographic Codes Not Recognized

**Symptoms**: Filters on geo dimension return no results

**Solutions**:
1. Use correct geo codes (ISO 2-letter: 'DE', 'FR', etc.)
2. Check geo_level dimension for available levels
3. List available geo values:
   ```sql
   SELECT DISTINCT geo FROM EUROSTAT_Read('ESTAT', 'dataflow_id') LIMIT 100
   ```
