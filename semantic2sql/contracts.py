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
        dialect_guide = self._get_dialect_prompt_guide(self.current_dialect)
        
        return f"""
You are an expert SQL generator that creates syntactically correct SQL queries from natural language descriptions.

Generate SQL using {dialect_name} dialect syntax.

Your task:
1. Convert the natural language query to proper {dialect_name} SQL syntax
2. Ensure the SQL is syntactically correct and valid for {dialect_name}
3. Use only functions and syntax supported by {dialect_name}

{dialect_guide}

If table schema is provided, use the exact table and column names specified.
If no schema is provided, use reasonable generic table/column names.

Output format:
- sql: The generated SQL query (syntactically correct for {dialect_name})

Example:

Query: "find all users"
Schema: "Table: users\nColumns: id (INT), name (VARCHAR), email (VARCHAR)"
Response: {{
  "sql": "SELECT * FROM users"
}}

CRITICAL: Only use {dialect_name}-specific syntax and functions. Do not mix syntax from other SQL dialects.
"""

    def _get_dialect_prompt_guide(self, dialect: SQLDialect) -> str:
        """Get dialect-specific guidance for the main prompt"""
        if dialect == SQLDialect.MYSQL:
            return """
MYSQL-SPECIFIC SYNTAX RULES:
- Date arithmetic: Use INTERVAL syntax like "NOW() - INTERVAL 30 DAY"
- Date formatting: Use DATE_FORMAT(date_col, '%Y-%m-%d')
- Auto-increment: Use AUTO_INCREMENT (not AUTOINCREMENT)
- String concatenation: Use CONCAT() function
- Case-insensitive search: Use LIKE (MySQL LIKE is case-insensitive by default)
- Limit: Use LIMIT clause

AVOID: SQLite functions (strftime, ||), PostgreSQL functions (to_char, ILIKE, SERIAL)
"""
        elif dialect == SQLDialect.POSTGRESQL:
            return """
POSTGRESQL-SPECIFIC SYNTAX RULES:
- Date arithmetic: Use INTERVAL with quotes like "NOW() - INTERVAL '30 days'"
- Date formatting: Use to_char(date_col, 'YYYY-MM-DD')
- Auto-increment: Use SERIAL PRIMARY KEY or GENERATED ALWAYS AS IDENTITY
- String concatenation: Use CONCAT() or || operator
- Case-insensitive search: Use ILIKE
- Limit: Use LIMIT clause

AVOID: MySQL functions (DATE_FORMAT, AUTO_INCREMENT), SQLite functions (strftime, AUTOINCREMENT)
"""
        elif dialect == SQLDialect.SQLITE:
            return """
SQLITE-SPECIFIC SYNTAX RULES:
- Date arithmetic: Use datetime('now', '-30 days') or date('now', '-30 days') - NO INTERVAL syntax
- Date formatting: Use strftime('%Y-%m-%d', date_col)
- Auto-increment: Use INTEGER PRIMARY KEY AUTOINCREMENT (not SERIAL or AUTO_INCREMENT)
- String concatenation: Use || operator (not CONCAT function)
- Case-insensitive search: Use LIKE (SQLite LIKE is case-insensitive by default)
- Limit: Use LIMIT clause

CRITICAL RESTRICTIONS:
- NO INTERVAL syntax (use datetime functions instead)
- NO ILIKE (use LIKE instead)
- NO SERIAL (use AUTOINCREMENT instead)
- NO FULL OUTER JOIN (not supported)
- NO to_char, DATE_FORMAT functions

AVOID: MySQL functions (DATE_FORMAT, AUTO_INCREMENT), PostgreSQL functions (to_char, ILIKE, SERIAL)
"""
        else:  # GENERIC
            return """
GENERIC SQL SYNTAX RULES:
- Use standard SQL that works across most databases
- Avoid dialect-specific functions
- Use basic date and string functions
- Use standard JOIN syntax
- Use LIMIT for row limiting
"""

    def forward(self, input: QueryInput) -> SQLOutput:
        """Generate SQL from natural language input"""
        # Set current dialect for this request
        self.current_dialect = input.sql_dialect
        # Store the original query for validation context
        self._current_query = input.query
        
        if self.contract_result is None:
            return SQLOutput(sql="SELECT 1;")
        
        # Return the result directly
        return self.contract_result

    def __call__(self, input: QueryInput) -> SQLOutput:
        """Override call to ensure dialect is set before any processing"""
        # Set dialect before any prompt generation
        self.current_dialect = input.sql_dialect
        # Now call the parent implementation
        return super().__call__(input=input)
    
    def pre(self, input: QueryInput) -> bool:
        """Pre-condition: Check if query is valid"""
        return len(input.query.strip()) > 0
    
    def post(self, result: SQLOutput) -> bool:
        """
        Post-condition: Validate that the generated SQL is syntactically correct
        If this returns False, SymbolicAI will automatically retry the contract
        """
        # Basic syntax checks
        sql = result.sql.strip()
        if not sql:
            return False
            

            
        # Basic quote syntax checks 
        if sql.count("(") != sql.count(")"):
            return False
        if sql.count("'") % 2 != 0:  # Unbalanced single quotes
            return False
        if sql.count('"') % 2 != 0:  # Unbalanced double quotes
            return False
        
        # Dialect-specific validation - pass the original query for context
        return self._validate_dialect_syntax(sql, self.current_dialect, getattr(self, '_current_query', ''))
    
    def _validate_dialect_syntax(self, sql: str, dialect: SQLDialect, original_query: str = '') -> bool:
        """Perform dialect-specific syntax validation using LLM"""
        # Basic syntax checks first (fast)
        sql_upper = sql.upper()
        
        # Quick syntactic checks for common issues
        basic_issues = self._check_basic_dialect_issues(sql_upper, dialect)
        if basic_issues:
            return False
            
        # Advanced LLM-powered dialect validation with original query context
        return self._llm_validate_dialect(sql, dialect, original_query)
    
    def _check_basic_dialect_issues(self, sql_upper: str, dialect: SQLDialect) -> bool:
        """Fast basic checks for obvious dialect issues"""
        if dialect == SQLDialect.MYSQL:
            if " TOP " in sql_upper:  # MySQL uses LIMIT, not TOP
                return True
            if "AUTOINCREMENT" in sql_upper:  # MySQL uses AUTO_INCREMENT
                return True
        elif dialect == SQLDialect.POSTGRESQL:
            if " TOP " in sql_upper:  # PostgreSQL uses LIMIT, not TOP
                return True
            if "AUTO_INCREMENT" in sql_upper:  # PostgreSQL uses SERIAL
                return True
        elif dialect == SQLDialect.SQLITE:
            if " FULL OUTER JOIN " in sql_upper:  # SQLite doesn't support FULL OUTER JOIN
                return True
            if " TOP " in sql_upper:  # SQLite uses LIMIT, not TOP
                return True
            if " ILIKE " in sql_upper:  # SQLite doesn't have ILIKE
                return True
            if "INTERVAL" in sql_upper:  # SQLite doesn't support INTERVAL syntax at all
                return True
            if " SERIAL " in sql_upper:  # SQLite uses AUTOINCREMENT
                return True
            if "STRFTIME" in sql_upper and dialect != SQLDialect.SQLITE:  # Check for wrong dialect usage
                return True
        
        return False  # No issues found
    
    def _llm_validate_dialect(self, sql: str, dialect: SQLDialect, original_query: str = '') -> bool:
        """LLM validation: does this SQL correctly implement the query for this dialect?"""
        dialect_name = dialect.value.upper()
        
        # Include original query if available for better context
        context = f"\nOriginal request: {original_query}" if original_query else ""
        
        validation_prompt = f"""
Is this SQL query correct for {dialect_name}?{context}

SQL: {sql}
Dialect: {dialect_name}

Answer only "YES" if the SQL uses proper {dialect_name} syntax, or "NO" if it uses syntax from other databases.
"""

        try:
            # Use SymbolicAI's Expression for validation
            validator = Expression()
            response = validator(validation_prompt)
            
            # Parse the response
            if isinstance(response, str):
                return response.strip().upper().startswith("YES")
            return True  # Default to valid if we can't parse
            
        except Exception:
            # If LLM validation fails, fall back to basic validation only
            return True 