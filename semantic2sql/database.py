"""
Database interface for automatic schema discovery and query execution
"""

import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path


class SQLInterface:
    """
    Interface for connecting to databases with automatic schema discovery
    """
    
    def __init__(self, database_path: str):
        """
        Initialize database connection
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        
    def get_table_names(self) -> List[str]:
        """Get all table names in the database"""
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]
        
    def get_table_schema(self, table_name: str) -> str:
        """
        Get formatted table schema for a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Formatted schema string for the SQL generator
        """
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        cursor = self.connection.cursor()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        if not columns:
            raise ValueError(f"Table '{table_name}' not found")
            
        # Format as expected by our SQL generator
        schema_lines = [f"Table: {table_name}"]
        column_parts = []
        
        for col in columns:
            col_name = col[1]  # name
            col_type = col[2]  # type
            is_pk = col[5]     # pk
            not_null = col[3]  # notnull
            
            col_desc = f"{col_name} ({col_type}"
            if is_pk:
                col_desc += ", PRIMARY KEY"
            if not_null and not is_pk:
                col_desc += ", NOT NULL"
            col_desc += ")"
            
            column_parts.append(col_desc)
            
        schema_lines.append(f"Columns: {', '.join(column_parts)}")
        return "\n   ".join(schema_lines)
        
    def list_tables_with_info(self) -> Dict[str, Dict[str, Any]]:
        """Get all tables with basic information"""
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        tables = {}
        for table_name in self.get_table_names():
            cursor = self.connection.cursor()
            # Quote table names to handle reserved words and special characters
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cursor.fetchone()[0]
            
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            
            tables[table_name] = {
                'row_count': row_count,
                'column_count': len(columns),
                'columns': [col[1] for col in columns]
            }
            
        return tables
        
    def get_columns_info(self, table_name: str) -> str:
        """
        Get formatted column information for a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Formatted column information string
        """
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        cursor = self.connection.cursor()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        if not columns:
            raise ValueError(f"Table '{table_name}' not found")
            
        # Format column information
        column_parts = []
        for col in columns:
            col_name = col[1]  # name
            col_type = col[2]  # type
            is_pk = col[5]     # pk
            not_null = col[3]  # notnull
            
            col_desc = f"{col_name} ({col_type}"
            if is_pk:
                col_desc += ", PRIMARY KEY"
            if not_null and not is_pk:
                col_desc += ", NOT NULL"
            col_desc += ")"
            
            column_parts.append(col_desc)
            
        return ", ".join(column_parts)
        
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Query results as list of dictionaries
        """
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        
        # Convert to list of dictionaries
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
        return results
        
 