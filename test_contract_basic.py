from symai.strategy import contract
from symai.core import Expression
from symai.models import LLMDataModel
from pydantic import Field



class QueryInput(LLMDataModel):
    query: str = Field(description="Natural language query to convert to SQL")


class SQLOutput(LLMDataModel):
    sql: str = Field(description="Generated SQL query")


@contract()
class BasicSQLGenerator(Expression):
    def __init__(self):
        super().__init__()
    
    def forward(self, input: QueryInput) -> SQLOutput:
        """Generate SQL from natural language query"""
        return SQLOutput(sql=f"SELECT * FROM table WHERE condition = '{input.query}';")
    
    def pre(self, input: QueryInput) -> bool:
        """Pre-condition: Check if query is valid"""
        return len(input.query.strip()) > 0
    
    def post(self, result: SQLOutput) -> bool:
        """Post-condition: Check if SQL is valid"""
        return result.sql.strip().upper().startswith('SELECT')


if __name__ == "__main__":
    generator = BasicSQLGenerator()
    
    test_input = QueryInput(query="show me all active customers")
    result = generator(input=test_input)
    
    print("Input:", test_input.query)
    print("Output:", result.sql)