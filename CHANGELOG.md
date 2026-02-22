# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-22

### Added
- **Flexible LLM Provider Support**: The MCP server now supports multiple LLM providers
  - Anthropic Claude (default)
  - OpenAI GPT-4
  - Ollama (local LLM execution)
  - Azure OpenAI
- New `llm_providers.py` module with abstract base class and provider implementations
- Provider factory function for easy provider creation
- Comprehensive LLM provider documentation in `docs/LLM_PROVIDERS.md`
- New test suite for LLM providers (`tests/test_llm_providers.py`)
- Environment variable `LLM_PROVIDER` to configure which provider to use

### Changed
- **BREAKING**: `QueryTranslator` now uses provider pattern instead of direct Anthropic client
  - Old: `QueryTranslator(api_key="...")`
  - New: `QueryTranslator(provider_type="anthropic", api_key="...")` or `QueryTranslator(provider=custom_provider)`
- **BREAKING**: Anthropic is now an optional dependency
  - Install with: `pip install -e ".[anthropic]"` or `pip install -e ".[all-providers]"`
- Updated `EurostatMCPServer` to accept LLM provider configuration
- Refactored all tests to work with the new provider system
- Updated README with comprehensive provider configuration examples
- Updated `.env.example` with configuration for all supported providers

### Migration Guide

**For existing users using Anthropic:**

No changes needed if you install with the anthropic extra:
```bash
pip install -e ".[anthropic]"
export LLM_PROVIDER=anthropic  # Optional, this is the default
export ANTHROPIC_API_KEY=your-key
```

**To switch to a different provider:**

```bash
# For OpenAI
pip install -e ".[openai]"
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-key

# For Ollama (local)
pip install -e ".[ollama]"
export LLM_PROVIDER=ollama
# No API key needed!

# For Azure OpenAI
pip install -e ".[azure]"
export LLM_PROVIDER=azure
export AZURE_OPENAI_API_KEY=your-key
export AZURE_OPENAI_ENDPOINT=your-endpoint
export AZURE_OPENAI_DEPLOYMENT=your-deployment
```

## [0.1.0] - 2026-02-22

### Added
- Initial release of DuckDB Eurostat MCP Server
- Natural language to SQL translation using Anthropic Claude
- 5 MCP tools: query_eurostat, list_dataflows, get_dataflow_structure, execute_sql, list_providers
- DuckDB Eurostat extension integration
- Comprehensive test suite
- Development workflows
- Documentation and examples
