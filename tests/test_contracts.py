"""
Tests for SymbolicAI contracts for SQL generation
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput, SemanticSQLGenerator


class TestSemanticSQLGenerator:
    """Test cases for SemanticSQLGenerator contract"""
    
    def test_contract_initialization(self):
        """Test that contract can be initialized"""
        generator = SemanticSQLGenerator()
        assert generator is not None
    
    def test_basic_sql_generation(self):
        """Test basic SQL generation without table schema"""
        generator = SemanticSQLGenerator()
        test_input = QueryInput(query="show me all active users")
        result = generator(input=test_input)
        
        assert isinstance(result, SQLOutput)
        assert result.sql
        assert "SELECT" in result.sql.upper()
        assert result.is_valid is True
    
    def test_table_schema_generation(self):
        """Test SQL generation with table schema"""
        generator = SemanticSQLGenerator()
        
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
        assert result.is_valid is True
    
    def test_contract_input_validation(self):
        """Test contract handles input properly"""
        generator = SemanticSQLGenerator()
        
        # Test with valid input
        test_input = QueryInput(query="find users")
        result = generator(input=test_input)
        assert isinstance(result, SQLOutput)
        assert result.is_valid is True 