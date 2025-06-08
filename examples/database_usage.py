#!/usr/bin/env python3
"""
Example showing how to use SQLInterface with the Northwind database
This demonstrates automatic schema discovery and SQL generation with actual data.

To use this example:
1. Download northwind.db from: https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db
2. Place it in your project directory
3. Run this script!
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from semantic2sql import SQLInterface, SQLGeneratorService

# Get database path from environment or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "northwind.db")


def main():
    """Demonstrate SQLInterface with the Northwind database"""
    
    # Check if database exists
    if not Path(DATABASE_PATH).exists():
        print(f"Database not found: {DATABASE_PATH}")
        print()
        print("To get the Northwind database:")
        print("   1. Download from: https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db")
        print("   2. Save it to your project directory")
        print("   3. Set DATABASE_PATH environment variable or create .env file")
        print()
        print("Example .env file:")
        print("   DATABASE_PATH=northwind.db")
        return
    
    print("Exploring Northwind Database\n")
    
    # Initialize components
    sql_generator = SQLGeneratorService()
    
    # Connect to database
    with SQLInterface(DATABASE_PATH) as db:
        
        # 1. Show available tables
        print("Available Tables:")
        tables_info = db.list_tables_with_info()
        for table_name, info in tables_info.items():
            print(f"   • {table_name}: {info['row_count']} rows, {info['column_count']} columns")
            print(f"     Columns: {', '.join(info['columns'][:5])}{'...' if len(info['columns']) > 5 else ''}")
        
        print("\n" + "="*60 + "\n")
        
        # 2. Generate and execute queries for different tables
        test_queries = [
            # Customers table
            ("Customers", "find customers from USA"),
            ("Customers", "get customers from London"),
            ("Customers", "show customers from Germany"),
            
            # Products table  
            ("Products", "find products under 20 dollars"),
            ("Products", "get discontinued products"),
            ("Products", "show the most expensive products"),
            ("Products", "find beverages"),
            
            # Orders table
            ("Orders", "find orders from 1997"),
            ("Orders", "get recent orders"),
            ("Orders", "show orders with high freight cost"),
            
            # Employees table
            ("Employees", "find employees from London"),
            ("Employees", "get sales representatives"),
            ("Employees", "show employees hired after 1993"),
        ]
        
        for table_name, natural_query in test_queries:
            print(f"Table: {table_name}")
            print(f"Query: \"{natural_query}\"")
            
            try:
                # Show the auto-discovered schema
                schema = db.get_table_schema(table_name)
                print(f"Schema: {schema.replace(chr(10), ' ')}")
                
                # Generate SQL using the generator
                sql = sql_generator.generate_sql(natural_query, schema)
                
                # Execute the query
                results = db.execute_query(sql)
                
                print(f"Generated SQL: {sql}")
                print(f"Results: {len(results)} rows")
                
                # Show sample results (first 3 rows)
                if results:
                    print("   Sample data:")
                    for i, row in enumerate(results[:3]):
                        # Show first few fields to keep output manageable
                        row_preview = {k: v for k, v in list(row.items())[:3]}
                        print(f"     Row {i+1}: {row_preview}")
                    
                    if len(results) > 3:
                        print(f"     ... and {len(results) - 3} more rows")
                
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n" + "-"*50 + "\n")
        
        # 3. Demonstrate schema introspection
        print("Schema Introspection Examples:\n")
        
        example_tables = ["Customers", "Products", "Orders", "Employees"]
        for table in example_tables:
            print(f"{table.upper()} Table Schema:")
            schema = db.get_table_schema(table)
            print(f"   {schema}")
            print()


if __name__ == "__main__":
    main() 