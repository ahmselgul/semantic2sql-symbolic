# Semantic2SQL-Symbolic

Natural language to SQL query generator using SymbolicAI contracts with multi-dialect support.

## Features

- Convert natural language to SQL using SymbolicAI `@contract` decorators
- Multi-dialect SQL support (MySQL, PostgreSQL, SQLite, Generic)
- Enhanced prompts with dialect-specific syntax rules
- Contract-based validation for reliable SQL generation

## Installation

### Create a virtual environment

```bash
git clone https://github.com/ahmselgul/semantic2sql-symbolic.git
cd semantic2sql-symbolic
python -m venv .venv  # Create virtual environment
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### Option 1: Using Poetry (Recommended)


```bash
poetry install  # Creates virtual environment automatically and installs dependencies
```

### Option 2: Using pip

With pip, you need to manually create and activate a virtual environment.

```bash
pip install -r requirements.txt  # Install dependencies
```

### SymbolicAI Configuration

After installation, SymbolicAI will automatically create a configuration file. You need to configure your OpenAI API or other LLM-Engine key:

1. **Run any import to generate the config file:**
```bash
poetry run python -c "from semantic2sql import SemanticSQLGenerator"
```
or if no poetry installed
```bash
python -c "from semantic2sql import SemanticSQLGenerator"
```
2. **Configure your LLM API key in the config file:**
   - Edit `.venv/.symai/symai.config.json` (you can use nano: `nano .venv/.symai/symai.config.json`)
   - Set your `NEUROSYMBOLIC_ENGINE_API_KEY` with your LLM API key
   - Set `NEUROSYMBOLIC_ENGINE_MODEL` to `"gpt-4o-mini"` (or your preferred model)

**Edit with nano:**
```bash
nano .venv/.symai/symai.config.json
```

**Example configuration:**
```json
{
    "NEUROSYMBOLIC_ENGINE_API_KEY": "sk-your-actual-api-key-here",
    "NEUROSYMBOLIC_ENGINE_MODEL": "gpt-4o-mini",
    ...
}
```


For database path create a `.env` file:
```bash
# Copy example and customize
cp env.example .env
```

## Quick Start

### Python API

```python
from semantic2sql.contracts import SemanticSQLGenerator
from semantic2sql.models import QueryInput, SQLDialect

# Initialize the generator
generator = SemanticSQLGenerator()

# Define your table schema
schema = """
Table: customers
Columns: id (INT), name (VARCHAR), country (VARCHAR), created_at (TIMESTAMP)
"""

# Generate SQL for different dialects
input_data = QueryInput(
    query="find customers from USA created in the last 30 days",
    table_schema=schema,
    sql_dialect=SQLDialect.MYSQL
)

result = generator(input=input_data)
print(f"Generated SQL: {result.sql}")
```

### Web Demo API

For easy testing and demonstration, run the FastAPI server:

```bash
poetry run python api.py
```

Then open http://localhost:8000 in your browser for an interactive demo where you can:

- **Upload SQLite databases** - Drop any `.db` file to extract schema automatically
- **Natural language queries** - Query databases with plain English
- **Multi-dialect support** - Test MySQL, PostgreSQL, SQLite, and Generic SQL
- **Live execution** - See both generated SQL and actual results

**API Endpoints:**
- `POST /generate-sql` - Generate SQL from natural language and schema
- `POST /upload-db` - Upload a SQLite database file  
- `POST /query-db/{db_id}` - Query an uploaded database with natural language

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/generate-sql" \
     -H "Content-Type: application/json" \
     -d '{"query": "find customers from USA", "sql_dialect": "mysql"}'
```

## Supported SQL Dialects

- **MySQL**: `DATE_FORMAT()`, `AUTO_INCREMENT`, `INTERVAL` syntax
- **PostgreSQL**: `to_char()`, `SERIAL`, `ILIKE`, `INTERVAL '30 days'`
- **SQLite**: `strftime()`, `AUTOINCREMENT`, `datetime()` functions
- **Generic**: Standard SQL compatible across databases

## Architecture

The system uses a clean, minimal architecture:

- **`QueryInput`**: Input model with query, schema, and dialect
- **`SQLOutput`**: Output model containing just the generated SQL
- **`SemanticSQLGenerator`**: SymbolicAI contract with enhanced prompts and validation

## Example Queries

Try these with different dialects:

```python
# String functions (shows LIKE vs ILIKE differences)
"find customers with names containing 'john'"

# Date functions (shows dialect-specific date handling)
"show orders from the last 30 days"

# Auto-increment (shows different syntax)
"create a users table with auto-increment ID"
```

## Examples

Run the included examples:

```bash
# Basic usage with different dialects
python examples/basic_usage.py

# Database integration with Northwind database
python examples/database_usage.py
```

For the database example, download the Northwind database:
```bash
curl -o northwind.db https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db
```

## Development

```bash
poetry run pytest  # Run tests
poetry run pytest tests/test_dialect_performance.py -v  # Test dialect differences
```

## Testing

The project includes comprehensive tests:

- **Model tests**: Input/output validation
- **Contract tests**: SQL generation functionality  
- **Dialect performance tests**: Verify dialect-specific behavior

Built with [SymbolicAI](https://github.com/ExtensityAI/symbolicai)
