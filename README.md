# Bridge2AI Standards Explorer MCP

A Model Context Protocol (MCP) server for the Bridge2AI Standards Explorer that provides tools to search and query standards data from the Synapse platform using SQL.

## Overview

This MCP server provides access to the Bridge2AI Standards Explorer table (`syn63096833`) which is part of the Bridge2AI Standards Explorer project (`syn63096806`) on Synapse. It enables LLM applications to query and retrieve standards information through the Synapse Table Query API.

## Features

- **SQL-Based Table Queries**: Execute SQL queries directly against the Bridge2AI Standards Explorer table
- **Text Search**: Convenient search tool for finding text across multiple columns
- **Async Job Handling**: Automatically handles Synapse's async query pattern with polling
- **Pagination Support**: Control the number of results and offset for paginated queries
- **Table Information**: Get metadata about the Bridge2AI Standards Explorer table and project
- **Optional Authentication**: Public tables may work without authentication; set `SYNAPSE_AUTH_TOKEN` environment variable for authenticated access

## Tools

### `query_table`

Execute SQL queries directly against the Bridge2AI Standards Explorer table.

**Parameters:**
- `sql_query` (str, required): SQL query string to execute (e.g., `"SELECT * FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 10"`)
- `max_wait_seconds` (int, optional): Maximum time to wait for query results (default: 30)

**Returns:** A dictionary containing:
- `success`: Boolean indicating if the query was successful
- `sql_query`: The executed SQL query
- `row_count`: Number of rows returned
- `total_rows`: Total number of matching rows
- `columns`: Array of column definitions with names and types
- `rows`: Array of result rows with their data

**Example queries:**
```sql
SELECT * FROM syn63096833 LIMIT 10
SELECT * FROM syn63096833 WHERE name LIKE '%FHIR%'
SELECT id, name, description FROM syn63096833 WHERE description LIKE '%metadata%' LIMIT 5
```

### `search_standards`

Search for text within the Bridge2AI Standards Explorer table (convenience wrapper around `query_table`).

**Parameters:**
- `search_text` (str, required): The text to search for (case-insensitive)
- `columns_to_search` (list[str], optional): List of column names to search (default: `["name", "description"]`)
- `max_results` (int, optional): Maximum number of results to return (default: 10)
- `offset` (int, optional): Number of results to skip for pagination (default: 0)

**Returns:** Same format as `query_table`, plus:
- `search_text`: The original search text
- `searched_columns`: List of columns that were searched

### `get_standards_table_info`

Get information about the Bridge2AI Standards Explorer table.

**Returns:** Dictionary with table and project information including:
- `table_id`: Synapse ID of the table
- `project_id`: Synapse ID of the project
- URLs to view the table and project on Synapse

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Usage

### Running the Server

```bash
# Using uv (recommended)
uv run standards-explorer-mcp

# Or using the CLI entry point directly
standards-explorer-mcp

# Or using Python module
python -m standards_explorer_mcp
```

### Authentication (Optional)

For authenticated access, set the `SYNAPSE_AUTH_TOKEN` environment variable:

```bash
export SYNAPSE_AUTH_TOKEN="your_synapse_personal_access_token"
```

To get a Synapse Personal Access Token:
1. Log in to [Synapse](https://www.synapse.org/)
2. Go to Account Settings → Personal Access Tokens
3. Create a new token with appropriate scopes (at minimum: view, download)

Public tables may work without authentication.

### Using with an MCP Client

```python
from fastmcp import Client

async with Client("standards-explorer-mcp") as client:
    # Execute a SQL query
    results = await client.call_tool(
        name="query_table",
        arguments={"sql_query": "SELECT * FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 5"}
    )
    print(results)
    
    # Search for text across columns
    results = await client.call_tool(
        name="search_standards",
        arguments={"search_text": "metadata", "max_results": 5}
    )
    print(results)
    
    # Get table information
    info = await client.call_tool(name="get_standards_table_info")
    print(info)
```

### Testing

Test the implementation directly:

```bash
# Test table queries
uv run test_table_query.py

# With authentication
SYNAPSE_AUTH_TOKEN="your_token" uv run test_table_query.py
```

## Configuration

The server is configured to query:
- **Table ID**: `syn63096833`
- **Project ID**: `syn63096806`
- **Base URL**: `https://repo-prod.prod.sagebase.org`
- **Authentication**: Optional via `SYNAPSE_AUTH_TOKEN` environment variable

## Resources

- [Synapse REST API Documentation](https://rest-docs.synapse.org/rest/index.html)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Bridge2AI Standards Explorer on Synapse](https://www.synapse.org/#!Synapse:syn63096806)

## Development

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```
