---
description: Add a new feature to the DuckDB Eurostat MCP server
auto_execution_mode: 3
---

# Add New Feature Workflow

This workflow guides you through adding new features to the MCP server while maintaining code quality.

## Steps

### 1. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Plan your feature

Consider:
- What new MCP tool(s) will you add?
- What DuckDB Eurostat functions will you use?
- What parameters are needed?
- How will errors be handled?

### 3. Update the server.py

Add new tool definition in `_setup_handlers()`:

```python
Tool(
    name="your_new_tool",
    description="Clear description of what this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description",
            },
        },
        "required": ["param1"],
    },
)
```

### 4. Implement the handler method

Add handler in the `EurostatMCPServer` class:

```python
async def _handle_your_new_tool(self, arguments: dict[str, Any]) -> list[TextContent]:
    # Implementation here
    pass
```

### 5. Add the tool to call_tool dispatcher

```python
elif name == "your_new_tool":
    return await self._handle_your_new_tool(arguments)
```

### 6. Write tests

Create tests in `tests/test_server.py`:

```python
@pytest.mark.asyncio
async def test_your_new_tool(self, server):
    result = await server._handle_your_new_tool({
        "param1": "test_value"
    })
    assert len(result) > 0
    # Add more assertions
```

### 7. Run tests

// turbo
```bash
pytest tests/test_server.py::TestEurostatMCPServer::test_your_new_tool -v
```

### 8. Run all tests to ensure nothing broke

```bash
pytest
```

### 9. Format and lint

// turbo
```bash
black src/ tests/
ruff check src/ tests/
```

### 10. Update documentation

Update README.md with:
- New tool description
- Example usage
- Any new dependencies

### 11. Commit your changes

```bash
git add .
git commit -m "feat: add [feature name] tool for [purpose]"
```

### 12. Push and create pull request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub.

## Feature Ideas

Consider implementing:
- **Time series analysis**: Tools for analyzing trends over time
- **Geographic filtering**: Enhanced geo-level filtering and aggregation
- **Data export**: Export to different formats (CSV, JSON, Parquet)
- **Caching**: Cache frequently accessed datasets
- **Visualization hints**: Return data with visualization suggestions
- **Dataset recommendations**: Suggest related datasets based on query
- **Metadata search**: Enhanced search across dataset metadata
- **Batch queries**: Execute multiple queries in one call
- **Data validation**: Validate query results and data quality
- **Custom aggregations**: Pre-built aggregation functions for common patterns

## Best Practices

- Keep tools focused and single-purpose
- Provide clear, helpful error messages
- Add comprehensive tests for edge cases
- Document all parameters thoroughly
- Consider rate limiting for API-heavy operations
- Use type hints consistently
- Follow existing code patterns and style
