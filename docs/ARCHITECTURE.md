# Architecture Overview

## Flexible LLM Provider Pattern

This MCP server implements a flexible architecture that allows users to choose any LLM provider they have access to.

### Design Principles

1. **Provider Agnostic**: Server logic doesn't depend on specific LLM implementations
2. **Dependency Injection**: Providers are injected rather than hard-coded
3. **Optional Dependencies**: Users only install the LLM packages they need
4. **Graceful Degradation**: Clear error messages when providers aren't configured
5. **Testability**: Easy to mock providers for testing

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Server                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              EurostatMCPServer                        │  │
│  │  - Accepts LLMProvider via constructor                │  │
│  │  - Reads LLM_PROVIDER env var                         │  │
│  │  - Delegates LLM calls to provider                    │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            QueryTranslator                            │  │
│  │  - Uses LLMProvider interface                         │  │
│  │  - Builds system prompts                              │  │
│  │  - Cleans LLM responses                               │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │      LLMProvider (ABC)       │
        │  - generate()                │
        │  - is_configured()           │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────┐            ┌───────────────┐
│  Anthropic    │            │   OpenAI      │
│  Provider     │            │   Provider    │
└───────────────┘            └───────────────┘
        │                             │
        ▼                             ▼
┌───────────────┐            ┌───────────────┐
│   Ollama      │            │  Azure OpenAI │
│   Provider    │            │   Provider    │
└───────────────┘            └───────────────┘
```

### Provider Interface

All LLM providers implement this interface:

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass
```

### Provider Implementations

#### AnthropicProvider
- **Model**: claude-3-5-sonnet-20241022
- **API**: Anthropic Messages API
- **Config**: ANTHROPIC_API_KEY
- **Best for**: High-quality SQL generation

#### OpenAIProvider
- **Model**: gpt-4o (default)
- **API**: OpenAI Chat Completions API
- **Config**: OPENAI_API_KEY
- **Best for**: Users with OpenAI credits

#### OllamaProvider
- **Model**: llama3.1 (default, configurable)
- **API**: OpenAI-compatible local API
- **Config**: No API key needed
- **Best for**: Privacy, offline use, no API costs

#### AzureOpenAIProvider
- **Model**: User's deployment
- **API**: Azure OpenAI Service
- **Config**: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
- **Best for**: Enterprise compliance

### Configuration Flow

```
1. User sets environment variables:
   ├─ LLM_PROVIDER=anthropic (or openai, ollama, azure)
   └─ Provider-specific API keys

2. Server initialization:
   ├─ Read LLM_PROVIDER env var (default: anthropic)
   ├─ Call create_provider(provider_type)
   └─ Inject provider into QueryTranslator

3. Query processing:
   ├─ Check provider.is_configured()
   ├─ Call provider.generate(system_prompt, user_message)
   └─ Return response to user
```

### Dependency Management

```toml
[project]
dependencies = [
    "mcp>=0.9.0",
    "duckdb>=1.0.0",
    # No LLM packages in core dependencies
]

[project.optional-dependencies]
anthropic = ["anthropic>=0.18.0"]
openai = ["openai>=1.0.0"]
ollama = ["openai>=1.0.0"]  # Uses OpenAI-compatible API
azure = ["openai>=1.0.0"]
all-providers = ["anthropic>=0.18.0", "openai>=1.0.0"]
```

**Installation examples:**
```bash
pip install -e ".[anthropic]"     # Only Anthropic
pip install -e ".[openai]"        # Only OpenAI
pip install -e ".[all-providers]" # All providers
```

### Error Handling

```python
# Provider not configured
if not self.provider.is_configured():
    raise ValueError(
        "LLM provider not configured. "
        "Please set the appropriate API key."
    )

# API call failures
try:
    response = await self.provider.generate(system, user)
except Exception as e:
    logger.error(f"LLM API call failed: {e}")
    raise Exception(f"Failed to generate response: {str(e)}")
```

### Testing Strategy

#### Mock Provider Pattern
```python
class MockLLMProvider(LLMProvider):
    def __init__(self, response: str = "test"):
        self.response = response
    
    def is_configured(self) -> bool:
        return True
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        return self.response

# Use in tests
server = EurostatMCPServer(llm_provider=MockLLMProvider())
```

#### Provider-Specific Tests
- Unit tests for each provider implementation
- Integration tests with mock providers
- End-to-end tests with real APIs (optional, CI/CD)

### Extension Points

#### Adding a New Provider

1. Create provider class implementing `LLMProvider`
2. Add to factory function in `create_provider()`
3. Add optional dependency in `pyproject.toml`
4. Document in `docs/LLM_PROVIDERS.md`
5. Add tests in `tests/test_llm_providers.py`

Example:
```python
class CustomProvider(LLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CUSTOM_API_KEY")
        # Initialize your client
    
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        # Your implementation
        pass
```

### Performance Considerations

- **Lazy Loading**: LLM packages imported only when provider is instantiated
- **Async I/O**: All LLM calls are async to avoid blocking
- **Connection Pooling**: Clients reused across requests
- **Error Recovery**: Graceful handling of API failures

### Security Considerations

- **API Keys**: Never hard-coded, always from environment
- **Local Execution**: Ollama option for sensitive data
- **Audit Trail**: All LLM calls logged
- **Rate Limiting**: Handled by provider implementations

### Future Enhancements

Potential additions to the provider pattern:
- **Streaming Support**: Stream LLM responses for long queries
- **Caching**: Cache common query translations
- **Fallback Providers**: Try alternative provider on failure
- **Cost Tracking**: Monitor API usage and costs
- **Custom Models**: Allow users to specify model versions
- **Prompt Templates**: Configurable system prompts per provider

## Data Flow

### Natural Language Query Processing

```
User Query
    │
    ▼
MCP Tool: query_eurostat
    │
    ▼
QueryTranslator
    │
    ├─ Build system prompt (Eurostat SQL expertise)
    ├─ Format user message
    │
    ▼
LLMProvider.generate()
    │
    ├─ Anthropic: Call Claude API
    ├─ OpenAI: Call GPT API
    ├─ Ollama: Call local model
    └─ Azure: Call Azure OpenAI
    │
    ▼
Clean SQL response
    │
    ▼
DuckDBManager.execute_query()
    │
    ▼
Return results to user
```

### Configuration Precedence

1. **Programmatic**: Provider passed to constructor
2. **Environment**: LLM_PROVIDER environment variable
3. **Default**: Anthropic (if configured)

## File Structure

```
src/duckdb_eurostat_mcp/
├── __init__.py
├── server.py              # MCP server with provider injection
├── query_translator.py    # Uses LLMProvider interface
├── duckdb_manager.py      # Database operations
└── llm_providers.py       # Provider implementations
    ├── LLMProvider (ABC)
    ├── AnthropicProvider
    ├── OpenAIProvider
    ├── OllamaProvider
    ├── AzureOpenAIProvider
    └── create_provider()

tests/
├── test_server.py         # Server tests with mock provider
├── test_query_translator.py  # Translator tests
├── test_duckdb_manager.py    # Database tests
└── test_llm_providers.py     # Provider-specific tests

docs/
├── LLM_PROVIDERS.md       # User-facing provider guide
└── ARCHITECTURE.md        # This file

.windsurf/workflows/
└── create-flexible-mcp-server.md  # Development guide
```

## Benefits Summary

| Aspect | Benefit |
|--------|---------|
| **User Choice** | Pick any LLM provider |
| **Privacy** | Local execution with Ollama |
| **Cost** | Free local models or pay-per-use |
| **Testing** | Easy mocking with provider pattern |
| **Maintenance** | Add providers without changing server |
| **Dependencies** | Install only what you need |
| **Enterprise** | Azure support for compliance |
| **Future-Proof** | Easy to add new LLM services |

This architecture makes the MCP server truly flexible and user-centric.
