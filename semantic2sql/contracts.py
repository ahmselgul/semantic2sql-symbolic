"""
SymbolicAI contracts for SQL generation
"""

from symai import Expression
from symai.strategy import contract

from .models import QueryInput, SQLOutput


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
    
    @property
    def prompt(self) -> str:
        return """
You are an expert SQL generator that creates syntactically correct SQL queries from natural language descriptions.

Your task:
1. Convert the natural language query to proper SQL syntax
2. Ensure the SQL is syntactically correct and valid
3. Use proper SQL formatting and conventions
4. Generate ONLY SELECT statements for safety

If table schema is provided, use the exact table and column names specified.
If no schema is provided, use reasonable generic table/column names.

IMPORTANT: Always validate your SQL syntax before responding. The query will be automatically retried if syntax is invalid.

Output format:
- sql: The generated SQL query (syntactically correct)
- is_valid: true if SQL syntax is correct, false if there are issues
- validation_notes: Any notes about syntax validation or corrections made

Examples:

Query: "find all users"
Schema: "Table: users\nColumns: id (INT), name (VARCHAR), email (VARCHAR)"
Response: {
  "sql": "SELECT * FROM users",
  "is_valid": true,
  "validation_notes": ""
}

Query: "get users from London"  
Schema: "Table: users\nColumns: id (INT), name (VARCHAR), city (VARCHAR)"
Response: {
  "sql": "SELECT * FROM users WHERE city = 'London'",
  "is_valid": true,
  "validation_notes": ""
}

Always ensure your generated SQL follows proper syntax rules and is ready to execute.
"""

    def forward(self, input: QueryInput) -> SQLOutput:
        """Generate SQL from natural language input"""
        if self.contract_result is None:
            return SQLOutput(sql="SELECT 1;", is_valid=True, validation_notes="")
        return self.contract_result
    
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
            
        # Must be a SELECT statement (for safety)
        if not sql.upper().startswith("SELECT"):
            return False
            
        # Basic balance checks for common syntax issues
        if sql.count("(") != sql.count(")"):
            return False
        if sql.count("'") % 2 != 0:  # Unbalanced single quotes
            return False
        if sql.count('"') % 2 != 0:  # Unbalanced double quotes
            return False
            
        return True 