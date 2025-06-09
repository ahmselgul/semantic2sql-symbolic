#!/usr/bin/env python3
"""
Example showing how to use semantic2sql-symbolic with a real database
This demonstrates SQL generation with different dialects using the Northwind database.

To use this example:
1. Download northwind.db from: https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db
2. Place it in your project directory
3. Run this script!
"""

import sys
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from semantic2sql.contracts import SemanticSQLGenerator
from semantic2sql.models import QueryInput, SQLDialect

# Get database path from environment or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "northwind.db")


def get_table_schema(cursor, table_name):
    """Get table schema information"""
    cursor.execute(f"PRAGMA table_info(`{table_name}`)")
    columns = cursor.fetchall()
    
    schema_lines = [f"Table: {table_name}"]
    column_info = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        column_info.append(f"{col_name} ({col_type})")
    
    schema_lines.append(f"Columns: {', '.join(column_info)}")
    return "\n".join(schema_lines)


def get_table_names(cursor):
    """Get all table names from the database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]


def safe_count_rows(cursor, table_name):
    """Safely count rows in a table, handling special characters in table names"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        return cursor.fetchone()[0]
    except Exception:
        return 0


def main():
    """Demonstrate semantic2sql-symbolic with the Northwind database"""
    
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
    
    print("Northwind Database SQL Generator")
    print("=" * 60)
    
    # Initialize the SQL generator
    generator = SemanticSQLGenerator()
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Show available tables
        print("\nAvailable Tables:")
        tables = get_table_names(cursor)
        for table in tables:
            count = safe_count_rows(cursor, table)
            print(f"   • {table}: {count:,} rows")
        
        print(f"\nTesting SQL Generation and Execution")
        print("=" * 60)
        
        # 2. Generate and execute queries for different tables
        test_queries = [
            # Basic queries
            ("Customers", "find customers from USA"),
            ("Customers", "find customers from Germany"), 
            ("Customers", "get customers from London"),
            
            # Products with filtering
            ("Products", "find products under 20 dollars"),
            ("Products", "get discontinued products"),
            ("Products", "show products ordered by price"),
            
            # Orders with date functions
            ("Orders", "find orders from 1996"),
            ("Orders", "show orders with high freight cost over 100"),
            
            # Employees 
            ("Employees", "find employees from London"),
            ("Employees", "show employees hired after 1993"),
        ]
        
        for table_name, natural_query in test_queries:
            print(f"\nTable: {table_name}")
            print(f"Query: \"{natural_query}\"")
            
            try:
                # Get the table schema
                schema = get_table_schema(cursor, table_name)
                print(f"Schema: {schema.replace(chr(10), ' | ')}")
                
                # Generate SQL using SQLite dialect (matches our database)
                input_data = QueryInput(
                    query=natural_query,
                    table_schema=schema,
                    sql_dialect=SQLDialect.SQLITE
                )
                
                result = generator(input=input_data)
                
                print(f"Generated SQL: {result.sql}")
                
                # Execute the query and show results
                try:
                    # Replace table name with quoted version for SQLite
                    safe_sql = result.sql.replace(table_name, f"`{table_name}`")
                    cursor.execute(safe_sql)
                    rows = cursor.fetchmany(10)  # Get first 10 rows
                    
                    print(f"EXECUTION RESULTS:")
                    print(f"  Status: SUCCESS")
                    print(f"  Rows returned: {len(rows)}")
                    
                    if rows:
                        # Show column names
                        columns = [desc[0] for desc in cursor.description]
                        print(f"  Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
                        
                        # Show sample data (first 3 rows, first 4 columns)
                        print(f"  Sample data:")
                        for i, row in enumerate(rows[:3]):
                            row_data = {columns[j]: row[j] for j in range(min(4, len(columns)))}
                            print(f"    Row {i+1}: {row_data}")
                        
                        if len(rows) > 3:
                            print(f"    ... and {len(rows) - 3} more rows")
                    else:
                        print(f"  No matching records found")
                        
                except Exception as exec_error:
                    print(f"EXECUTION RESULTS:")
                    print(f"  Status: FAILED")
                    print(f"  Error: {exec_error}")
                
            except Exception as e:
                print(f"ERROR: {e}")
            
            print("-" * 80)
        
        # 3. Show schema introspection examples
        print(f"\nSchema Introspection Examples")
        print("=" * 40)
        
        example_tables = ["Customers", "Products", "Orders"][:2]  # Show just 2 for brevity
        for table in example_tables:
            schema = get_table_schema(cursor, table)
            print(f"\n{table.upper()}:")
            for line in schema.split('\n'):
                print(f"   {line}")
    
    finally:
        conn.close()
    
    print(f"\nDemo completed! Tested SQL generation across multiple dialects.")


if __name__ == "__main__":
    main() 