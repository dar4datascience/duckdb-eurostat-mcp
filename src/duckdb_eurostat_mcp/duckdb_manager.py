"""DuckDB connection and query management."""

import logging
from typing import Any

import duckdb

logger = logging.getLogger(__name__)


class DuckDBManager:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._initialize_extension()

    def _initialize_extension(self) -> None:
        try:
            self.conn.execute("INSTALL eurostat FROM community")
            self.conn.execute("LOAD eurostat")
            logger.info("DuckDB Eurostat extension loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Eurostat extension: {e}")
            raise

    def execute_query(self, sql: str, limit: int | None = None) -> str:
        try:
            if limit and "LIMIT" not in sql.upper():
                sql = f"{sql.rstrip(';')} LIMIT {limit}"
            
            result = self.conn.execute(sql).fetchdf()
            
            if result.empty:
                return "No results found."
            
            return result.to_markdown(index=False)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise Exception(f"Query execution failed: {str(e)}")

    def get_schema_info(self, provider_id: str, dataflow_id: str) -> dict[str, Any]:
        sql = f"""
        SELECT dimension, concept 
        FROM EUROSTAT_DataStructure('{provider_id}', '{dataflow_id}', language := 'en')
        WHERE position > 0
        ORDER BY position
        """
        
        result = self.conn.execute(sql).fetchdf()
        
        return {
            "dimensions": result["dimension"].tolist(),
            "concepts": result["concept"].tolist(),
        }

    def search_dataflows(self, search_term: str, limit: int = 10) -> list[dict[str, str]]:
        sql = f"""
        SELECT provider_id, dataflow_id, label 
        FROM EUROSTAT_Dataflows(language := 'en')
        WHERE label ILIKE '%{search_term}%'
        LIMIT {limit}
        """
        
        result = self.conn.execute(sql).fetchdf()
        
        return result.to_dict("records")

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            logger.info("DuckDB connection closed")

    def __enter__(self) -> "DuckDBManager":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
