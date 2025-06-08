# Semantic2SQL-Symbolic

Natural language to SQL query generator using SymbolicAI contracts.

## Features

- Convert natural language to SQL using SymbolicAI `@contract` decorators
- Automatic database schema discovery
- Clean, composable architecture

## Installation

```bash
git clone https://github.com/ahmselgul/semantic2sql-symbolic.git
cd semantic2sql-symbolic
poetry install
```

Configure environment variables:
```bash
export NEUROSYMBOLIC_ENGINE_API_KEY="your-api-key"
export NEUROSYMBOLIC_ENGINE_MODEL="gpt-4o-mini"
export DATABASE_PATH="northwind.db"
```

Or create a `.env` file:
```bash
# Copy example and customize
cp env.example .env
```

## Quick Start

```python
import os
from dotenv import load_dotenv
from semantic2sql import SQLInterface, SQLGeneratorService

# Load environment variables from .env file
load_dotenv()

# Download sample database
# curl -o northwind.db https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db

sql_generator = SQLGeneratorService()

# Get database path from environment or use default
db_path = os.getenv("DATABASE_PATH", "northwind.db")
with SQLInterface(db_path) as db:
    # Auto-discover schema
    schema = db.get_table_schema("Customers")
    
    # Generate SQL from natural language
    sql = sql_generator.generate_sql("find customers from USA", schema)
    
    # Execute query
    results = db.execute_query(sql)
    print(f"Found {len(results)} customers")
```

## Components

- **`SQLInterface`**: Database operations with schema discovery
- **`SQLGeneratorService`**: SQL generation from natural language  
- **`BasicSQLGenerator`**: SymbolicAI contract for SQL generation

## Example Queries

Try these with the Northwind database:

```python
"find customers from Germany"
"show products under 20 dollars" 
"get orders from 1997"
"find employees in London"
```

## Development

```bash
poetry run pytest  # Run tests
```

Built with [SymbolicAI](https://github.com/ExtensityAI/symbolicai)
