"""
Semantic2SQL: Natural language to SQL generator using SymbolicAI
"""

__version__ = "0.1.0"

from .models import QueryInput, SQLOutput
from .contracts import BasicSQLGenerator
from .database import SQLInterface
from .sql_generator import SQLGeneratorService

__all__ = [
    "QueryInput", 
    "SQLOutput", 
    "BasicSQLGenerator", 
    "SQLInterface",
    "SQLGeneratorService"
] 