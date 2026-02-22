# Contributing to DuckDB Eurostat MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/duckdb-eurostat-mcp.git
cd duckdb-eurostat-mcp
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Making Changes

1. **Write Tests First** - Add tests for new functionality
2. **Implement Feature** - Write the actual code
3. **Run Tests** - Ensure all tests pass
4. **Format Code** - Use black and ruff
5. **Type Check** - Run mypy
6. **Commit** - Write clear commit messages

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=duckdb_eurostat_mcp --cov-report=term-missing

# Run specific test
pytest tests/test_server.py::TestEurostatMCPServer::test_list_tools -v
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

### Example

```python
def execute_query(self, sql: str, limit: int | None = None) -> str:
    """Execute a SQL query and return results as markdown.
    
    Args:
        sql: SQL query to execute
        limit: Maximum number of rows to return
        
    Returns:
        Query results formatted as markdown table
        
    Raises:
        Exception: If query execution fails
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

## Testing Guidelines

### Test Structure

- One test file per source file
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

### Example Test

```python
class TestDuckDBManager:
    @pytest.fixture
    def db_manager(self):
        manager = DuckDBManager()
        yield manager
        manager.close()

    def test_execute_query_with_results(self, db_manager):
        result = db_manager.execute_query("SELECT 1 as value")
        assert "value" in result
        assert "1" in result
```

## Adding New Features

### 1. Plan Your Feature

- What problem does it solve?
- What are the inputs/outputs?
- How will it integrate with existing code?

### 2. Update Documentation

- Add to README.md if user-facing
- Update docstrings
- Add examples

### 3. Add Tests

- Unit tests for new functions
- Integration tests for new tools
- Edge case tests

### 4. Implement

Follow the workflow in `.windsurf/workflows/add-new-feature.md`

## Commit Message Guidelines

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks

### Examples

```
feat(server): add dataset recommendation tool

Add new MCP tool that recommends related datasets based on
current query context.

Closes #123
```

```
fix(translator): handle multi-line SQL queries

The query translator was failing on multi-line SQL. Updated
regex pattern to handle newlines correctly.
```

## Pull Request Process

### 1. Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Code is linted (ruff)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines

### 2. Submit PR

- Write clear title and description
- Reference related issues
- Add screenshots/examples if applicable
- Request review from maintainers

### 3. Review Process

- Address review comments
- Keep PR focused and small
- Rebase if needed to resolve conflicts

### 4. After Merge

- Delete your feature branch
- Update your local main branch

## Project-Specific Guidelines

### DuckDB Queries

- Always use parameterized queries when possible
- Add LIMIT clauses to prevent large result sets
- Use filter pushdown for better performance
- Handle empty results gracefully

### MCP Tools

- Provide clear descriptions
- Define complete input schemas
- Return helpful error messages
- Include usage examples in docstrings

### Natural Language Translation

- Test with various query phrasings
- Handle ambiguous queries gracefully
- Provide SQL explanation in responses
- Consider edge cases (typos, unclear intent)

## Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [DuckDB Eurostat Extension](https://github.com/ahuarte47/duckdb-eurostat)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Eurostat API Documentation](https://ec.europa.eu/eurostat/web/main/data/web-services)

## Getting Help

- Check `.windsurf/memories/common-issues.md`
- Review existing issues on GitHub
- Ask questions in pull request comments
- Open a discussion for design questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
