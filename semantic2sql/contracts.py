"""
SymbolicAI contracts for SQL generation
"""

from symai import Expression
from symai.strategy import contract

from .models import QueryInput, SQLOutput, SQLDialect


@contract(
    pre_remedy=False,
    post_remedy=True,
    verbose=True
)
class SemanticSQLGenerator(Expression):
    """
    SymbolicAI contract for generating syntactically correct SQL queries from natural language
    """
    
    def __init__(self):
        super().__init__()
        self.current_dialect = SQLDialect.GENERIC
    
    @property
    def prompt(self) -> str:
        dialect_name = self.current_dialect.value.upper()
        
        return f"""
You are an expert SQL generator that creates syntactically correct SQL queries from natural language descriptions.

Generate SQL using {dialect_name} dialect syntax.

Your task:
1. Convert the natural language query to proper {dialect_name} SQL syntax
2. Ensure the SQL is syntactically correct and valid

If table schema is provided, use the exact table and column names specified.
If no schema is provided, use reasonable generic table/column names.

Output format:
- sql: The generated SQL query (syntactically correct for {dialect_name})
- is_valid: true if SQL syntax is correct, false if there are issues
- validation_notes: Any notes about syntax validation or corrections made
- dialect_used: "{self.current_dialect.value}"

Examples:

Query: "find all users"
Schema: "Table: users\\nColumns: id (INT), name (VARCHAR), email (VARCHAR)"
Response: {{
  "sql": "SELECT * FROM users",
  "is_valid": true,
  "validation_notes": "",
  "dialect_used": "{self.current_dialect.value}"
}}

Always ensure your generated SQL follows proper {dialect_name} syntax.
"""



    def forward(self, input: QueryInput) -> SQLOutput:
        """Generate SQL from natural language input"""
        # Set current dialect for this request
        self.current_dialect = input.sql_dialect
        
        if self.contract_result is None:
            return SQLOutput(
                sql="SELECT 1;", 
                is_valid=True, 
                validation_notes="",
                dialect_used=input.sql_dialect
            )
        
        # Ensure the result has the correct dialect
        result = self.contract_result
        result.dialect_used = input.sql_dialect
        return result
    
    def pre(self, input: QueryInput) -> bool:
        """Pre-condition: Check if query is valid"""
        return len(input.query.strip()) > 0
    
    def post(self, result: SQLOutput) -> bool:
        """
        Post-condition: Validate that the generated SQL is syntactically correct
        If this returns False, SymbolicAI will automatically retry the contract
        """
        # Check if the contract itself marked the SQL as invalid
        if not result.is_valid:
            return False
        
        # Basic syntax checks
        sql = result.sql.strip()
        if not sql:
            return False
            

            
        # Basic balance checks for common syntax issues
        if sql.count("(") != sql.count(")"):
            return False
        if sql.count("'") % 2 != 0:  # Unbalanced single quotes
            return False
        if sql.count('"') % 2 != 0:  # Unbalanced double quotes
            return False
        
        # Dialect-specific validation
        return self._validate_dialect_syntax(sql, result.dialect_used)
    
    def _validate_dialect_syntax(self, sql: str, dialect: SQLDialect) -> bool:
        """Perform dialect-specific syntax validation"""
        sql_upper = sql.upper()
        
        if dialect == SQLDialect.MYSQL:
            # MySQL-specific checks
            if " TOP " in sql_upper:  # MySQL uses LIMIT, not TOP
                return False
        elif dialect == SQLDialect.POSTGRESQL:
            # PostgreSQL-specific checks
            if " TOP " in sql_upper:  # PostgreSQL uses LIMIT, not TOP
                return False
        elif dialect == SQLDialect.SQLITE:
            # SQLite-specific checks
            if " FULL OUTER JOIN " in sql_upper:  # SQLite doesn't support FULL OUTER JOIN
                return False
            if " TOP " in sql_upper:  # SQLite uses LIMIT, not TOP
                return False
        
        return True 