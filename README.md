# Bridge2AI Standards Explorer MCP

A Model Context Protocol (MCP) server for the Bridge2AI Standards Explorer that provides tools to search and query standards data from the Synapse platform using SQL.

## Overview

This MCP server provides programmatic access to the Bridge2AI Standards Explorer table (`syn63096833`) on Synapse, enabling LLM applications to query and retrieve standards information through the Synapse Table Query API. The server uses FastMCP and implements Synapse's async query pattern with automatic polling.

## Features

- **SQL-Based Table Queries**: Execute SQL queries directly against the Bridge2AI Standards Explorer tables
- **Text Search**: Convenient search tool for finding text across multiple columns
- **Async Job Handling**: Automatically handles Synapse's async query pattern with polling
- **Pagination Support**: Control the number of results and offset for paginated queries
- **Table Information**: Get metadata about the Bridge2AI Standards Explorer tables and project

## Tools

### `query_table`

Execute SQL queries directly against the Bridge2AI Standards Explorer tables.

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
-- Simple query
SELECT * FROM syn63096833 LIMIT 10

-- Search for FHIR standards
SELECT * FROM syn63096833 WHERE Standard LIKE '%FHIR%'

-- Search across multiple columns
SELECT id, Standard, ShortDescription 
FROM syn63096833 
WHERE ShortDescription LIKE '%metadata%' 
LIMIT 5

-- Complex filtering with pagination
SELECT id, Standard, Category 
FROM syn63096833 
WHERE Standard LIKE '%format%' 
  AND Category IS NOT NULL
LIMIT 10 OFFSET 5
```

### `search_standards`

Search for text within the Bridge2AI Standards Explorer table (convenience wrapper around `query_table`).

**Parameters:**
- `search_text` (str, required): The text to search for (case-insensitive)
- `columns_to_search` (list[str], optional): List of column names to search (default: `["Standard", "ShortDescription"]`)
- `max_results` (int, optional): Maximum number of results to return (default: 10)
- `offset` (int, optional): Number of results to skip for pagination (default: 0)

**Returns:** Same format as `query_table`, plus:
- `search_text`: The original search text
- `searched_columns`: List of columns that were searched

**Example:**
```python
# Search in default columns (Standard, ShortDescription)
result = await client.call_tool(
    "search_standards",
    {"search_text": "FHIR", "max_results": 5}
)

# Search in custom columns
result = await client.call_tool(
    "search_standards",
    {
        "search_text": "metadata",
        "columns_to_search": ["ShortDescription", "LongDescription"],
        "max_results": 10
    }
)
```

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

### Development Installation

For development with testing dependencies:

```bash
uv pip install -e ".[dev]"
```

## Configuration

The server is configured to query:
- **Table ID**: `syn63096833` (Bridge2AI Standards Explorer Table)
- **Project ID**: `syn63096806` (Bridge2AI Standards Explorer Project)
- **Base URL**: `https://repo-prod.prod.sagebase.org`
- **Authentication**: Optional via `SYNAPSE_AUTH_TOKEN` environment variable (see below)

### Authentication (Optional)

This MCP accesses public Synapse tables only, so no authentication should be necessary. If you still need it for some reason, do the following.

For authenticated access, set the `SYNAPSE_AUTH_TOKEN` environment variable:

```bash
export SYNAPSE_AUTH_TOKEN="your_synapse_personal_access_token"
```

To get a Synapse Personal Access Token:
1. Log in to [Synapse](https://www.synapse.org/)
2. Go to Account Settings → Personal Access Tokens
3. Create a new token with appropriate scopes (at minimum: view, download)

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

The server communicates via stdio using the MCP protocol and will wait for messages from an MCP client.

### Using with an MCP Client

Example using the FastMCP client:

```python
from fastmcp import Client

async with Client("standards-explorer-mcp") as client:
    # Execute a SQL query
    results = await client.call_tool(
        name="query_table",
        arguments={"sql_query": "SELECT * FROM syn63096833 WHERE Standard LIKE '%FHIR%' LIMIT 5"}
    )
    print(results.data)
    
    # Search for text across columns
    results = await client.call_tool(
        name="search_standards",
        arguments={"search_text": "metadata", "max_results": 5}
    )
    print(results.data)
    
    # Get table information
    info = await client.call_tool(name="get_standards_table_info")
    print(info.data)
```

### Example Client

A complete example client is available in `tests/example_client.py`:

```bash
uv run python tests/example_client.py
```

## Testing

### Run All Tests

```bash
# Run complete test suite
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=src/standards_explorer_mcp --cov-report=html
```

**Note:** Integration tests use FastMCP's in-memory transport, automatically starting and stopping the server - no manual server startup required!

## Architecture

### Implementation Approach

The server uses **Synapse's Table Query API** which provides table-specific SQL query capabilities:

**Async Job Pattern:**
1. POST to `/entity/{id}/table/query/async/start` → returns `asyncToken`
2. Poll GET to `/entity/{id}/table/query/async/get/{asyncToken}`
   - Returns 202 ACCEPTED while processing
   - Returns 200 OK with results when complete
3. Automatic retry with 1-second intervals
4. Configurable timeout (default 30 seconds)

**Benefits:**
- ✅ Table-specific queries (results only from syn63096833)
- ✅ Full SQL WHERE clause support
- ✅ LIKE operator for substring matching
- ✅ Flexible column selection
- ✅ Built-in pagination with LIMIT/OFFSET
- ✅ No cross-contamination from other Synapse entities

### Code Structure

The implementation separates business logic from MCP decorators for testability:

```python
# Implementation function (testable)
async def query_table_impl(sql_query: str, max_wait_seconds: int = 30) -> dict:
    # Business logic here
    ...

# MCP Wrapper (thin layer)
@mcp.tool
async def query_table(sql_query: str, max_wait_seconds: int = 30) -> dict:
    return await query_table_impl(sql_query, max_wait_seconds)
```

This design allows:
- Direct testing of business logic without mocking MCP framework
- Fast test execution
- Easy debugging
- Clear separation of concerns

## Development

### Project Structure

```
standards-explorer-mcp/
├── src/
│   └── standards_explorer_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       └── main.py          # Main server implementation
├── tests/
│   ├── conftest.py          # Shared test fixtures
│   ├── test_api_endpoints.py    # API layer tests
│   ├── test_tools.py            # Business logic tests
│   ├── test_mcp_integration.py  # Integration tests
│   └── example_client.py        # Example usage
├── pyproject.toml           # Project configuration
└── README.md
```

### Dependencies

- `fastmcp>=2.12.5` - MCP server framework
- `httpx>=0.27.0` - Async HTTP client for API calls
- `pytest>=8.0.0` - Testing framework (dev)
- `pytest-asyncio>=0.23.0` - Async test support (dev)

## Resources

- [Synapse REST API Documentation](https://rest-docs.synapse.org/rest/index.html)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Bridge2AI Standards Explorer on Synapse](https://www.synapse.org/#!Synapse:syn63096806)
- [Bridge2AI Standards Explorer Table](https://www.synapse.org/#!Synapse:syn63096833)

## Troubleshooting

### Server won't start
Make sure dependencies are installed:
```bash
uv pip install -e .
```

### Query fails
- Check internet connectivity to `repo-prod.prod.sagebase.org`
- Verify SQL syntax is correct
- For private tables, ensure `SYNAPSE_AUTH_TOKEN` is set

### Tests fail
- Ensure you have the dev dependencies: `uv pip install -e ".[dev]"`
- Check that you have network access to Synapse API
- Some tests may require authentication for full functionality

### Authentication issues
- Verify your token is valid and hasn't expired
- Ensure the token has appropriate scopes (view, download)
- Check that the environment variable is exported correctly

## Support

For questions about:
- **FastMCP**: https://discord.gg/uu8dJCgttd or https://github.com/jlowin/fastmcp
- **Synapse API**: https://help.synapse.org/
- **MCP Protocol**: https://github.com/modelcontextprotocol
