"""Tests for query translation functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from duckdb_eurostat_mcp.query_translator import QueryTranslator
from duckdb_eurostat_mcp.duckdb_manager import DuckDBManager
from duckdb_eurostat_mcp.llm_providers import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    def __init__(self, configured: bool = True, response: str = "SELECT * FROM test"):
        self.configured = configured
        self.response = response
    
    def is_configured(self) -> bool:
        return self.configured
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.configured:
            raise ValueError("Provider not configured")
        return self.response


class TestQueryTranslator:
    @pytest.fixture
    def translator_no_provider(self):
        mock_provider = MockLLMProvider(configured=False)
        return QueryTranslator(provider=mock_provider)

    @pytest.fixture
    def translator_with_provider(self):
        mock_provider = MockLLMProvider(configured=True)
        return QueryTranslator(provider=mock_provider)

    @pytest.fixture
    def db_manager(self):
        manager = DuckDBManager()
        yield manager
        manager.close()

    def test_initialization_without_provider(self, translator_no_provider):
        assert not translator_no_provider.provider.is_configured()

    def test_initialization_with_provider(self, translator_with_provider):
        assert translator_with_provider.provider.is_configured()

    @pytest.mark.asyncio
    async def test_translate_without_provider_raises_error(self, translator_no_provider, db_manager):
        with pytest.raises(ValueError, match="LLM provider not configured"):
            await translator_no_provider.translate("test query", db_manager)

    @pytest.mark.asyncio
    async def test_translate_with_provider(self, db_manager):
        mock_provider = MockLLMProvider(response="SELECT * FROM EUROSTAT_Endpoints()")
        translator = QueryTranslator(provider=mock_provider)
        
        result = await translator.translate("list providers", db_manager)
        
        assert "SELECT" in result
        assert "EUROSTAT" in result

    @pytest.mark.asyncio
    async def test_translate_strips_markdown(self, db_manager):
        mock_provider = MockLLMProvider(response="```sql\nSELECT * FROM test\n```")
        translator = QueryTranslator(provider=mock_provider)
        
        result = await translator.translate("test", db_manager)
        
        assert result == "SELECT * FROM test"
        assert "```" not in result

    def test_system_prompt_contains_key_info(self, translator_with_provider):
        prompt = translator_with_provider._build_system_prompt()
        
        assert "EUROSTAT_Read" in prompt
        assert "EUROSTAT_Dataflows" in prompt
        assert "DEMO_R_D2JAN" in prompt
        assert "WHERE" in prompt

    @pytest.mark.asyncio
    async def test_translate_with_anthropic_provider_type(self, db_manager):
        with patch("duckdb_eurostat_mcp.llm_providers.Anthropic"):
            translator = QueryTranslator(provider_type="anthropic", api_key="test-key")
            assert translator.provider is not None

    @pytest.mark.asyncio
    async def test_translate_with_openai_provider_type(self, db_manager):
        with patch("duckdb_eurostat_mcp.llm_providers.AsyncOpenAI"):
            translator = QueryTranslator(provider_type="openai", api_key="test-key")
            assert translator.provider is not None

    def test_clean_sql_response_removes_sql_markdown(self, translator_with_provider):
        result = translator_with_provider._clean_sql_response("```sql\nSELECT 1\n```")
        assert result == "SELECT 1"

    def test_clean_sql_response_removes_generic_markdown(self, translator_with_provider):
        result = translator_with_provider._clean_sql_response("```\nSELECT 1\n```")
        assert result == "SELECT 1"

    def test_clean_sql_response_handles_plain_text(self, translator_with_provider):
        result = translator_with_provider._clean_sql_response("SELECT 1")
        assert result == "SELECT 1"
