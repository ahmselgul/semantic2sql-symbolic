"""
Basic tests for SymbolicAI contracts for SQL generation
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput, BasicSQLGenerator


class TestBasicSQLGenerator:
    """Basic test cases for BasicSQLGenerator contract"""
    
    def test_contract_initialization(self):
        """Test that contract can be initialized"""
        generator = BasicSQLGenerator()
        assert generator is not None
    
    def test_basic_sql_generation(self):
        """Test basic SQL generation without table schema"""
        generator = BasicSQLGenerator()
        test_input = QueryInput(query="show me all active users")
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql
        assert "SELECT" in result.sql.upper()
    
    def test_table_schema_generation(self):
        """Test SQL generation with table schema"""
        generator = BasicSQLGenerator()
        
        client_table = """
        Table: clients
        Columns: client_id (INT), name (VARCHAR), email (VARCHAR), status (VARCHAR)
        """
        
        test_input = QueryInput(query="find all active clients", table_schema=client_table)
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql
        assert "SELECT" in result.sql.upper()
        assert "clients" in result.sql.lower()
    
    def test_contract_input_validation(self):
        """Test contract handles invalid input properly"""
        generator = BasicSQLGenerator()
        
        # Test with valid input
        test_input = QueryInput(query="find users")
        result = generator(input=test_input)
        assert isinstance(result, SQLOutput) 