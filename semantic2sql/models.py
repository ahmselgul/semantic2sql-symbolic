"""
Data models for semantic2sql using SymbolicAI LLMDataModel
"""

from symai.models import LLMDataModel
from pydantic import Field
from enum import Enum


class SQLDialect(str, Enum):
    """Supported SQL dialects with specific syntax rules"""
    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    GENERIC = "generic"


class QueryInput(LLMDataModel):
    """Input model for natural language queries"""
    query: str = Field(description="Natural language query to convert to SQL")
    table_schema: str = Field(
        description="Table definition with column names and types",
        default=""
    )
    sql_dialect: SQLDialect = Field(
        description="Target SQL dialect for query generation (sqlite, mysql, postgresql, generic)",
        default=SQLDialect.GENERIC
    )


class SQLOutput(LLMDataModel):
    """Output model for generated SQL queries"""
    sql: str = Field(description="Generated SQL query") 