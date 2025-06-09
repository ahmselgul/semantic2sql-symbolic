#!/usr/bin/env python3
"""
Basic usage example for semantic2sql-symbolic
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from semantic2sql.contracts import SemanticSQLGenerator
from semantic2sql.models import QueryInput, SQLDialect


def main():
    """Demonstrate basic SQL generation with different dialects"""
    
    # Initialize the SQL generator
    generator = SemanticSQLGenerator()
    
    # Demo table: Portfolio positions
    portfolio_table = """
    Table: portfolio_positions
    Columns: position_id (INT), client_id (INT), symbol (VARCHAR), quantity (DECIMAL), avg_cost (DECIMAL), current_price (DECIMAL), last_updated (TIMESTAMP)
    """
    
    print("Portfolio Management SQL Generator")
    print("=" * 50)
    print(f"Table Schema:")
    for line in portfolio_table.strip().split('\n'):
        if line.strip():
            print(f"   {line.strip()}")
    
    # Example queries with different dialects
    test_cases = [
        ("Find all positions with unrealized losses", SQLDialect.MYSQL),
        ("Get the largest position by value", SQLDialect.POSTGRESQL), 
        ("Show positions updated in the last hour", SQLDialect.SQLITE),
        ("List all losing positions", SQLDialect.GENERIC)
    ]
    
    print("\nQuery Examples:")
    print("-" * 50)
    
    for query, dialect in test_cases:
        print(f"\nNatural Language: \"{query}\"")
        print(f"SQL Dialect: {dialect.value.upper()}")
        
        # Create input with table schema and dialect
        input_data = QueryInput(
            query=query, 
            table_schema=portfolio_table,
            sql_dialect=dialect
        )
        
        # Generate SQL - note the simplified output (just .sql)
        result = generator(input=input_data)
        
        print(f"Generated SQL: {result.sql}")
    
    print(f"\nDemo completed! Generated {len(test_cases)} SQL queries across different dialects.")


if __name__ == "__main__":
    main() 