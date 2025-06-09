"""
Tests for SymbolicAI contracts for SQL generation
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
def client_table_schema():
    """Fixture to provide test table schema"""
    return """
    Table: clients
    Columns: client_id (INT), name (VARCHAR), email (VARCHAR), status (VARCHAR)
    """


class TestSemanticSQLGenerator:
    """Test cases for SemanticSQLGenerator contract"""
    
    def test_contract_initialization(self, generator):
        """Test that contract can be initialized"""
        assert generator is not None
        assert generator.current_dialect == SQLDialect.GENERIC
    
    def test_basic_sql_generation(self, generator):
        """Test basic SQL generation functionality"""
        query_input = QueryInput(query="find all users")
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
        assert len(result.sql.strip()) > 0
    
    def test_table_schema_generation(self, generator):
        """Test SQL generation with table schema"""
        query_input = QueryInput(
            query="find all active users",
            table_schema="Table: users\nColumns: id (INT), name (VARCHAR), status (VARCHAR)"
        )
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert "users" in result.sql.lower()
        assert result.sql is not None
    
    def test_contract_input_validation(self, generator):
        """Test that contract validates input properly"""
        # Valid input should work
        valid_input = QueryInput(query="select all users")
        result = generator(input=valid_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE,
    ])
    def test_sql_dialect_generation(self, generator, dialect):
        """Test SQL generation with different dialects"""
        query_input = QueryInput(
            query="find all users created yesterday",
            sql_dialect=dialect
        )
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
        assert len(result.sql.strip()) > 0 