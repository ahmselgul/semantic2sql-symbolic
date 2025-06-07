from symai import Symbol, Expression
from symai.models import LLMDataModel
from symai.strategy import contract
from pydantic import Field



class QueryInput(LLMDataModel):
    query: str = Field(description="Natural language query to convert to SQL")


class SQLOutput(LLMDataModel):
    sql: str = Field(description="Generated SQL query")


@contract(
    pre_remedy=False,
    post_remedy=True,
    verbose=True
)
class BasicSQLGenerator(Expression):
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
        # Check basic SQL validity
        return sql.endswith(';')
    
    @property
    def prompt(self) -> str:
        return (
            "You are an expert SQL generator. Convert natural language queries to valid SQL statements. "
            "Rules:\n"
            "1. Use standard SQL syntax\n" 
            "2. Always end with semicolon\n"
            "3. Return only the SQL statement, no explanation\n"
        )


if __name__ == "__main__":
    generator = BasicSQLGenerator()
    
    test_queries = [
        "show me all active users",
        "get the top 5 customers by order rating",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        test_input = QueryInput(query=query)
        result = generator(input=test_input)
        print(f"SQL result:   {result.sql}")
    
