"""
Test SymbolicAI contracts for SQL generation
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from semantic2sql import QueryInput, SQLOutput, BasicSQLGenerator


def test_basic_sql_generation():
    """Test basic SQL generation without table schema"""
    generator = BasicSQLGenerator()
    
    test_queries = [
        "show me all active users",
        "get the top 5 customers by order rating",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        test_input = QueryInput(query=query)
        result = generator(input=test_input)
        print(f"SQL: {result.sql}")


def test_table_schema_generation():
    """Test SQL generation with table schema"""
    generator = BasicSQLGenerator()
    
    # Client table schema
    client_table = """
    Table: clients
    Columns: client_id (INT), name (VARCHAR), email (VARCHAR), risk_tolerance (VARCHAR), account_type (VARCHAR), onboard_date (DATE)
    """
    
    print(f"Table: {client_table.strip()}")
    
    table_queries = [
        "find all high-risk clients",
        "get clients who joined in the last 30 days",
        "show client emails sorted by name",
    ]
    
    for query in table_queries:
        print(f"\nQuery: '{query}'")
        test_input = QueryInput(query=query, table_schema=client_table)
        result = generator(input=test_input)
        print(f"SQL: {result.sql}")


if __name__ == "__main__":
    test_basic_sql_generation()
    test_table_schema_generation() 