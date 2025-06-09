"""
Dialect testing focusing on dialect differences
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic2sql import QueryInput, SQLOutput, SemanticSQLGenerator
from semantic2sql.models import SQLDialect


@pytest.fixture
def generator():
    """Fixture to provide SQL generator instance"""
    return SemanticSQLGenerator()


@pytest.fixture
def test_schema():
    """Fixture to provide test schema"""
    return """
    Table: users
    Columns: id (INT), name (VARCHAR), created_at (TIMESTAMP), age (INT)
    """


class TestDialectSupport:
    """Test key dialect differences with proper pytest patterns"""
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE,
        SQLDialect.GENERIC
    ])
    def test_basic_functionality_all_dialects(self, generator, test_schema, dialect):
        """Test basic functionality works across all dialects"""
        query_input = QueryInput(
            query="find all users older than 25",
            table_schema=test_schema,
            sql_dialect=dialect
        )
        
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
        assert len(result.sql.strip()) > 0
        assert "users" in result.sql.lower()
        assert "25" in result.sql or ">" in result.sql
        
        print(f"\n{dialect.value.upper()}: {result.sql}")
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE
    ])
    def test_date_functions_show_differences(self, generator, test_schema, dialect):
        """Test date functions where we expect dialect differences"""
        query_input = QueryInput(
            query="find users created in the last 30 days",
            table_schema=test_schema,
            sql_dialect=dialect
        )
        
        result = generator(input=query_input)
        
        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
        assert "users" in result.sql.lower()
        assert "30" in result.sql
        
        # Check for dialect-specific syntax
        sql_lower = result.sql.lower()
        if dialect == SQLDialect.MYSQL:
            # MySQL should use INTERVAL syntax
            assert "interval" in sql_lower or "date_sub" in sql_lower
        elif dialect == SQLDialect.POSTGRESQL:
            # PostgreSQL should use INTERVAL with quotes
            assert "interval" in sql_lower and "'" in result.sql
        elif dialect == SQLDialect.SQLITE:
            # SQLite should use datetime/date functions
            assert ("datetime" in sql_lower or "date" in sql_lower) and "now" in sql_lower
        
        print(f"\n{dialect.value.upper()} date handling: {result.sql}")
    
    @pytest.mark.parametrize("dialect", [
        SQLDialect.MYSQL,
        SQLDialect.POSTGRESQL,
        SQLDialect.SQLITE
    ])
    def test_case_sensitive_search_differences(self, generator, test_schema, dialect):
        """Test case-sensitive search differences between dialects"""
        query_input = QueryInput(
            query="find users with names containing 'john' (case-insensitive)",
            table_schema=test_schema,
            sql_dialect=dialect
        )

        result = generator(input=query_input)

        # Assertions
        assert isinstance(result, SQLOutput)
        assert result.sql is not None
        assert "john" in result.sql.lower()
        
        # Check for dialect-specific case-insensitive syntax
        sql_lower = result.sql.lower()
        if dialect == SQLDialect.POSTGRESQL:
            # PostgreSQL should use ILIKE
            assert "ilike" in sql_lower
        else:
            # MySQL and SQLite should use LIKE
            assert "like" in sql_lower
    
    def test_dialects_produce_different_sql(self, generator, test_schema):
        """Verify that different dialects actually produce different SQL"""
        
        # Test Case 1: Date functions (known to produce differences)
        date_query = "find users created in the last 30 days"
        date_results = {}
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=date_query,
                table_schema=test_schema,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            date_results[dialect] = result.sql
        
        print(f"\n=== DATE FUNCTIONS TEST ===")
        for dialect, sql in date_results.items():
            print(f"  {dialect.value.upper()}: {sql}")
        
        # Test Case 2: String functions and pattern matching
        string_query = "find users whose name contains 'john' and format the name in uppercase"
        string_results = {}
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=string_query,
                table_schema=test_schema,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            string_results[dialect] = result.sql
        
        print(f"\n=== STRING FUNCTIONS TEST ===")
        for dialect, sql in string_results.items():
            print(f"  {dialect.value.upper()}: {sql}")
            
        # Test Case 3: Limit and pagination syntax
        limit_query = "get the first 10 users ordered by name"
        limit_results = {}
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=limit_query,
                table_schema=test_schema,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            limit_results[dialect] = result.sql
        
        print(f"\n=== LIMIT/PAGINATION TEST ===")
        for dialect, sql in limit_results.items():
            print(f"  {dialect.value.upper()}: {sql}")
            
        # Test Case 4: Date formatting functions
        format_query = "show user names and their registration dates formatted as YYYY-MM-DD"
        format_results = {}
        extended_schema = """
        Table: users
        Columns: id (INT), name (VARCHAR), created_at (TIMESTAMP), age (INT), registered_at (DATETIME)
        """
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=format_query,
                table_schema=extended_schema,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            format_results[dialect] = result.sql
        
        print(f"\n=== DATE FORMATTING TEST ===")
        for dialect, sql in format_results.items():
            print(f"  {dialect.value.upper()}: {sql}")
            
        # Test Case 5: Auto-increment and identity columns
        create_query = "create a table for storing user sessions with auto-incrementing ID"
        create_results = {}
        for dialect in [SQLDialect.MYSQL, SQLDialect.POSTGRESQL, SQLDialect.SQLITE]:
            query_input = QueryInput(
                query=create_query,
                sql_dialect=dialect
            )
            result = generator(input=query_input)
            create_results[dialect] = result.sql
        
        print(f"\n=== AUTO-INCREMENT/IDENTITY TEST ===")
        for dialect, sql in create_results.items():
            print(f"  {dialect.value.upper()}: {sql}")
        
        # Verification: Check that we get different SQL for different test cases
        print(f"\n=== DIALECT DIFFERENCES ANALYSIS ===")
        
        all_test_results = [date_results, string_results, limit_results, format_results, create_results]
        test_names = ["Date Functions", "String Functions", "Limit/Pagination", "Date Formatting", "Auto-Increment"]
        
        differences_found = False
        for i, (test_name, results) in enumerate(zip(test_names, all_test_results)):
            mysql_sql = results[SQLDialect.MYSQL]
            postgres_sql = results[SQLDialect.POSTGRESQL] 
            sqlite_sql = results[SQLDialect.SQLITE]
            
            # Check if any dialects produce different SQL
            has_differences = not (mysql_sql == postgres_sql == sqlite_sql)
            status = "DIFFERENT" if has_differences else "IDENTICAL"
            print(f"  {test_name}: {status}")
            
            if has_differences:
                differences_found = True
        
        # At least one test case should show differences
        assert differences_found, "No dialect differences found in any test case - dialect support may not be working properly"
        
        print(f"\nDialect support verification: PASSED")
        print(f"   Found dialect-specific differences in SQL generation")

 