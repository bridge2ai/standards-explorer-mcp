# Bridge2AI Standards Explorer MCP

A Model Context Protocol (MCP) server for the Bridge2AI Standards Explorer that provides tools to search and explore standards data from the Synapse platform.

## Overview

This MCP server provides access to the Bridge2AI Standards Explorer table (`syn63096833`) which is part of the Bridge2AI Standards Explorer project (`syn63096806`) on Synapse. It enables LLM applications to search and retrieve standards information through the Synapse REST API.

## Features

- **Search Standards**: Query Synapse entities using free-text search across all public content
- **No Authentication Required**: The search endpoint doesn't require Synapse authentication for public data
- **Pagination Support**: Control the number of results and offset for paginated queries
- **Table Information**: Get metadata about the Bridge2AI Standards Explorer table and project

**Note**: The Synapse Search API searches across all public entities in Synapse. While this MCP server is configured with the Bridge2AI Standards Explorer table (`syn63096833`) and project (`syn63096806`) IDs, the search results may include entities from other projects. You can filter results by checking the returned entity IDs against the configured table/project IDs.

## Tools

### `search_standards`

Search for standards from the Bridge2AI Standards Explorer table.

**Parameters:**
- `query` (str, required): The search query string to find standards
- `max_results` (int, optional): Maximum number of results to return (default: 10)
- `offset` (int, optional): Number of results to skip for pagination (default: 0)

**Returns:** A dictionary containing:
- `success`: Boolean indicating if the search was successful
- `query`: The original search query
- `total_results`: Total number of matching results found
- `returned_results`: Number of results in this response
- `hits`: Array of matching standards with their metadata
- `facets`: Available facets for filtering

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
# Using the CLI entry point
standards-explorer-mcp

# Or using Python module
python -m standards_explorer_mcp
```

### Using with an MCP Client

```python
from fastmcp import Client

async with Client("standards-explorer-mcp") as client:
    # Search for standards
    results = await client.call_tool(
        name="search_standards",
        arguments={"query": "FHIR", "max_results": 5}
    )
    print(results)
    
    # Get table information
    info = await client.call_tool(name="get_standards_table_info")
    print(info)
```

## Configuration

The server is configured to query:
- **Table ID**: `syn63096833`
- **Project ID**: `syn63096806`
- **Base URL**: `https://repo-prod.prod.sagebase.org`

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
