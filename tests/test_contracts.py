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
        """Test basic SQL generation without table schema"""
        test_input = QueryInput(query="show me all active users")
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql
        assert result.is_valid is True
        assert result.dialect_used == SQLDialect.GENERIC
    
    def test_table_schema_generation(self, generator, client_table_schema):
        """Test SQL generation with table schema"""
        test_input = QueryInput(query="find all active clients", table_schema=client_table_schema)
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql
        assert "clients" in result.sql.lower()
        assert result.is_valid is True
        assert result.dialect_used == SQLDialect.GENERIC
    
    def test_contract_input_validation(self, generator):
        """Test contract handles input properly"""
        # Test with valid input
        test_input = QueryInput(query="find users")
        result = generator(input=test_input)
        assert isinstance(result, SQLOutput)
        assert result.is_valid is True
        
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE
    ])
    def test_sql_dialect_generation(self, generator, dialect):
        """Test SQL generation with different dialects"""
        test_input = QueryInput(
            query="find all users",
            sql_dialect=dialect
        )
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.dialect_used == dialect
        assert result.sql
        
    @pytest.mark.parametrize("sql,dialect,expected", [
        ("SELECT * FROM users FULL OUTER JOIN orders ON users.id = orders.user_id", SQLDialect.SQLITE, False),
        ("SELECT TOP 10 * FROM users", SQLDialect.MYSQL, False),
        ("SELECT * FROM users LIMIT 10", SQLDialect.MYSQL, True)
    ])
    def test_dialect_specific_validation(self, generator, sql, dialect, expected):
        """Test dialect-specific validation in post-conditions"""
        result = generator._validate_dialect_syntax(sql, dialect)
        assert result is expected 