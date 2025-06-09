"""
Basic tests for Pydantic models
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput
from semantic2sql.models import SQLDialect


@pytest.fixture
def sample_schema():
    """Fixture to provide sample table schema"""
    return "Table: users\nColumns: id (INT), name (VARCHAR)"


class TestQueryInput:
    """Test cases for QueryInput model"""
    
    def test_query_input_creation(self):
        """Test creating QueryInput with required fields"""
        query_input = QueryInput(query="find all users")
        assert query_input.query == "find all users"
        assert query_input.table_schema == ""  # Default value is empty string
        assert query_input.sql_dialect == SQLDialect.GENERIC  # Default dialect
        
    def test_query_input_with_schema(self, sample_schema):
        """Test creating QueryInput with table schema"""
        query_input = QueryInput(query="find all users", table_schema=sample_schema)
        assert query_input.query == "find all users"
        assert query_input.table_schema == sample_schema
        assert query_input.sql_dialect == SQLDialect.GENERIC
    
    def test_query_input_with_dialect(self):
        """Test creating QueryInput with specific SQL dialect"""
        query_input = QueryInput(query="find all users", sql_dialect=SQLDialect.MYSQL)
        assert query_input.query == "find all users"
        assert query_input.sql_dialect == SQLDialect.MYSQL
        
    @pytest.mark.parametrize("dialect", list(SQLDialect))
    def test_query_input_all_dialects(self, dialect):
        """Test QueryInput with all supported dialects"""
        query_input = QueryInput(query="test query", sql_dialect=dialect)
        assert query_input.sql_dialect == dialect


class TestSQLOutput:
    """Test cases for SQLOutput model"""
    
    def test_sql_output_creation(self):
        """Test creating SQLOutput with required fields"""
        sql_output = SQLOutput(sql="SELECT * FROM users")
        assert sql_output.sql == "SELECT * FROM users"

    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE,
        SQLDialect.GENERIC
    ])
    def test_sql_output_with_dialect(self, dialect):
        """Test SQLOutput creation is independent of dialect"""  
        sql_output = SQLOutput(sql="SELECT name FROM users WHERE id = 1")
        assert sql_output.sql == "SELECT name FROM users WHERE id = 1"

    def test_sql_output_minimal(self):
        """Test SQLOutput with only required fields"""
        sql_output = SQLOutput(sql="SELECT 1")
        assert sql_output.sql == "SELECT 1"


class TestSQLDialect:
    """Test cases for SQLDialect enum"""
    
    def test_dialect_enum_values(self):
        """Test that all expected SQL dialects are available"""
        expected_dialects = {"sqlite", "mysql", "postgresql", "generic"}
        actual_dialects = {dialect.value for dialect in SQLDialect}
        assert actual_dialects == expected_dialects
        
    @pytest.mark.parametrize("dialect,expected_value", [
        (SQLDialect.MYSQL, "mysql"),
        (SQLDialect.POSTGRESQL, "postgresql"),
        (SQLDialect.SQLITE, "sqlite"),
        (SQLDialect.GENERIC, "generic")
    ])
    def test_dialect_string_representation(self, dialect, expected_value):
        """Test dialect string representation"""
        assert dialect.value == expected_value 