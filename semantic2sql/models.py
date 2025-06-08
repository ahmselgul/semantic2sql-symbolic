"""
Data models for semantic2sql using SymbolicAI LLMDataModel
"""

from symai.models import LLMDataModel
from pydantic import Field


class QueryInput(LLMDataModel):
    """Input model for natural language queries"""
    query: str = Field(description="Natural language query to convert to SQL")
    table_schema: str = Field(
        description="Table definition with column names and types",
        default=""
    )


class SQLOutput(LLMDataModel):
    """Output model for generated SQL queries"""
    sql: str = Field(description="Generated SQL query") 