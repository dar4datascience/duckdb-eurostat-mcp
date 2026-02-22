"""Tests for MCP server functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from duckdb_eurostat_mcp.server import EurostatMCPServer
from duckdb_eurostat_mcp.llm_providers import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    def __init__(self):
        pass
    
    def is_configured(self) -> bool:
        return True
    
    async def generate(self, system_prompt: str, user_message: str) -> str:
        return "SELECT * FROM EUROSTAT_Endpoints() LIMIT 1"


class TestEurostatMCPServer:
    @pytest.fixture
    def server(self):
        mock_provider = MockLLMProvider()
        return EurostatMCPServer(llm_provider=mock_provider)

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        tools = await server.server._tool_manager.list_tools()
        
        tool_names = [tool.name for tool in tools]
        assert "query_eurostat" in tool_names
        assert "list_dataflows" in tool_names
        assert "get_dataflow_structure" in tool_names
        assert "execute_sql" in tool_names
        assert "list_providers" in tool_names

    @pytest.mark.asyncio
    async def test_list_providers_tool(self, server):
        result = await server._handle_list_providers({})
        
        assert len(result) > 0
        assert "ESTAT" in result[0].text

    @pytest.mark.asyncio
    async def test_list_dataflows_tool(self, server):
        result = await server._handle_list_dataflows({"limit": 5})
        
        assert len(result) > 0
        assert "dataflow" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_list_dataflows_with_search(self, server):
        result = await server._handle_list_dataflows({
            "search": "population",
            "limit": 5
        })
        
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_dataflow_structure_tool(self, server):
        result = await server._handle_get_dataflow_structure({
            "provider_id": "ESTAT",
            "dataflow_id": "DEMO_R_D2JAN"
        })
        
        assert len(result) > 0
        assert "dimension" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_execute_sql_tool(self, server):
        result = await server._handle_execute_sql({
            "sql": "SELECT provider_id FROM EUROSTAT_Endpoints() LIMIT 3",
            "limit": 3
        })
        
        assert len(result) > 0
        assert "provider_id" in result[0].text

    @pytest.mark.asyncio
    @patch("duckdb_eurostat_mcp.server.QueryTranslator.translate")
    async def test_query_eurostat_tool(self, mock_translate, server):
        mock_translate.return_value = "SELECT * FROM EUROSTAT_Endpoints() LIMIT 1"
        
        result = await server._handle_query_eurostat({
            "query": "list providers",
            "limit": 1
        })
        
        assert len(result) > 0
        assert "Natural Language Query" in result[0].text
        assert "Generated SQL" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        result = await server._handle_execute_sql({
            "sql": "SELECT * FROM INVALID_TABLE"
        })
        
        assert len(result) > 0
        assert "Error" in result[0].text
