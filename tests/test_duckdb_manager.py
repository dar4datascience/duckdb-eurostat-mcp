"""Tests for DuckDB manager functionality."""

import pytest
from duckdb_eurostat_mcp.duckdb_manager import DuckDBManager


class TestDuckDBManager:
    @pytest.fixture
    def db_manager(self):
        manager = DuckDBManager()
        yield manager
        manager.close()

    def test_initialization(self, db_manager):
        assert db_manager.conn is not None

    def test_list_providers(self, db_manager):
        result = db_manager.execute_query(
            "SELECT provider_id FROM EUROSTAT_Endpoints()"
        )
        assert "ESTAT" in result
        assert "provider_id" in result

    def test_list_dataflows(self, db_manager):
        result = db_manager.execute_query(
            "SELECT dataflow_id FROM EUROSTAT_Dataflows(language := 'en') LIMIT 5"
        )
        assert "dataflow_id" in result

    def test_get_dataflow_structure(self, db_manager):
        result = db_manager.execute_query(
            "SELECT dimension FROM EUROSTAT_DataStructure('ESTAT', 'DEMO_R_D2JAN', language := 'en')"
        )
        assert "dimension" in result

    def test_read_data_with_limit(self, db_manager):
        result = db_manager.execute_query(
            "SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') WHERE geo = 'DE' LIMIT 5"
        )
        assert result is not None
        assert len(result) > 0

    def test_search_dataflows(self, db_manager):
        results = db_manager.search_dataflows("population", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "dataflow_id" in results[0]

    def test_get_schema_info(self, db_manager):
        schema = db_manager.get_schema_info("ESTAT", "DEMO_R_D2JAN")
        assert "dimensions" in schema
        assert "concepts" in schema
        assert isinstance(schema["dimensions"], list)
        assert len(schema["dimensions"]) > 0

    def test_query_with_filters(self, db_manager):
        result = db_manager.execute_query(
            """
            SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') 
            WHERE geo = 'DE' AND time_period = '2020'
            LIMIT 10
            """
        )
        assert "DE" in result or "No results" in result

    def test_empty_result(self, db_manager):
        result = db_manager.execute_query(
            "SELECT * FROM EUROSTAT_Read('ESTAT', 'DEMO_R_D2JAN') WHERE geo = 'INVALID' LIMIT 1"
        )
        assert "No results found" in result

    def test_invalid_query(self, db_manager):
        with pytest.raises(Exception):
            db_manager.execute_query("SELECT * FROM INVALID_TABLE")
