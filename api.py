"""
Simple FastAPI for semantic2sql-symbolic demonstration
Showcases natural language to SQL conversion capabilities
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import os

from semantic2sql import SemanticSQLGenerator, QueryInput, SQLDialect, SQLInterface

app = FastAPI(
    title="Semantic2SQL Demo",
    description="Convert natural language to SQL using SymbolicAI",
    version="1.0.0"
)

# Simple request/response models
class SQLRequest(BaseModel):
    query: str
    table_schema: Optional[str] = ""
    sql_dialect: Optional[str] = "generic"

class DatabaseQueryRequest(BaseModel):
    query: str
    table_name: str
    execute: Optional[bool] = True

# Store uploaded databases
databases = {}

@app.get("/", response_class=HTMLResponse)
async def demo_interface():
    """Simple demo interface"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Semantic2SQL Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .section { background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 8px; }
            textarea, input, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .result { background: #e9ecef; padding: 15px; border-radius: 4px; margin: 10px 0; font-family: monospace; }
            .error { background: #f8d7da; color: #721c24; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>🤖 Semantic2SQL Demo</h1>
        <p>Convert natural language to SQL using SymbolicAI @contract decorators</p>
        
        <div class="section">
            <h3>📁 Upload Database & Query</h3>
            <input type="file" id="dbFile" accept=".db" />
            <button onclick="uploadDB()">Upload Database</button>
            
            <div id="dbSection" style="display:none;">
                <textarea id="dbQuery" placeholder="e.g., find customers from USA" rows="2"></textarea>
                <select id="tableSelect"></select>
                <button onclick="queryDB()">Generate & Execute SQL</button>
            </div>
        </div>

        <div class="section">
            <h3>✏️ Manual Query</h3>
            <textarea id="manualQuery" placeholder="e.g., find all active users" rows="2"></textarea>
            <textarea id="schema" placeholder="Table: users\nColumns: id (INT), name (VARCHAR), active (BOOLEAN)" rows="3"></textarea>
            <select id="dialect">
                <option value="generic">Generic SQL</option>
                <option value="mysql">MySQL</option>
                <option value="postgresql">PostgreSQL</option>
                <option value="sqlite">SQLite</option>
            </select>
            <button onclick="generateSQL()">Generate SQL</button>
        </div>

        <div id="result" style="display:none;"></div>

        <script>
            let currentDB = null;

            async function uploadDB() {
                const file = document.getElementById('dbFile').files[0];
                if (!file) return alert('Please select a database file');

                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/upload-db', { method: 'POST', body: formData });
                    const data = await response.json();
                    
                    if (data.success) {
                        currentDB = data.database_id;
                        const tableSelect = document.getElementById('tableSelect');
                        tableSelect.innerHTML = data.tables.map(t => `<option value="${t}">${t}</option>`).join('');
                        document.getElementById('dbSection').style.display = 'block';
                        showResult(`Database uploaded! Tables: ${data.tables.join(', ')}`);
                    } else {
                        showResult(data.error, true);
                    }
                } catch (error) {
                    showResult('Upload failed: ' + error.message, true);
                }
            }

            async function queryDB() {
                if (!currentDB) return alert('Please upload a database first');
                
                const query = document.getElementById('dbQuery').value;
                const table = document.getElementById('tableSelect').value;
                
                try {
                    const response = await fetch(`/query-db/${currentDB}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, table_name: table, execute: true })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        let html = `<strong>Generated SQL:</strong><br><code>${data.sql}</code>`;
                        if (data.results && data.results.length > 0) {
                            html += '<br><br><strong>Results:</strong>';
                            html += '<table><thead><tr>' + Object.keys(data.results[0]).map(k => `<th>${k}</th>`).join('') + '</tr></thead><tbody>';
                            data.results.forEach(row => {
                                html += '<tr>' + Object.values(row).map(v => `<td>${v || 'NULL'}</td>`).join('') + '</tr>';
                            });
                            html += '</tbody></table>';
                        }
                        showResult(html);
                    } else {
                        showResult(data.error, true);
                    }
                } catch (error) {
                    showResult('Query failed: ' + error.message, true);
                }
            }

            async function generateSQL() {
                const query = document.getElementById('manualQuery').value;
                const schema = document.getElementById('schema').value;
                const dialect = document.getElementById('dialect').value;
                
                if (!query.trim()) return alert('Please enter a query');
                
                try {
                    const response = await fetch('/generate-sql', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, table_schema: schema, sql_dialect: dialect })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        showResult(`<strong>Generated SQL (${dialect}):</strong><br><code>${data.sql}</code>`);
                    } else {
                        showResult(data.error, true);
                    }
                } catch (error) {
                    showResult('Generation failed: ' + error.message, true);
                }
            }

            function showResult(content, isError = false) {
                const result = document.getElementById('result');
                result.className = isError ? 'result error' : 'result';
                result.innerHTML = content;
                result.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """)

@app.post("/generate-sql")
async def generate_sql(request: SQLRequest):
    """Generate SQL from natural language"""
    try:
        query_input = QueryInput(
            query=request.query,
            table_schema=request.table_schema,
            sql_dialect=SQLDialect(request.sql_dialect)
        )
        
        generator = SemanticSQLGenerator()
        result = generator(input=query_input)
        
        return {"sql": result.sql, "success": True}
    except Exception as e:
        return {"sql": "", "success": False, "error": str(e)}

@app.post("/upload-db")
async def upload_database(file: UploadFile = File(...)):
    """Upload database and extract schema"""
    if not file.filename.endswith('.db'):
        raise HTTPException(status_code=400, detail="Only .db files supported")
    
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Extract schema using our existing SQLInterface
        with SQLInterface(temp_path) as db:
            tables = db.get_table_names()
            schema_info = {table: db.get_table_schema(table) for table in tables}
        
        # Store database
        db_id = file.filename.replace('.db', '')
        databases[db_id] = {"path": temp_path, "tables": tables, "schema_info": schema_info}
        
        return {"success": True, "database_id": db_id, "tables": tables}
    except Exception as e:
        if 'temp_path' in locals():
            os.unlink(temp_path)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query-db/{db_id}")
async def query_database(db_id: str, request: DatabaseQueryRequest):
    """Query uploaded database"""
    if db_id not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    try:
        db_info = databases[db_id]
        
        if request.table_name not in db_info["tables"]:
            raise HTTPException(status_code=400, detail=f"Table not found. Available: {db_info['tables']}")
        
        # Generate SQL using our existing contract
        table_schema = db_info["schema_info"][request.table_name]
        query_input = QueryInput(
            query=request.query,
            table_schema=table_schema,
            sql_dialect=SQLDialect.SQLITE
        )
        
        generator = SemanticSQLGenerator()
        result = generator(input=query_input)
        
        response_data = {"sql": result.sql, "success": True}
        
        # Execute if requested using our existing SQLInterface
        if request.execute:
            with SQLInterface(db_info["path"]) as db:
                safe_sql = result.sql.replace(request.table_name, f'"{request.table_name}"')
                results = db.execute_query(safe_sql)
                response_data["results"] = results[:10]  # Limit to 10 rows
        
        return response_data
        
    except Exception as e:
        return {"sql": "", "success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting Semantic2SQL Demo")
    print("Open http://localhost:8000 for demo interface")
    uvicorn.run(app, host="0.0.0.0", port=8000) 