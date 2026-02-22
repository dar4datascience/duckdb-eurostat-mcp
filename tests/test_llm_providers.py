"""Tests for LLM provider implementations."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from duckdb_eurostat_mcp.llm_providers import (
    LLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    OllamaProvider,
    AzureOpenAIProvider,
    create_provider,
)


class TestProviderFactory:
    def test_create_anthropic_provider(self):
        provider = create_provider("anthropic", api_key="test-key")
        assert isinstance(provider, AnthropicProvider)

    def test_create_openai_provider(self):
        provider = create_provider("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

    def test_create_ollama_provider(self):
        provider = create_provider("ollama")
        assert isinstance(provider, OllamaProvider)

    def test_create_azure_provider(self):
        provider = create_provider(
            "azure",
            api_key="test-key",
            endpoint="https://test.openai.azure.com/",
            deployment="test-deployment",
        )
        assert isinstance(provider, AzureOpenAIProvider)

    def test_create_unknown_provider_raises_error(self):
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_provider("unknown")


class TestAnthropicProvider:
    @pytest.fixture
    def provider_no_key(self):
        return AnthropicProvider(api_key=None)

    @pytest.fixture
    def provider_with_key(self):
        with patch("duckdb_eurostat_mcp.llm_providers.Anthropic"):
            return AnthropicProvider(api_key="test-key")

    def test_initialization_without_key(self, provider_no_key):
        assert not provider_no_key.is_configured()

    def test_initialization_with_key(self, provider_with_key):
        assert provider_with_key.is_configured()

    @pytest.mark.asyncio
    async def test_generate_without_key_raises_error(self, provider_no_key):
        with pytest.raises(ValueError, match="Anthropic provider not configured"):
            await provider_no_key.generate("system", "user")

    @pytest.mark.asyncio
    async def test_generate_with_key(self, provider_with_key):
        mock_response = Mock()
        mock_response.content = [Mock(text="SELECT * FROM test")]
        provider_with_key.client.messages.create = Mock(return_value=mock_response)

        result = await provider_with_key.generate("system prompt", "user message")
        assert result == "SELECT * FROM test"


class TestOpenAIProvider:
    @pytest.fixture
    def provider_no_key(self):
        return OpenAIProvider(api_key=None)

    @pytest.fixture
    def provider_with_key(self):
        with patch("duckdb_eurostat_mcp.llm_providers.AsyncOpenAI"):
            return OpenAIProvider(api_key="test-key")

    def test_initialization_without_key(self, provider_no_key):
        assert not provider_no_key.is_configured()

    def test_initialization_with_key(self, provider_with_key):
        assert provider_with_key.is_configured()

    @pytest.mark.asyncio
    async def test_generate_without_key_raises_error(self, provider_no_key):
        with pytest.raises(ValueError, match="OpenAI provider not configured"):
            await provider_no_key.generate("system", "user")

    @pytest.mark.asyncio
    async def test_generate_with_key(self, provider_with_key):
        mock_choice = Mock()
        mock_choice.message.content = "SELECT * FROM test"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        provider_with_key.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await provider_with_key.generate("system prompt", "user message")
        assert result == "SELECT * FROM test"


class TestOllamaProvider:
    @pytest.fixture
    def provider(self):
        with patch("duckdb_eurostat_mcp.llm_providers.AsyncOpenAI"):
            return OllamaProvider(model="llama3.1")

    def test_initialization(self, provider):
        assert provider.is_configured()
        assert provider.model == "llama3.1"

    @pytest.mark.asyncio
    async def test_generate(self, provider):
        mock_choice = Mock()
        mock_choice.message.content = "SELECT * FROM test"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        provider.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await provider.generate("system prompt", "user message")
        assert result == "SELECT * FROM test"


class TestAzureOpenAIProvider:
    @pytest.fixture
    def provider_no_config(self):
        return AzureOpenAIProvider(api_key=None, endpoint=None, deployment=None)

    @pytest.fixture
    def provider_with_config(self):
        with patch("duckdb_eurostat_mcp.llm_providers.AsyncAzureOpenAI"):
            return AzureOpenAIProvider(
                api_key="test-key",
                endpoint="https://test.openai.azure.com/",
                deployment="test-deployment",
            )

    def test_initialization_without_config(self, provider_no_config):
        assert not provider_no_config.is_configured()

    def test_initialization_with_config(self, provider_with_config):
        assert provider_with_config.is_configured()

    @pytest.mark.asyncio
    async def test_generate_without_config_raises_error(self, provider_no_config):
        with pytest.raises(ValueError, match="Azure OpenAI provider not configured"):
            await provider_no_config.generate("system", "user")

    @pytest.mark.asyncio
    async def test_generate_with_config(self, provider_with_config):
        mock_choice = Mock()
        mock_choice.message.content = "SELECT * FROM test"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        provider_with_config.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await provider_with_config.generate("system prompt", "user message")
        assert result == "SELECT * FROM test"
