"""
SQL generation service using SymbolicAI contracts
"""

from typing import Dict, Any
from .contracts import SemanticSQLGenerator
from .models import QueryInput


class SQLGeneratorService:
    """
    Service for generating SQL from natural language queries
    """
    
    def __init__(self):
        """Initialize the SQL generator"""
        self.sql_generator = SemanticSQLGenerator()
        
    def generate_sql(self, natural_query: str, table_schema: str) -> str:
        """
        Generate SQL for a natural language query with table schema
        
        Args:
            natural_query: Natural language description of the query
            table_schema: Table schema information
            
        Returns:
            Generated SQL query string
        """
        # Create input for SQL generator
        query_input = QueryInput(
            query=natural_query,
            table_schema=table_schema
        )
        
        # Generate SQL using our contract
        result = self.sql_generator(input=query_input)
        return result.sql
        
    def generate_sql_for_table(self, natural_query: str, table_name: str, columns_info: str) -> str:
        """
        Generate SQL for a specific table with column information
        
        Args:
            natural_query: Natural language description
            table_name: Target table name
            columns_info: Column definitions string
            
        Returns:
            Generated SQL query string
        """
        # Format schema for the generator
        table_schema = f"Table: {table_name}\n   Columns: {columns_info}"
        
        return self.generate_sql(natural_query, table_schema) 