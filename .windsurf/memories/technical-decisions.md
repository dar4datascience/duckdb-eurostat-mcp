# Technical Decisions and Rationale

## Why DuckDB Extension over Direct API?

**Decision**: Use DuckDB Eurostat extension instead of direct SDMX API calls

**Rationale**:
1. **Performance**: DuckDB optimizes queries and pushes filters to API
2. **SQL Interface**: Standard SQL is more familiar than SDMX
3. **Local Processing**: Can combine Eurostat data with other sources
4. **Caching**: DuckDB can cache results efficiently
5. **Type Safety**: Strong typing and schema validation

## Why Anthropic Claude for Translation?

**Decision**: Use Claude API for natural language to SQL translation

**Rationale**:
1. **Context Understanding**: Claude excels at understanding domain-specific queries
2. **SQL Generation**: Strong performance on SQL generation tasks
3. **Flexibility**: Can adapt to new datasets without retraining
4. **Error Handling**: Can explain errors and suggest corrections

**Alternative Considered**: Local LLM (rejected due to complexity and resource requirements)

## Why MCP Protocol?

**Decision**: Implement as MCP server rather than REST API

**Rationale**:
1. **Claude Integration**: Native integration with Claude Desktop
2. **Standardization**: MCP is becoming standard for AI tool integration
3. **Simplicity**: Less overhead than REST API
4. **Streaming**: Built-in support for streaming responses

## Project Structure Decisions

### Why `src/` Layout?

**Decision**: Use `src/duckdb_eurostat_mcp/` instead of flat structure

**Rationale**:
1. **Import Safety**: Prevents accidental imports from development directory
2. **Best Practice**: Recommended by Python Packaging Authority
3. **Testing**: Ensures tests run against installed package

### Why Separate Manager Classes?

**Decision**: Split functionality into `DuckDBManager` and `QueryTranslator`

**Rationale**:
1. **Separation of Concerns**: Each class has single responsibility
2. **Testability**: Easier to mock and test independently
3. **Reusability**: Components can be used separately
4. **Maintainability**: Changes isolated to specific components

## Testing Decisions

### Why pytest over unittest?

**Decision**: Use pytest as testing framework

**Rationale**:
1. **Simplicity**: Less boilerplate than unittest
2. **Fixtures**: Powerful fixture system
3. **Async Support**: Built-in async testing with pytest-asyncio
4. **Plugins**: Rich ecosystem (coverage, mock, etc.)

### Why Mock Anthropic API?

**Decision**: Mock Anthropic API calls in tests

**Rationale**:
1. **Speed**: Tests run faster without API calls
2. **Reliability**: No dependency on external service
3. **Cost**: Avoid API charges during testing
4. **Determinism**: Predictable test outcomes

## Dependency Decisions

### Why Minimal Dependencies?

**Decision**: Keep dependencies minimal (mcp, duckdb, anthropic)

**Rationale**:
1. **Security**: Fewer dependencies = smaller attack surface
2. **Maintenance**: Less dependency updates to manage
3. **Compatibility**: Fewer version conflicts
4. **Performance**: Faster installation

### Why Not Include pandas?

**Decision**: Use DuckDB's native DataFrame conversion instead of pandas

**Rationale**:
1. **Size**: pandas is large dependency
2. **Redundancy**: DuckDB provides similar functionality
3. **Performance**: DuckDB's native conversion is fast

## Error Handling Strategy

**Decision**: Fail fast with descriptive errors

**Rationale**:
1. **User Experience**: Clear error messages help users fix issues
2. **Debugging**: Easier to diagnose problems
3. **Reliability**: Don't hide errors or return partial results

## Configuration Strategy

**Decision**: Use environment variables over config files

**Rationale**:
1. **Security**: API keys not committed to repository
2. **Flexibility**: Easy to change per environment
3. **12-Factor**: Follows 12-factor app methodology
4. **MCP Standard**: Aligns with MCP configuration patterns

## Versioning Strategy

**Decision**: Start at 0.1.0, use semantic versioning

**Rationale**:
1. **Clarity**: Clear indication this is early/beta version
2. **Compatibility**: Semantic versioning communicates breaking changes
3. **Standard**: Industry standard versioning scheme
