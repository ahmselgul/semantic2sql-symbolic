"""
Simple dialect testing focusing on dialect differences
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput, SemanticSQLGenerator
from semantic2sql.models import SQLDialect


@pytest.fixture
def generator():
    """Fixture to provide SQL generator instance"""
    return SemanticSQLGenerator()


@pytest.fixture
def test_schema():
    """Fixture to provide test schema"""
    return """
    Table: users
    Columns: id (INT), name (VARCHAR), created_at (TIMESTAMP), age (INT)
    """


class TestDialectSupport:
    """Test key dialect differences with proper pytest patterns"""
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL, 
        SQLDialect.SQLITE,
        SQLDialect.GENERIC
    ])
    def test_basic_functionality_all_dialects(self, generator, test_schema, dialect):
        """Test basic functionality works across all dialects"""
        query_input = QueryInput(
            query="find all users older than 25",
            table_schema=test_schema,
            sql_dialect=dialect
        )
        
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.dialect_used == dialect
        assert result.is_valid is True
        assert result.sql.strip()
        assert "users" in result.sql.lower()
        
        print(f"\n{dialect.value.upper()}: {result.sql}")
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE
    ])
    def test_date_functions_show_differences(self, generator, test_schema, dialect):
        """Test date functions where we expect dialect differences"""
        query_input = QueryInput(
            query="find users created in the last 30 days",
            table_schema=test_schema,
            sql_dialect=dialect
        )
        
        result = generator(input=query_input)
        
        # Assertions
        assert result.dialect_used == dialect
        assert result.is_valid is True
        assert "created_at" in result.sql.lower()
        
        print(f"\n{dialect.value.upper()} date handling: {result.sql}")
    
    def test_dialects_produce_different_sql(self, generator, test_schema):
        """Verify that different dialects actually produce different SQL"""
        query = "find users created in the last 30 days"
        
        # Generate SQL for each dialect
        results = {}
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=query,
                table_schema=test_schema,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            results[dialect] = result.sql
        
        # Verify we get different SQL for different dialects
        mysql_sql = results[SQLDialect.MYSQL]
        postgres_sql = results[SQLDialect.POSTGRESQL] 
        sqlite_sql = results[SQLDialect.SQLITE]
        
        # At least one should be different (proving dialect support works)
        assert not (mysql_sql == postgres_sql == sqlite_sql), \
            f"All dialects produced identical SQL: {mysql_sql}"
        
        print(f"\nDialect differences confirmed:")
        for dialect, sql in results.items():
            print(f"  {dialect.value.upper()}: {sql}")

 