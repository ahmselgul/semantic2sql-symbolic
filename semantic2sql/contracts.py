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
class BasicSQLGenerator(Expression):
    """Basic SQL generator using SymbolicAI @contract"""
    
    def __init__(self):
        super().__init__()
    
    def forward(self, input: QueryInput) -> SQLOutput:
        """Generate SQL from natural language query using LLM"""
        if self.contract_result is None:
            return SQLOutput(sql="SELECT example;")
        return self.contract_result
    
    def pre(self, input: QueryInput) -> bool:
        """Pre-condition: Check if query is valid"""
        return len(input.query.strip()) > 0
    
    def post(self, result: SQLOutput) -> bool:
        """Post-condition: Check if SQL is valid"""
        sql = result.sql.strip().upper()
        return sql.endswith(';')
    
    @property
    def prompt(self) -> str:
        return (
            "You are an expert SQL generator. Convert natural language queries to valid SQL statements using the provided table schema. "
            "Rules:\n"
            "1. Use standard SQL syntax\n" 
            "2. Always end with semicolon\n"
            "3. Use actual table and column names from the provided table schema\n"
            "4. If no table schema is provided, use generic table/column names\n"
            "5. Return only the SQL statement, no explanation\n"
        ) 