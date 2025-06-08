#!/usr/bin/env python3
"""
Basic usage example for semantic2sql
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from semantic2sql import QueryInput, SQLOutput, BasicSQLGenerator


def main():
    """Demonstrate SQL generation with table schema"""
    
    # Initialize the SQL generator
    generator = BasicSQLGenerator()
    
    # Demo table: Portfolio positions
    portfolio_table = """
    Table: portfolio_positions
    Columns: position_id (INT), client_id (INT), symbol (VARCHAR), quantity (DECIMAL), avg_cost (DECIMAL), current_price (DECIMAL), last_updated (TIMESTAMP)
    """
    
    print(f"Table Schema:")
    for line in portfolio_table.strip().split('\n'):
        if line.strip():
            print(f"   {line.strip()}")
    
    # Example queries
    queries = [
        "find all positions with unrealized losses",
        "get the largest position by value",
        "show positions updated in the last hour"
    ]
    
    for query in queries:
        print(f"\nNatural Language: {query}")
        
        # Create input with table schema
        input_data = QueryInput(query=query, table_schema=portfolio_table)
        
        # Generate SQL
        result = generator(input=input_data)
        
        print(f"Generated SQL: {result.sql}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main() 