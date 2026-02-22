# LLM Provider Configuration Guide

The DuckDB Eurostat MCP server supports multiple LLM providers for natural language to SQL translation. This flexibility allows you to choose the provider that best fits your needs, whether it's cloud-based or local.

## Supported Providers

- **Anthropic Claude** (default) - High-quality translation with Claude 3.5 Sonnet
- **OpenAI GPT** - GPT-4 and other OpenAI models
- **Ollama** - Local LLM execution (privacy-focused, no API costs)
- **Azure OpenAI** - Enterprise Azure-hosted OpenAI models

## Installation

### Base Installation

```bash
pip install -e .
```

### Install with Specific Provider

```bash
# Anthropic (default)
pip install -e ".[anthropic]"

# OpenAI
pip install -e ".[openai]"

# Azure OpenAI
pip install -e ".[azure]"

# Ollama (uses OpenAI-compatible API)
pip install -e ".[ollama]"

# All providers
pip install -e ".[all-providers]"

# Development (includes all providers)
pip install -e ".[dev]"
```

## Configuration

### 1. Anthropic Claude (Default)

**Environment Variables:**
```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-api-key-here
```

**Claude Desktop Config:**
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

**Get API Key:** https://console.anthropic.com/

**Models Used:** `claude-3-5-sonnet-20241022`

### 2. OpenAI GPT

**Environment Variables:**
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
```

**Claude Desktop Config:**
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

**Get API Key:** https://platform.openai.com/api-keys

**Models Used:** `gpt-4o` (default)

### 3. Ollama (Local)

**Prerequisites:**
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama3.1`
3. Ensure Ollama is running: `ollama serve`

**Environment Variables:**
```bash
export LLM_PROVIDER=ollama
# No API key needed!
```

**Claude Desktop Config:**
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

**Models Used:** `llama3.1` (default)

**Benefits:**
- No API costs
- Complete privacy (runs locally)
- No internet required after model download
- Fast inference on modern hardware

### 4. Azure OpenAI

**Environment Variables:**
```bash
export LLM_PROVIDER=azure
export AZURE_OPENAI_API_KEY=your-api-key-here
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "duckdb-eurostat": {
      "command": "python",
      "args": ["-m", "duckdb_eurostat_mcp.server"],
      "env": {
        "LLM_PROVIDER": "azure",
        "AZURE_OPENAI_API_KEY": "your-api-key-here",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT": "your-deployment-name"
      }
    }
  }
}
```

**Setup:** Follow Azure OpenAI service documentation

## Programmatic Configuration

You can also configure the provider programmatically:

```python
from duckdb_eurostat_mcp.server import EurostatMCPServer
from duckdb_eurostat_mcp.llm_providers import create_provider

# Option 1: Use provider type
server = EurostatMCPServer(provider_type="openai")

# Option 2: Create custom provider
provider = create_provider("anthropic", model="claude-3-5-sonnet-20241022")
server = EurostatMCPServer(llm_provider=provider)

# Option 3: Custom provider with specific settings
from duckdb_eurostat_mcp.llm_providers import OllamaProvider
provider = OllamaProvider(model="llama3.1", base_url="http://localhost:11434")
server = EurostatMCPServer(llm_provider=provider)
```

## Provider Comparison

| Provider | Cost | Speed | Quality | Privacy | Internet Required |
|----------|------|-------|---------|---------|-------------------|
| Anthropic | $$ | Fast | Excellent | Cloud | Yes |
| OpenAI | $$ | Fast | Excellent | Cloud | Yes |
| Azure OpenAI | $$$ | Fast | Excellent | Enterprise | Yes |
| Ollama | Free | Medium-Fast* | Good | Complete | No** |

\* Depends on hardware  
\** Only for initial model download

## Choosing a Provider

**Use Anthropic if:**
- You want the best SQL translation quality (default)
- You're okay with cloud-based processing
- You have an Anthropic API key

**Use OpenAI if:**
- You prefer OpenAI's models
- You already have OpenAI credits
- You want GPT-4 level performance

**Use Ollama if:**
- Privacy is a top concern
- You want to avoid API costs
- You have decent local hardware (8GB+ RAM recommended)
- You don't need internet connectivity

**Use Azure OpenAI if:**
- You're in an enterprise environment
- You need compliance with specific data residency requirements
- You already use Azure services

## Troubleshooting

### Provider Not Configured

**Error:** `LLM provider not configured`

**Solution:** Ensure you've set the appropriate environment variables for your chosen provider.

### Missing Dependencies

**Error:** `anthropic package not installed` or `openai package not installed`

**Solution:** Install the provider-specific dependencies:
```bash
pip install -e ".[anthropic]"  # or openai, azure, ollama
```

### Ollama Connection Failed

**Error:** `Ollama API error: Connection refused`

**Solution:** 
1. Check if Ollama is running: `ollama serve`
2. Verify the model is downloaded: `ollama pull llama3.1`
3. Check the base URL is correct (default: `http://localhost:11434`)

### Azure Configuration Issues

**Error:** `Azure OpenAI provider not configured`

**Solution:** Ensure all three environment variables are set:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`

## Advanced: Custom Provider Implementation

You can implement your own LLM provider by extending the `LLMProvider` base class:

```python
from duckdb_eurostat_mcp.llm_providers import LLMProvider

class CustomProvider(LLMProvider):
    def __init__(self, **kwargs):
        # Your initialization
        pass
    
    def is_configured(self) -> bool:
        # Check if provider is ready
        return True
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        # Your LLM call implementation
        return "SELECT * FROM ..."

# Use it
server = EurostatMCPServer(llm_provider=CustomProvider())
```

## Performance Tips

1. **Anthropic/OpenAI**: Use for best quality, especially for complex queries
2. **Ollama**: 
   - Use larger models (llama3.1:70b) for better quality if you have the hardware
   - Use smaller models (llama3.1:8b) for faster responses
3. **All providers**: The system prompt is optimized for SQL generation, so results should be consistent across providers
