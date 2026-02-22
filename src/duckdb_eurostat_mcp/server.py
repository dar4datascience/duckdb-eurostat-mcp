"""Main MCP server implementation for DuckDB Eurostat."""

import asyncio
import logging
import os
from typing import Any

import duckdb
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .query_translator import QueryTranslator
from .duckdb_manager import DuckDBManager
from .llm_providers import LLMProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EurostatMCPServer:
    def __init__(self, llm_provider: LLMProvider | None = None, provider_type: str | None = None) -> None:
        """Initialize the Eurostat MCP server.
        
        Args:
            llm_provider: Pre-configured LLM provider instance. If None, creates one based on provider_type.
            provider_type: Type of LLM provider to use. If None, reads from LLM_PROVIDER env var (default: 'anthropic').
        """
        self.server = Server("duckdb-eurostat-mcp")
        self.db_manager = DuckDBManager()
        
        # Determine provider type from environment or parameter
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        # Initialize query translator with the specified provider
        if llm_provider:
            self.query_translator = QueryTranslator(provider=llm_provider)
        else:
            self.query_translator = QueryTranslator(provider_type=provider_type)
        
        logger.info(f"Initialized MCP server with {provider_type} LLM provider")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="query_eurostat",
                    description=(
                        "Query Eurostat data using natural language. "
                        "The query will be translated to SQL and executed against the DuckDB Eurostat extension. "
                        "Examples: 'Get population data for Germany in 2020', "
                        "'Show unemployment rates for EU countries', "
                        "'List available datasets about GDP'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about Eurostat data",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of rows to return (default: 100)",
                                "default": 100,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="list_dataflows",
                    description=(
                        "List available Eurostat dataflows/datasets. "
                        "You can optionally filter by provider or search for specific keywords."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Provider ID (e.g., 'ESTAT', 'ECFIN'). Leave empty for all providers.",
                            },
                            "search": {
                                "type": "string",
                                "description": "Search term to filter dataflows by label",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of dataflows to return (default: 50)",
                                "default": 50,
                            },
                        },
                    },
                ),
                Tool(
                    name="get_dataflow_structure",
                    description=(
                        "Get the structure (dimensions and concepts) of a specific Eurostat dataflow. "
                        "This helps understand what data is available and how to query it."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider_id": {
                                "type": "string",
                                "description": "Provider ID (e.g., 'ESTAT')",
                            },
                            "dataflow_id": {
                                "type": "string",
                                "description": "Dataflow ID (e.g., 'DEMO_R_D2JAN')",
                            },
                        },
                        "required": ["provider_id", "dataflow_id"],
                    },
                ),
                Tool(
                    name="execute_sql",
                    description=(
                        "Execute a raw SQL query against the DuckDB Eurostat database. "
                        "Use this for advanced queries or when you need precise control. "
                        "The DuckDB Eurostat extension provides functions like EUROSTAT_Read, "
                        "EUROSTAT_Dataflows, EUROSTAT_DataStructure, etc."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "SQL query to execute",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of rows to return (default: 100)",
                                "default": 100,
                            },
                        },
                        "required": ["sql"],
                    },
                ),
                Tool(
                    name="list_providers",
                    description="List all available Eurostat API endpoints/providers",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            try:
                if name == "query_eurostat":
                    return await self._handle_query_eurostat(arguments)
                elif name == "list_dataflows":
                    return await self._handle_list_dataflows(arguments)
                elif name == "get_dataflow_structure":
                    return await self._handle_get_dataflow_structure(arguments)
                elif name == "execute_sql":
                    return await self._handle_execute_sql(arguments)
                elif name == "list_providers":
                    return await self._handle_list_providers(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_query_eurostat(self, arguments: dict[str, Any]) -> list[TextContent]:
        query = arguments["query"]
        limit = arguments.get("limit", 100)

        sql_query = await self.query_translator.translate(query, self.db_manager)
        
        result = self.db_manager.execute_query(sql_query, limit)
        
        response = f"**Natural Language Query:** {query}\n\n"
        response += f"**Generated SQL:**\n```sql\n{sql_query}\n```\n\n"
        response += f"**Results:**\n{result}"
        
        return [TextContent(type="text", text=response)]

    async def _handle_list_dataflows(self, arguments: dict[str, Any]) -> list[TextContent]:
        provider = arguments.get("provider")
        search = arguments.get("search")
        limit = arguments.get("limit", 50)

        sql = "SELECT provider_id, dataflow_id, label, version FROM EUROSTAT_Dataflows("
        params = []
        
        if provider:
            params.append(f"providers = ['{provider}']")
        
        params.append("language := 'en'")
        sql += ", ".join(params) + ")"
        
        if search:
            sql += f" WHERE label ILIKE '%{search}%'"
        
        sql += f" LIMIT {limit}"
        
        result = self.db_manager.execute_query(sql)
        
        return [TextContent(type="text", text=f"**Available Dataflows:**\n{result}")]

    async def _handle_get_dataflow_structure(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        provider_id = arguments["provider_id"]
        dataflow_id = arguments["dataflow_id"]

        sql = f"""
        SELECT position, dimension, concept 
        FROM EUROSTAT_DataStructure('{provider_id}', '{dataflow_id}', language := 'en')
        ORDER BY position
        """
        
        result = self.db_manager.execute_query(sql)
        
        response = f"**Dataflow Structure for {provider_id}/{dataflow_id}:**\n{result}"
        
        return [TextContent(type="text", text=response)]

    async def _handle_execute_sql(self, arguments: dict[str, Any]) -> list[TextContent]:
        sql = arguments["sql"]
        limit = arguments.get("limit", 100)

        result = self.db_manager.execute_query(sql, limit)
        
        return [TextContent(type="text", text=f"**SQL Query Results:**\n{result}")]

    async def _handle_list_providers(self, arguments: dict[str, Any]) -> list[TextContent]:
        sql = "SELECT provider_id, organization, description FROM EUROSTAT_Endpoints()"
        
        result = self.db_manager.execute_query(sql)
        
        return [TextContent(type="text", text=f"**Available Providers:**\n{result}")]


async def main() -> None:
    logger.info("Starting DuckDB Eurostat MCP Server")
    server_instance = EurostatMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options(),
        )


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
