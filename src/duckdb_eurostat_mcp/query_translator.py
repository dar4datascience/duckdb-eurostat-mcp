"""Natural language to SQL query translation using configurable LLM providers."""

import logging
import os
from typing import Any

from .llm_providers import LLMProvider, create_provider

logger = logging.getLogger(__name__)


class QueryTranslator:
    def __init__(self, provider: LLMProvider | None = None, provider_type: str = "anthropic", **provider_kwargs: Any) -> None:
        """Initialize the query translator with a configurable LLM provider.
        
        Args:
            provider: Pre-configured LLM provider instance. If None, creates one based on provider_type.
            provider_type: Type of provider to create ('anthropic', 'openai', 'ollama', 'azure').
            **provider_kwargs: Additional arguments passed to the provider constructor.
        """
        if provider:
            self.provider = provider
        else:
            self.provider = create_provider(provider_type, **provider_kwargs)
        
        if not self.provider.is_configured():
            logger.warning(
                f"{provider_type.title()} provider not configured. Natural language queries will not work. "
                f"Please configure the appropriate API key or settings."
            )

    async def translate(self, natural_query: str, db_manager: Any) -> str:
        """Translate a natural language query to SQL.
        
        Args:
            natural_query: Natural language query to translate
            db_manager: Database manager instance (for context if needed)
            
        Returns:
            SQL query string
        """
        if not self.provider.is_configured():
            raise ValueError(
                "LLM provider not configured. Cannot translate natural language queries. "
                "Please set the appropriate API key or configuration."
            )

        system_prompt = self._build_system_prompt()
        user_message = f"Translate this query to SQL: {natural_query}"
        
        try:
            response = await self.provider.generate(system_prompt, user_message)
            sql_query = self._clean_sql_response(response)
            
            logger.info(f"Translated query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise Exception(f"Failed to translate query: {str(e)}")
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean SQL response by removing markdown formatting."""
        sql_query = response.strip()
        
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.replace("```", "").strip()
        
        return sql_query

    def _build_system_prompt(self) -> str:
        return """You are a SQL expert specializing in the DuckDB Eurostat extension.

The DuckDB Eurostat extension provides these main functions:

1. EUROSTAT_Endpoints() - Lists available providers (ESTAT, ECFIN, EMPL, GROW, TAXUD)
2. EUROSTAT_Dataflows([providers], [dataflows], language) - Lists available datasets
3. EUROSTAT_DataStructure(provider_id, dataflow_id, language) - Shows dataset structure
4. EUROSTAT_Read(provider_id, dataflow_id, [filters]) - Reads actual data

Common dataflows:
- DEMO_R_D2JAN: Population by age, sex, and NUTS-2 region
- UNE_RT_A: Unemployment rates
- NAMA_10_GDP: GDP and main components
- PRC_HICP_MIDX: HICP - Monthly index

When translating queries:
1. Use EUROSTAT_Read() to fetch actual data
2. Apply WHERE filters for dimensions (geo, time_period, etc.)
3. The extension supports pushdown filters: WHERE geo = 'DE' or WHERE geo IN ('DE', 'FR')
4. Time filters: WHERE time_period >= '2020' AND time_period <= '2023'
5. Always specify provider_id (usually 'ESTAT') and dataflow_id
6. Use language := 'en' for English labels

Examples:
- "Population of Germany in 2020" → 
  SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') 
  WHERE geo = 'DE' AND time_period = '2020'

- "Unemployment rates for EU countries" →
  SELECT * FROM EUROSTAT_Read('ESTAT', 'UNE_RT_A') 
  WHERE geo_level = 'country'

Return ONLY the SQL query, no explanations or markdown formatting unless specifically requested."""

    def translate_sync(self, natural_query: str, db_manager: Any) -> str:
        import asyncio
        return asyncio.run(self.translate(natural_query, db_manager))
