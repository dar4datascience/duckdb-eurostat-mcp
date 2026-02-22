---
description: Guide to creating an MCP server with flexible LLM provider support
---

# Creating an MCP Server with Flexible LLM Support

This workflow guides you through creating an MCP server that allows users to choose any LLM provider they have access to, following the pattern used in this DuckDB Eurostat MCP server.

## Why Flexible LLM Support?

**Benefits:**
- **User Choice**: Let users pick their preferred LLM (Anthropic, OpenAI, local models, etc.)
- **Privacy**: Support local LLMs like Ollama for sensitive data
- **Cost Control**: Users can choose free local models or pay-per-use APIs
- **Enterprise Ready**: Support Azure OpenAI for compliance requirements
- **Future-Proof**: Easy to add new LLM providers as they emerge

## Architecture Pattern

The flexible LLM pattern uses:
1. **Abstract Base Class** - Defines the LLM provider interface
2. **Concrete Providers** - Implementations for each LLM service
3. **Factory Pattern** - Easy provider creation
4. **Dependency Injection** - Server accepts any provider implementation

## Step-by-Step Implementation

### Step 1: Create the Provider Abstraction

Create `src/your_mcp_server/llm_providers.py`:

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass
```

**Key Points:**
- Use ABC (Abstract Base Class) for interface definition
- `generate()` is the core method all providers must implement
- `is_configured()` allows graceful handling of missing API keys
- Use `async` for all LLM calls (they're I/O bound)

### Step 2: Implement Provider Classes

**Anthropic Provider:**
```python
class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("Anthropic provider not configured")
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text.strip()
```

**OpenAI Provider:**
```python
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("OpenAI provider not configured")
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
```

**Ollama Provider (Local):**
```python
class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            base_url=f"{base_url}/v1",
            api_key="ollama",  # Ollama doesn't need a real key
        )
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
```

### Step 3: Create a Provider Factory

```python
def create_provider(provider_type: str = "anthropic", **kwargs) -> LLMProvider:
    """Factory function to create LLM providers."""
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "azure": AzureOpenAIProvider,
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Available: {', '.join(providers.keys())}"
        )
    
    return provider_class(**kwargs)
```

### Step 4: Update Your MCP Server

**Modify your server to accept providers:**

```python
class YourMCPServer:
    def __init__(
        self, 
        llm_provider: LLMProvider | None = None, 
        provider_type: str | None = None
    ):
        self.server = Server("your-mcp-server")
        
        # Determine provider from environment or parameter
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        # Initialize with specified provider
        if llm_provider:
            self.llm_provider = llm_provider
        else:
            self.llm_provider = create_provider(provider_type)
        
        logger.info(f"Initialized with {provider_type} LLM provider")
        self._setup_handlers()
```

**Use the provider in your tools:**

```python
async def _handle_your_tool(self, arguments: dict):
    if not self.llm_provider.is_configured():
        raise ValueError("LLM provider not configured")
    
    system_prompt = "Your system instructions here..."
    user_message = f"Process this: {arguments['query']}"
    
    response = await self.llm_provider.generate(system_prompt, user_message)
    return [TextContent(type="text", text=response)]
```

### Step 5: Update Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "mcp>=0.9.0",
    # Core dependencies only
]

[project.optional-dependencies]
anthropic = [
    "anthropic>=0.18.0",
]
openai = [
    "openai>=1.0.0",
]
ollama = [
    "openai>=1.0.0",  # Uses OpenAI-compatible API
]
azure = [
    "openai>=1.0.0",
]
all-providers = [
    "anthropic>=0.18.0",
    "openai>=1.0.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "anthropic>=0.18.0",
    "openai>=1.0.0",
]
```

**Installation:**
```bash
# Install with specific provider
pip install -e ".[anthropic]"
pip install -e ".[openai]"
pip install -e ".[ollama]"

# Install all providers
pip install -e ".[all-providers]"
```

### Step 6: Create Environment Configuration

**`.env.example`:**
```bash
# Choose your LLM provider
LLM_PROVIDER=anthropic  # Options: anthropic, openai, ollama, azure

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-key

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment

# Ollama (local) - no API key needed!
```

### Step 7: Write Tests with Mock Providers

```python
class MockLLMProvider(LLMProvider):
    """Mock provider for testing."""
    
    def __init__(self, response: str = "test response"):
        self.response = response
    
    def is_configured(self) -> bool:
        return True
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        return self.response

# Use in tests
@pytest.fixture
def server():
    mock_provider = MockLLMProvider(response="SELECT * FROM test")
    return YourMCPServer(llm_provider=mock_provider)
```

### Step 8: Document Provider Configuration

Create `docs/LLM_PROVIDERS.md` with:
- Installation instructions for each provider
- Environment variable setup
- Claude Desktop configuration examples
- Provider comparison table
- Troubleshooting guide

**Example Claude Desktop Config:**
```json
{
  "mcpServers": {
    "your-server": {
      "command": "python",
      "args": ["-m", "your_mcp_server.server"],
      "env": {
        "LLM_PROVIDER": "anthropic",
        "ANTHROPIC_API_KEY": "your-key"
      }
    }
  }
}
```

### Step 9: Update README

Add sections for:
- **Flexible LLM Support** in features
- **Prerequisites** listing provider options
- **Installation** with provider-specific commands
- **Configuration** examples for each provider

## Best Practices

### 1. Lazy Import Dependencies

```python
def __init__(self, api_key: str | None = None):
    self.api_key = api_key
    self.client = None
    
    if self.api_key:
        try:
            from anthropic import Anthropic  # Import only when needed
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            logger.warning("anthropic package not installed")
```

**Why?** Users only install the providers they need.

### 2. Graceful Degradation

```python
def is_configured(self) -> bool:
    return self.client is not None

async def generate(self, system_prompt: str, user_message: str) -> str:
    if not self.is_configured():
        raise ValueError(
            "Provider not configured. Please set the appropriate API key."
        )
    # ... rest of implementation
```

**Why?** Clear error messages help users fix configuration issues.

### 3. Environment Variable Defaults

```python
provider_type = os.getenv("LLM_PROVIDER", "anthropic").lower()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

**Why?** Users can configure via environment without code changes.

### 4. Provider-Specific Error Handling

```python
try:
    response = await self.provider.generate(system, user)
except Exception as e:
    logger.error(f"LLM API call failed: {e}")
    raise Exception(f"Failed to generate response: {str(e)}")
```

**Why?** Different providers have different error types.

### 5. Consistent Interface

All providers must implement the same interface:
- `generate(system_prompt, user_message) -> str`
- `is_configured() -> bool`

**Why?** Server code doesn't need to know which provider is being used.

## Testing Strategy

### Unit Tests for Each Provider

```python
class TestAnthropicProvider:
    @pytest.fixture
    def provider(self):
        with patch("your_module.Anthropic"):
            return AnthropicProvider(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate(self, provider):
        # Test implementation
        pass
```

### Integration Tests with Mock Provider

```python
@pytest.mark.asyncio
async def test_server_with_custom_provider():
    mock_provider = MockLLMProvider(response="test")
    server = YourMCPServer(llm_provider=mock_provider)
    result = await server._handle_tool({"query": "test"})
    assert "test" in result[0].text
```

## Common Pitfalls to Avoid

### ❌ Don't: Hard-code a specific provider
```python
from anthropic import Anthropic
self.client = Anthropic(api_key=api_key)
```

### ✅ Do: Use dependency injection
```python
def __init__(self, llm_provider: LLMProvider):
    self.llm_provider = llm_provider
```

### ❌ Don't: Make all providers required dependencies
```toml
dependencies = [
    "anthropic>=0.18.0",
    "openai>=1.0.0",
]
```

### ✅ Do: Use optional dependencies
```toml
[project.optional-dependencies]
anthropic = ["anthropic>=0.18.0"]
openai = ["openai>=1.0.0"]
```

### ❌ Don't: Assume a provider is configured
```python
response = await self.provider.generate(prompt, message)
```

### ✅ Do: Check configuration first
```python
if not self.provider.is_configured():
    raise ValueError("Provider not configured")
response = await self.provider.generate(prompt, message)
```

## Example: Complete Minimal Implementation

See the DuckDB Eurostat MCP server for a complete reference implementation:
- `src/duckdb_eurostat_mcp/llm_providers.py` - Provider implementations
- `src/duckdb_eurostat_mcp/query_translator.py` - Provider usage
- `src/duckdb_eurostat_mcp/server.py` - Server integration
- `tests/test_llm_providers.py` - Provider tests
- `docs/LLM_PROVIDERS.md` - User documentation

## Quick Start Checklist

- [ ] Create `llm_providers.py` with abstract base class
- [ ] Implement at least 2 providers (e.g., Anthropic + Ollama)
- [ ] Add factory function for provider creation
- [ ] Update server to accept provider via dependency injection
- [ ] Make LLM packages optional dependencies in `pyproject.toml`
- [ ] Add `LLM_PROVIDER` environment variable support
- [ ] Update `.env.example` with all provider configurations
- [ ] Write tests with mock providers
- [ ] Document provider setup in README
- [ ] Create detailed provider guide in `docs/`
- [ ] Test with at least 2 different providers

## Benefits of This Pattern

1. **User Freedom**: Users choose their preferred LLM
2. **Cost Flexibility**: Free local models or paid APIs
3. **Privacy Control**: Local execution option (Ollama)
4. **Enterprise Ready**: Azure support for compliance
5. **Easy Testing**: Mock providers for unit tests
6. **Future-Proof**: Add new providers without changing server code
7. **Minimal Dependencies**: Users only install what they need

## Next Steps

After implementing flexible LLM support:
1. Test with multiple providers to ensure consistency
2. Document provider-specific quirks or limitations
3. Consider adding provider-specific optimizations
4. Monitor for new LLM providers to add support for
5. Gather user feedback on provider preferences
