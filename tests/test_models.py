"""
Basic tests for Pydantic models
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput


class TestQueryInput:
    """Test cases for QueryInput model"""
    
    def test_query_input_creation(self):
        """Test creating QueryInput with required fields"""
        query_input = QueryInput(query="find all users")
        assert query_input.query == "find all users"
        assert query_input.table_schema == ""  # Default value is empty string
        
    def test_query_input_with_schema(self):
        """Test creating QueryInput with table schema"""
        schema = "Table: users\nColumns: id (INT), name (VARCHAR)"
        query_input = QueryInput(query="find all users", table_schema=schema)
        assert query_input.query == "find all users"
        assert query_input.table_schema == schema


class TestSQLOutput:
    """Test cases for SQLOutput model"""
    
    def test_sql_output_creation(self):
        """Test creating SQLOutput with required fields"""
        sql_output = SQLOutput(sql="SELECT * FROM users")
        assert sql_output.sql == "SELECT * FROM users" 